This is a Home Assistant custom integration intended for use with [HACS](https://hacs.xyz/docs/publish/integration/).

See the README.md for its intended use cases and workflows.

Development:

- Changes should be made on branches and merged to main thru pull requests.
- Pull requests should only be merged when CI passes.
- Commits should be small and complete.
- Don't reference Claude or Anthropic in commit messages.
- Tests and lint should pass before committing.
- Never use `git push --force`. Use `--force-with-lease` instead.
- Strive for total behavioral coverage, but 100% structural coverage isn't
  worthwhile.
- Changing the version in `custom_component/consumable_tracker/manifest.json`
  will generate a new release. It will also drive changes to the `uv.lock`
  that should also be committed.
- Versioning follows semantic versioning conventions.
- Changes to the integration should avoid breaking the
  [blueprint](https://www.home-assistant.io/docs/blueprint/) in
  `blueprints/automation/consumable_notification.yaml` and vice versa.
- <https://github.com/ludeeus/integration_blueprint> is an example of a good
  custom integration.
- <https://github.com/oncleben31/cookiecutter-homeassistant-custom-component>
  is a cookiecutter for creating custom integrations. It is documented at
  <https://cookiecutter-homeassistant-custom-component.readthedocs.io/>.
- Prefer use of a trailing comma in Python so that formatted diffs are smaller.
