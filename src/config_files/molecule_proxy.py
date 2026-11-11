"""Proxy support for Molecule runs: detect a loopback proxy and generate a matching scenario."""

import contextlib
import ipaddress
import logging
import shutil
import tempfile
from collections.abc import Generator, Mapping
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

logger = logging.getLogger(__name__)

PROXY_ENV_NAMES = (
    "http_proxy",
    "https_proxy",
    "no_proxy",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "NO_PROXY",
)
LOCAL_PROXY_HOSTS = {"localhost"}
DEFAULT_SCENARIO = "default"


def proxy_environment_value(env: Mapping[str, str], name: str) -> str | None:
    """Return a proxy environment value independent of variable casing."""
    return env.get(name) or env.get(name.upper()) or env.get(name.lower())


def is_local_proxy_url(proxy_url: str) -> bool:
    """Check whether a proxy URL points at the local host."""
    value = proxy_url.strip()
    if not value:
        return False

    parsed_url = urlparse(value)
    if not parsed_url.hostname and "://" not in value:
        parsed_url = urlparse(f"http://{value}")

    hostname = parsed_url.hostname
    if not hostname:
        return False

    if hostname.lower() in LOCAL_PROXY_HOSTS:
        return True

    try:
        return ipaddress.ip_address(hostname).is_loopback
    except ValueError:
        return False


def has_local_proxy(env: Mapping[str, str]) -> bool:
    """Check whether the given environment uses a loopback proxy."""
    return any(
        is_local_proxy_url(proxy_url)
        for proxy_url in (
            proxy_environment_value(env, "http_proxy"),
            proxy_environment_value(env, "https_proxy"),
        )
        if proxy_url
    )


def normalize_proxy_environment(env: Mapping[str, str]) -> dict[str, str]:
    """Set both upper- and lower-case proxy variables for Molecule interpolation."""
    proxy_env = dict(env)
    for name in ("http_proxy", "https_proxy", "no_proxy"):
        value = proxy_environment_value(env, name)
        if value:
            proxy_env[name] = value
            proxy_env[name.upper()] = value
    return proxy_env


def add_proxy_to_molecule_config(config: dict[str, Any]) -> dict[str, Any]:
    """Add local proxy Docker options to a Molecule config."""
    proxy_values = {name: f"${{{name}}}" for name in PROXY_ENV_NAMES}
    for platform in config.get("platforms", []):
        platform["network_mode"] = "host"
        platform["buildargs"] = proxy_values
        platform["env"] = proxy_values
    return config


@contextlib.contextmanager
def molecule_scenario(
    test_role: Path, env: Mapping[str, str]
) -> Generator[tuple[str, dict[str, str]]]:
    """Yield a Molecule scenario name and environment for this run.

    Without a loopback proxy the default scenario is used unchanged. With one, a
    temporary scenario is generated next to it and removed afterwards.
    """
    if not has_local_proxy(env):
        yield DEFAULT_SCENARIO, dict(env)
        return

    source_scenario = test_role / "molecule" / DEFAULT_SCENARIO
    generated_scenario = Path(
        tempfile.mkdtemp(prefix="cf_molecule_", dir=source_scenario.parent)
    )
    try:
        shutil.copytree(
            source_scenario, generated_scenario, symlinks=True, dirs_exist_ok=True
        )
        generated_config_file = generated_scenario / "molecule.yml"
        molecule_config = yaml.safe_load(generated_config_file.read_text())
        if generated_config_file.is_symlink():
            generated_config_file.unlink()
        generated_config_file.write_text(
            yaml.safe_dump(
                add_proxy_to_molecule_config(molecule_config),
                explicit_start=True,
                sort_keys=False,
            ),
        )
        logger.info(
            "Local proxy detected, using generated Molecule scenario: %s",
            generated_scenario.name,
        )
        yield generated_scenario.name, normalize_proxy_environment(env)
    finally:
        shutil.rmtree(generated_scenario, ignore_errors=True)
