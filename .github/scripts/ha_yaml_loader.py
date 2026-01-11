#!/usr/bin/env python3
"""
Home Assistant YAML Loader Utility

Provides a custom YAML loader that handles Home Assistant specific tags like
!input, !include, !secret, and !env_var.
"""

import yaml


class HomeAssistantLoader(yaml.SafeLoader):
    """Custom YAML loader that handles Home Assistant specific tags."""


def input_constructor(loader: yaml.Loader, node: yaml.Node) -> str | dict | list:
    """Handle !input tags."""
    if isinstance(node, yaml.ScalarNode):
        return f"INPUT:{loader.construct_scalar(node)}"
    if isinstance(node, yaml.MappingNode):
        return {f"INPUT:{k}": v for k, v in loader.construct_mapping(node).items()}
    if isinstance(node, yaml.SequenceNode):
        return [f"INPUT:{item}" for item in loader.construct_sequence(node)]
    return loader.construct_object(node)


def include_constructor(loader: yaml.Loader, node: yaml.Node) -> str:
    """Handle !include tags."""
    return f"INCLUDE:{loader.construct_scalar(node)}"


def secret_constructor(loader: yaml.Loader, node: yaml.Node) -> str:
    """Handle !secret tags."""
    return f"SECRET:{loader.construct_scalar(node)}"


def env_var_constructor(loader: yaml.Loader, node: yaml.Node) -> str:
    """Handle !env_var tags."""
    return f"ENV_VAR:{loader.construct_scalar(node)}"


# Register constructors for Home Assistant tags
HomeAssistantLoader.add_constructor("!input", input_constructor)
HomeAssistantLoader.add_constructor("!include", include_constructor)
HomeAssistantLoader.add_constructor("!secret", secret_constructor)
HomeAssistantLoader.add_constructor("!env_var", env_var_constructor)


def load_ha_yaml(content: str) -> dict:
    """Load YAML content with Home Assistant tag support."""
    return yaml.load(content, Loader=HomeAssistantLoader)


def load_ha_yaml_file(filepath: str) -> dict:
    """Load YAML file with Home Assistant tag support."""
    with open(filepath) as f:
        content = f.read()
    return load_ha_yaml(content)
