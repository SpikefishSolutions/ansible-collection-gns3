#!/usr/bin/env python

ANSIBLE_METADATA = {
    "metadata_version": "1.2",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
---
module: gns3_nodes_inventory
short_description: Retrieves GNS3 a project nodes console information
version_added: '2.8'
description:
    - "Retrieves nodes inventory information from a GNS3 project"
requirements: [ gns3fy ]
author:
    - David Flores (@davidban77)
options:
    url:
        description:
            - URL target of the GNS3 server
        required: true
        type: str
    port:
        description:
            - TCP port to connect to server REST API
        type: int
        default: 3080
    user:
        description:
            - User to connect to GNS3 server
        type: str
    password:
        description:
            - Password to connect to GNS3 server
        type: str
    project_name:
        description:
            - Project name
        type: str
    project_id:
        description:
            - Project ID
        type: str
"""

EXAMPLES = """
# Retrieve the GNS3 server version
- name: Get the server version
  gns3_nodes_inventory:
    url: http://localhost
    port: 3080
    project_name: test_lab
  register: nodes_inventory

- debug: var=nodes_inventory
"""

RETURN = """
nodes_inventory:
    description: Dictionary that contain: name, server, console_port, console_type,
    type and template of each node
    type: dict
total_nodes:
    description: Total number of nodes
    type: int
"""
import traceback

GNS3FY_IMP_ERR = None
try:
    from gns3fy import Gns3Connector, Project, Node

    HAS_GNS3FY = True
except ImportError:
    GNS3FY_IMP_ERR = traceback.format_exc()
    HAS_GNS3FY = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib


def main():
    module = AnsibleModule(
        argument_spec=dict(
            url=dict(type="str", required=True),
            port=dict(type="int", default=3080),
            user=dict(type="str", default=None),
            password=dict(type="str", default=None, no_log=True),
            project_name=dict(type="str", default=None),
            project_id=dict(type="str", default=None),
        ),
        required_one_of=[["project_name", "project_id"]],
    )
    if not HAS_GNS3FY:
        module.fail_json(msg=missing_required_lib("gns3fy"), exception=GNS3FY_IMP_ERR)
    result = dict(changed=False, nodes_inventory=None, total_nodes=None)

    server_url = module.params["url"]
    server_port = module.params["port"]
    server_user = module.params["user"]
    server_password = module.params["password"]
    project_name = module.params["project_name"]
    project_id = module.params["project_id"]

    # Create server session
    server = Gns3Connector(
        url="%s:%s" % (server_url, server_port), user=server_user, cred=server_password
    )
    # Define the project
    if project_name is not None:
        project = Project(name=project_name, connector=server)
    elif project_id is not None:
        project = Project(project_id=project_id, connector=server)

    # Retrieve project info
    project.get()

    nodes_inventory = project.nodes
    for _n in nodes_inventory: 
        result[_n.name] = dict(
                project_id         = _n.project_id,
                node_id            = _n.node_id,
                compute_id         = _n.compute_id,
                node_type          = _n.node_type,
#               connector          = _n.connector,
                template_id        = _n.template_id,
                template           = _n.template,
                node_directory     = _n.node_directory,
                status             = _n.status,
                ports              = _n.ports, 
                port_name_format   = _n.port_name_format,
                port_segment_size  = _n.port_segment_size,
                first_port_name    = _n.first_port_name,
                properties         = _n.properties,
                locked             = _n.locked,
                label              = _n.label,
                console            = _n.console,
                console_host       = _n.console_host,
                console_auto_start = _n.console_auto_start,
                command_line       = _n.command_line,
                custom_adapters    = _n.custom_adapters,
                height             = _n.height,
                width              = _n.width,
                symbol             = _n.symbol,
                x                  = _n.x,
                y                  = _n.y,
                z                  = _n.z,
                )
        if isinstance(_n.properties, dict):
            hd_image_names = {
                "hda_disk_image": "hda_disk.qcow2",
                "hdb_disk_image": "hdb_disk.qcow2", 
                "hdc_disk_image": "hdc_disk.qcow2", 
                "hdd_disk_image": "hdd_disk.qcow2", 
            }
            for disk_image in hd_image_names:
                if disk_image in _n.properties:
                    if _n.properties[disk_image] != "":
                        key = "_".join([disk_image, "real"])
                        _n.properties[key] = hd_image_names[disk_image]

    module.exit_json(**result)


if __name__ == "__main__":
    main()
