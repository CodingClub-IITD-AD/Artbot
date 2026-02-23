"""Load machine configuration from YAML."""

import os
import yaml


def load_config(path: str = None) -> dict:
    """
    Load the machine config YAML file.

    If no path is given, looks for config/machine.yaml relative to the
    repo root (two levels up from this file).
    """
    if path is None:
        here = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(os.path.dirname(here))
        path = os.path.join(repo_root, "config", "machine.yaml")

    if not os.path.exists(path):
        raise FileNotFoundError(f"Config not found: {path}")

    with open(path, "r") as f:
        config = yaml.safe_load(f)

    return config
