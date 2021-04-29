#!/usr/bin/python
# -*- coding: utf-8 -*-

# copyright (c) 2020, Jacob Floyd
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


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
  mirror:
    description:
      - If True, synchronization will run in "mirror" mode instead of "additive"
    type: bool
extends_documentation_fragment:
  - pulp.squeezer.pulp
author:
  - Jacob Floyd (@cognifloyd)
"""

EXAMPLES = r"""
- name: Sync rpm remote into repository
  rpm_sync:
    api_url: localhost:24817
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
)


def main():
    with PulpAnsibleModule(
        argument_spec=dict(
            remote=dict(required=True),
            repository=dict(required=True),
            mirror=dict(type="bool"),
        ),
    ) as module:

        remote = PulpRpmRemote(module, {"name": module.params["remote"]})
        remote.find(failsafe=False)

        repository = PulpRpmRepository(module, {"name": module.params["repository"]})
        repository.find(failsafe=False)

        repository.process_sync(remote, module.params["mirror"])


if __name__ == "__main__":
    main()
