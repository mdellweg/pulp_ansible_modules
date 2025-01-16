#!/usr/bin/python

# copyright (c) 2019, Matthias Dellweg
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
---
module: file_distribution
short_description: Manage file distributions of a pulp api server instance
description:
  - "This performs CRUD operations on file distributions in a pulp api server instance."
options:
  name:
    description:
      - Name of the distribution to query or manipulate
    type: str
    required: false
  base_path:
    description:
      - Base path to distribute a publication
    type: str
    required: false
  publication:
    description:
      - Href of the publication to be served
    type: str
    required: false
  content_guard:
    description:
      - Name of the content guard for the served content
      - "Warning: This feature is not yet supported."
    type: str
    required: false
extends_documentation_fragment:
  - pulp.squeezer.pulp.entity_state
  - pulp.squeezer.pulp.glue
  - pulp.squeezer.pulp
author:
  - Matthias Dellweg (@mdellweg)
"""

EXAMPLES = r"""
- name: Read list of file distributions from pulp api server
  pulp.squeezer.file_distribution:
    pulp_url: https://pulp.example.org
    username: admin
    password: password
  register: distribution_status
- name: Report pulp file distributions
  debug:
    var: distribution_status

- name: Create a file distribution
  pulp.squeezer.file_distribution:
    pulp_url: https://pulp.example.org
    username: admin
    password: password
    name: new_file_distribution
    base_path: new/file/dist
    publication: /pub/api/v3/publications/file/file/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/
    state: present

- name: Delete a file distribution
  pulp.squeezer.file_distribution:
    pulp_url: https://pulp.example.org
    username: admin
    password: password
    name: new_file_distribution
    state: absent
"""

RETURN = r"""
  distributions:
    description: List of file distributions
    type: list
    returned: when no name is given
  distribution:
    description: File distribution details
    type: dict
    returned: when name is given
"""


import traceback

from ansible_collections.pulp.squeezer.plugins.module_utils.pulp_glue import PulpEntityAnsibleModule

try:
    from pulp_glue.core.context import PulpContentGuardContext
    from pulp_glue.file.context import PulpFileDistributionContext

    PULP_CLI_IMPORT_ERR = None
except ImportError:
    PULP_CLI_IMPORT_ERR = traceback.format_exc()
    PulpFileDistributionContext = None


def main():
    with PulpEntityAnsibleModule(
        context_class=PulpFileDistributionContext,
        entity_singular="distribution",
        entity_plural="distributions",
        import_errors=[("pulp-glue", PULP_CLI_IMPORT_ERR)],
        argument_spec={
            "name": {},
            "base_path": {},
            "publication": {},
            "content_guard": {},
        },
        required_if=[
            ("state", "present", ["name", "base_path"]),
            ("state", "absent", ["name"]),
        ],
    ) as module:
        content_guard_name = module.params["content_guard"]

        natural_key = {"name": module.params["name"]}
        desired_attributes = {
            key: module.params[key]
            for key in ["base_path", "publication"]
            if module.params[key] is not None
        }

        if content_guard_name is not None:
            if content_guard_name:
                content_guard_ctx = PulpContentGuardContext(
                    module.pulp_ctx, entity={"name": content_guard_name}
                )
                desired_attributes["content_guard"] = content_guard_ctx.pulp_href
            else:
                desired_attributes["content_guard"] = ""

        module.process(natural_key, desired_attributes)


if __name__ == "__main__":
    main()
