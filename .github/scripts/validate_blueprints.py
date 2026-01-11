#!/usr/bin/env python3
"""
Home Assistant Blueprint YAML Validation Script

Validates YAML syntax and Home Assistant Blueprint schema compliance.
"""

from __future__ import annotations

import glob
import os
import sys

import yaml
from ha_yaml_loader import HomeAssistantLoader, load_ha_yaml_file


def get_blueprints_dir() -> str:
    """Get the blueprints directory path."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))
    return os.path.join(repo_root, "blueprints")


def find_blueprint_files(blueprints_dir: str) -> list[str]:
    """Find all blueprint YAML files."""
    return glob.glob(
        os.path.join(blueprints_dir, "**/*.yaml"),
        recursive=True,
    ) + glob.glob(
        os.path.join(blueprints_dir, "**/*.yml"),
        recursive=True,
    )


def validate_yaml_syntax() -> bool:
    """Validate YAML syntax for all blueprint files."""
    print("Validating Home Assistant Blueprint YAML syntax...")

    blueprints_dir = get_blueprints_dir()
    blueprint_files = find_blueprint_files(blueprints_dir)

    if not blueprint_files:
        print(f"WARNING: No blueprint files found in {blueprints_dir}")
        return True

    all_valid = True

    for filepath in blueprint_files:
        print(f"Checking: {filepath}")
        try:
            with open(filepath) as f:
                content = f.read()

            yaml.load(content, Loader=HomeAssistantLoader)
            print("  Valid YAML syntax")

        except yaml.YAMLError as e:
            print(f"  ERROR: Invalid YAML - {e}")
            all_valid = False
        except Exception as e:
            print(f"  ERROR: {e}")
            all_valid = False

    return all_valid


def validate_blueprint_schema() -> bool:
    """Validate Home Assistant Blueprint schema compliance."""
    print("Validating Home Assistant Blueprint schema...")

    blueprints_dir = get_blueprints_dir()
    blueprint_files = find_blueprint_files(blueprints_dir)

    required_fields = ["name", "domain"]
    valid_domains = ["automation", "script", "template"]
    all_valid = True

    for filepath in blueprint_files:
        print(f"Validating: {filepath}")
        try:
            data = load_ha_yaml_file(filepath)

            if not isinstance(data, dict):
                print("  ERROR: Blueprint must be a YAML object")
                all_valid = False
                continue

            if "blueprint" not in data:
                print('  ERROR: Missing "blueprint" key')
                all_valid = False
                continue

            blueprint = data["blueprint"]

            # Check required fields
            for field in required_fields:
                if field not in blueprint:
                    print(f'  ERROR: Missing required field "{field}"')
                    all_valid = False

            # Validate domain
            if "domain" in blueprint and blueprint["domain"] not in valid_domains:
                print(
                    f'  ERROR: Invalid domain "{blueprint["domain"]}". '
                    f"Must be one of {valid_domains}",
                )
                all_valid = False

            # Validate name is a string and not empty
            if "name" in blueprint and (
                not isinstance(blueprint["name"], str) or not blueprint["name"].strip()
            ):
                print("  ERROR: Blueprint name must be a non-empty string")
                all_valid = False

            # Check for recommended fields
            recommended_fields = ["description"]
            missing_recommended = [f for f in recommended_fields if f not in blueprint]
            if missing_recommended:
                print(f"  WARNING: Missing recommended fields {missing_recommended}")

            if all_valid:
                print("  Valid blueprint schema")

        except yaml.YAMLError as e:
            print(f"  ERROR: YAML error - {e}")
            all_valid = False
        except Exception as e:
            print(f"  ERROR: {e}")
            all_valid = False

    return all_valid


def check_duplicate_names() -> bool:
    """Check for duplicate blueprint names."""
    print("Checking for duplicate blueprint names...")

    blueprints_dir = get_blueprints_dir()
    blueprint_files = find_blueprint_files(blueprints_dir)

    names: dict[str, str] = {}
    duplicates: list[tuple[str, str, str]] = []

    for filepath in blueprint_files:
        try:
            data = load_ha_yaml_file(filepath)

            if "blueprint" in data and "name" in data["blueprint"]:
                name = data["blueprint"]["name"]
                if name in names:
                    duplicates.append((name, names[name], filepath))
                else:
                    names[name] = filepath
        except Exception as e:
            print(f"Error reading {filepath}: {e}")

    if duplicates:
        print("ERROR: Duplicate blueprint names found:")
        for name, file1, file2 in duplicates:
            print(f'  "{name}" in {file1} and {file2}')
        return False

    print("  No duplicate blueprint names found")
    return True


def main() -> None:
    """Run blueprint validations."""
    if len(sys.argv) > 1:
        validation_type = sys.argv[1]

        if validation_type == "syntax":
            success = validate_yaml_syntax()
        elif validation_type == "schema":
            success = validate_blueprint_schema()
        elif validation_type == "duplicates":
            success = check_duplicate_names()
        else:
            print(f"Unknown validation type: {validation_type}")
            print("Usage: python validate_blueprints.py [syntax|schema|duplicates]")
            sys.exit(1)
    else:
        # Run all validations
        syntax_ok = validate_yaml_syntax()
        schema_ok = validate_blueprint_schema()
        duplicates_ok = check_duplicate_names()
        success = syntax_ok and schema_ok and duplicates_ok

    if not success:
        sys.exit(1)

    print("All validations passed!")


if __name__ == "__main__":
    main()
