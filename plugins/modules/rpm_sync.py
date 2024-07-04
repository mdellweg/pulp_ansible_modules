#!/usr/bin/python

# copyright (c) 2020, Jacob Floyd
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: rpm_sync
short_description: Synchronize a rpm remote on a pulp server
description:
  - "This module synchronizes a rpm remote into a repository."
  - "In check_mode this module assumes, nothing changed upstream."
options:
  remote:
    description:
      - Name of the remote to synchronize
    type: str
    required: true
  repository:
    description:
      - Name of the repository
    type: str
    required: true
  sync_policy:
    description:
      - Policy to use when syncing.
      - The module will fall back to use the mirror parameter when pulp_rpm version is less than 3.16.
      - The mirror parameter does not support "mirror_content_only" value.
    type: str
    required: false
    default: "additive"
    choices: ["additive", "mirror_complete", "mirror_content_only"]
  skip_types:
    description:
      - List of content types to skip during sync.
    type: list
    required: false
    elements: str
    choices: ["srpm", "treeinfo"]
  optimize:
    description:
      - Whether or not to optimize sync.
    type: bool
    required: false
    default: true

extends_documentation_fragment:
  - pulp.squeezer.pulp
author:
  - Jacob Floyd (@cognifloyd)
"""

EXAMPLES = r"""
- name: Sync rpm remote into repository
  pulp.squeezer.rpm_sync:
    pulp_url: https://pulp.example.org
    username: admin
    password: password
    repository: repo_1
    remote: remote_1
  register: sync_result
- name: Report synched repository version
  debug:
    var: sync_result.repository_version
"""

RETURN = r"""
  repository_version:
    description: Repository version after synching
    type: dict
    returned: always
"""


from ansible_collections.pulp.squeezer.plugins.module_utils.pulp import (
    PulpAnsibleModule,
    PulpRpmRemote,
    PulpRpmRepository,
    SqueezerException,
    pulp_parse_version,
)


def main():
    with PulpAnsibleModule(
        argument_spec=dict(
            remote=dict(required=True),
            repository=dict(required=True),
            sync_policy=dict(
                type="str",
                default="additive",
                choices=["additive", "mirror_complete", "mirror_content_only"],
            ),
            skip_types=dict(
                type="list",
                elements="str",
                choices=["srpm", "treeinfo"],
            ),
            optimize=dict(type="bool", default=True),
        ),
    ) as module:
        remote = PulpRpmRemote(module, {"name": module.params["remote"]})
        remote.find(failsafe=False)

        repository = PulpRpmRepository(module, {"name": module.params["repository"]})
        repository.find(failsafe=False)

        # pulp_rpm supports sync_policy from 3.16.
        # Earlier versions support only mirror.
        rpm_version = (
            module.pulp_api.api_spec.get("info", {}).get("x-pulp-app-versions", {}).get("rpm", ())
        )
        if pulp_parse_version(rpm_version) >= pulp_parse_version("3.16.0"):
            parameters = {"sync_policy": module.params["sync_policy"]}
        elif module.params["sync_policy"] == "mirror_content_only":
            raise SqueezerException(
                "Cannot use sync policy 'mirror_content_only' with pulp_rpm<3.16"
            )
        else:
            mirror = module.params["sync_policy"] == "mirror_complete"
            parameters = {"mirror": mirror}

        parameters.update(
            {
                key: module.params[key]
                for key in [
                    "skip_types",
                    "optimize",
                ]
                if module.params[key] is not None
            }
        )

        repository.process_sync(remote, parameters)


if __name__ == "__main__":
    main()
