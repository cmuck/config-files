#!/usr/bin/env python3
"""
Sync MCP server definitions between the Copilot CLI config
(~/.copilot/mcp-config.json, "mcpServers" schema) and the VS Code
global MCP config (~/.config/Code/User/mcp.json, "servers" schema).

Behavior:
- Additive only: never overwrites an existing server definition or
  deletes a server. It only adds servers that exist in one file but
  not the other, converting between the two schemas.
- Secrets: when converting CLI -> VS Code, env/header values whose key
  looks like a secret (TOKEN, SECRET, PASSWORD, KEY, PAT) become
  "${input:<id>}" references with a matching "promptString" input
  (password: true) instead of being copied as plaintext.
- Secrets: when converting VS Code -> CLI, "${input:...}" references
  are replaced with "" (empty string) placeholders, since the CLI
  format has no input-prompt mechanism; you must fill them manually.
- Both files are backed up (<file>.bak.<timestamp>) before being
  rewritten. Nothing is written if there is nothing to sync.

Usage: sync-mcp.py [--dry-run]
"""

import json
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Any

CLI_CONFIG = Path.home() / ".copilot" / "mcp-config.json"
VSCODE_CONFIG = Path.home() / ".config" / "Code" / "User" / "mcp.json"

SECRET_HINTS = ("TOKEN", "SECRET", "PASSWORD", "PASS", "KEY", "PAT", "APIKEY")


def load_jsonc(path: Path) -> dict[str, Any]:
    """Load JSON that may contain trailing commas (VS Code's jsonc)."""
    text = path.read_text()
    # strip // line comments (not inside strings) - simple heuristic ok for these files
    text_no_comments = re.sub(
        r'(?m)^(?:[^"\n]|"(?:\\.|[^"\\])*")*?(//.*)$',
        lambda m: m.group(0)[: m.start(1) - m.start(0)] if m.group(1) else m.group(0),
        text,
    )
    # remove trailing commas before } or ]
    cleaned = re.sub(r",(\s*[}\]])", r"\1", text_no_comments)
    return json.loads(cleaned)


def is_secret_key(key: str) -> bool:
    up = key.upper()
    return any(hint in up for hint in SECRET_HINTS)


def is_http(cfg: dict[str, Any]) -> bool:
    return cfg.get("type") == "http"


def externalize_secrets(
    name: str, values: dict[str, Any]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Replace secret values by "${input:<id>}" references.
    Returns (new_values, list_of_input_defs)."""
    out: dict[str, Any] = {}
    inputs: list[dict[str, Any]] = []
    for key, value in values.items():
        if is_secret_key(key) and value not in ("", None):
            input_id = f"{name}-{key.lower()}"
            out[key] = f"${{input:{input_id}}}"
            inputs.append(
                {
                    "id": input_id,
                    "type": "promptString",
                    "description": f"{key} for {name}",
                    "password": True,
                }
            )
        else:
            out[key] = value
    return out, inputs


def blank_input_references(values: dict[str, Any]) -> dict[str, Any]:
    """Replace "${input:...}" references by empty placeholders."""
    return {
        key: "" if isinstance(value, str) and value.startswith("${input:") else value
        for key, value in values.items()
    }


def cli_to_vscode_server(
    name: str, cfg: dict[str, Any]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Convert a mcpServers-style entry to a VS Code servers-style entry.
    Returns (server_dict, list_of_input_defs)."""
    out: dict[str, Any] = {}
    inputs: list[dict[str, Any]] = []

    if is_http(cfg):
        out["type"] = "http"
        out["url"] = cfg["url"]
        secret_section = "headers"
    else:
        # stdio (or default)
        for key in ("command", "args"):
            if key in cfg:
                out[key] = cfg[key]
        secret_section = "env"

    if secret_section in cfg:
        out[secret_section], inputs = externalize_secrets(name, cfg[secret_section])
    return out, inputs


def vscode_to_cli_server(cfg: dict[str, Any]) -> dict[str, Any]:
    """Convert a VS Code servers-style entry to a mcpServers-style entry."""
    out: dict[str, Any] = {"tools": ["*"]}

    if is_http(cfg):
        out["type"] = "http"
        out["url"] = cfg["url"]
        blank_section = "headers"
    else:
        out["type"] = "stdio"
        for key in ("command", "args"):
            if key in cfg:
                out[key] = cfg[key]
        blank_section = "env"

    if blank_section in cfg:
        out[blank_section] = blank_input_references(cfg[blank_section])
    return out


def backup(path: Path) -> Path | None:
    if path.exists():
        ts = time.strftime("%Y%m%d-%H%M%S")
        bak = path.with_suffix(path.suffix + f".bak.{ts}")
        shutil.copy2(path, bak)
        return bak
    return None


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    cli_data = load_jsonc(CLI_CONFIG) if CLI_CONFIG.exists() else {"mcpServers": {}}
    vsc_data = (
        load_jsonc(VSCODE_CONFIG)
        if VSCODE_CONFIG.exists()
        else {"servers": {}, "inputs": []}
    )

    cli_servers = cli_data.setdefault("mcpServers", {})
    vsc_servers = vsc_data.setdefault("servers", {})
    vsc_inputs = vsc_data.setdefault("inputs", [])
    vsc_input_ids = {i["id"] for i in vsc_inputs}

    added_to_vsc = []
    added_to_cli = []

    # CLI -> VS Code (add servers missing in VS Code)
    for name, cfg in cli_servers.items():
        if name not in vsc_servers:
            new_cfg, new_inputs = cli_to_vscode_server(name, cfg)
            vsc_servers[name] = new_cfg
            for inp in new_inputs:
                if inp["id"] not in vsc_input_ids:
                    vsc_inputs.append(inp)
                    vsc_input_ids.add(inp["id"])
            added_to_vsc.append(name)

    # VS Code -> CLI (add servers missing in CLI)
    for name, cfg in vsc_servers.items():
        if name not in cli_servers and name not in added_to_vsc:
            cli_servers[name] = vscode_to_cli_server(cfg)
            added_to_cli.append(name)

    if not added_to_vsc and not added_to_cli:
        print("Already in sync. Nothing to do.")
        return

    print("Servers to add to VS Code config:", added_to_vsc or "none")
    print("Servers to add to CLI config:     ", added_to_cli or "none")

    if dry_run:
        print("\n--dry-run: no files written.")
        return

    if added_to_cli:
        bak = backup(CLI_CONFIG)
        CLI_CONFIG.write_text(json.dumps(cli_data, indent=2) + "\n")
        print(f"Updated {CLI_CONFIG} (backup: {bak})")

    if added_to_vsc:
        bak = backup(VSCODE_CONFIG)
        VSCODE_CONFIG.write_text(json.dumps(vsc_data, indent=2) + "\n")
        print(f"Updated {VSCODE_CONFIG} (backup: {bak})")

    print("\nNOTE: For servers newly added to the CLI config, secret values")
    print('were set to "" placeholders - edit ~/.copilot/mcp-config.json')
    print("to fill in real tokens.")


if __name__ == "__main__":
    main()
