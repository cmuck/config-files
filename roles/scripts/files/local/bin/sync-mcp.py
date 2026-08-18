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
import sys
import shutil
import time
from pathlib import Path

CLI_CONFIG = Path.home() / ".copilot" / "mcp-config.json"
VSCODE_CONFIG = Path.home() / ".config" / "Code" / "User" / "mcp.json"

SECRET_HINTS = ("TOKEN", "SECRET", "PASSWORD", "PASS", "KEY", "PAT", "APIKEY")


def load_jsonc(path: Path):
    """Load JSON that may contain trailing commas (VS Code's jsonc)."""
    text = path.read_text()
    # strip // line comments (not inside strings) - simple heuristic ok for these files
    text_no_comments = re.sub(r'(?m)^(?:[^"\n]|"(?:\\.|[^"\\])*")*?(//.*)$',
                               lambda m: m.group(0)[:m.start(1) - m.start(0)] if m.group(1) else m.group(0),
                               text)
    # remove trailing commas before } or ]
    cleaned = re.sub(r',(\s*[}\]])', r'\1', text_no_comments)
    return json.loads(cleaned)


def is_secret_key(key: str) -> bool:
    up = key.upper()
    return any(hint in up for hint in SECRET_HINTS)


def cli_to_vscode_server(name, cfg):
    """Convert a mcpServers-style entry to a VS Code servers-style entry.
    Returns (server_dict, list_of_input_defs)."""
    out = {}
    inputs = []

    if cfg.get("type") == "http":
        out["type"] = "http"
        out["url"] = cfg["url"]
        if "headers" in cfg:
            headers = {}
            for k, v in cfg["headers"].items():
                if is_secret_key(k) and v not in ("", None):
                    input_id = f"{name}-{k.lower()}"
                    headers[k] = f"${{input:{input_id}}}"
                    inputs.append({
                        "id": input_id,
                        "type": "promptString",
                        "description": f"{k} for {name}",
                        "password": True,
                    })
                else:
                    headers[k] = v
            out["headers"] = headers
    else:
        # stdio (or default)
        if "command" in cfg:
            out["command"] = cfg["command"]
        if "args" in cfg:
            out["args"] = cfg["args"]
        if "env" in cfg:
            env = {}
            for k, v in cfg["env"].items():
                if is_secret_key(k) and v not in ("", None):
                    input_id = f"{name}-{k.lower()}"
                    env[k] = f"${{input:{input_id}}}"
                    inputs.append({
                        "id": input_id,
                        "type": "promptString",
                        "description": f"{k} for {name}",
                        "password": True,
                    })
                else:
                    env[k] = v
            out["env"] = env
    return out, inputs


def vscode_to_cli_server(name, cfg):
    """Convert a VS Code servers-style entry to a mcpServers-style entry."""
    out = {"tools": ["*"]}

    if cfg.get("type") == "http":
        out["type"] = "http"
        out["url"] = cfg["url"]
        if "headers" in cfg:
            headers = {}
            for k, v in cfg["headers"].items():
                headers[k] = "" if isinstance(v, str) and v.startswith("${input:") else v
            out["headers"] = headers
    else:
        out["type"] = "stdio"
        if "command" in cfg:
            out["command"] = cfg["command"]
        if "args" in cfg:
            out["args"] = cfg["args"]
        if "env" in cfg:
            env = {}
            for k, v in cfg["env"].items():
                env[k] = "" if isinstance(v, str) and v.startswith("${input:") else v
            out["env"] = env
    return out


def backup(path: Path):
    if path.exists():
        ts = time.strftime("%Y%m%d-%H%M%S")
        bak = path.with_suffix(path.suffix + f".bak.{ts}")
        shutil.copy2(path, bak)
        return bak
    return None


def main():
    dry_run = "--dry-run" in sys.argv

    cli_data = load_jsonc(CLI_CONFIG) if CLI_CONFIG.exists() else {"mcpServers": {}}
    vsc_data = load_jsonc(VSCODE_CONFIG) if VSCODE_CONFIG.exists() else {"servers": {}, "inputs": []}

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
            cli_servers[name] = vscode_to_cli_server(name, cfg)
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
    print("were set to \"\" placeholders - edit ~/.copilot/mcp-config.json")
    print("to fill in real tokens.")


if __name__ == "__main__":
    main()
