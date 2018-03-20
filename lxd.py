#!/usr/bin/python
# -*- coding: utf-8 -*-

import optparse
import json
import subprocess
import sys
import os
import lxc

def execute_command(command):
    # ToDo :
    # Catch d'une exception si l'éxécutable n'est pas trouvé
    # Plus gestion d'un return code différent de 0
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = proc.communicate()[0]
    return result

def get_inventory(show_meta_hostvars):
    group = "LXC_CONTAINERS"

    if show_meta_hostvars:
        host_list = {
            "_meta": {
                "hostvars": {}
            }
        }
    else:
        host_list = {}

    host_list[group] = {'hosts': []}

    containers_path = '/sys/fs/cgroup/devices/lxc'
    num_sep = containers_path.count(os.path.sep)
    for dirname, dirnames, filenames in os.walk(containers_path):
        if dirname.count(os.path.sep) - num_sep == 1:
            container = dirname.split(os.path.sep)[-1]
            host_list[group]['hosts'].append(container)
            if show_meta_hostvars:
                host_list['_meta']['hostvars'][container] = {
                    "ansible_connection": "lxd"
                }

    return host_list

def main():
    parser = optparse.OptionParser()
    parser.add_option('--list', action='store_true', dest='list',
                      default=False, help='Liste les containers lxc')
    # parser.add_option('--host', dest='host', default=None, metavar='HOST',
    #                   help='Liste les variables pout un hote')

    # Ces options ne sont pas utilisés par Ansible, uniquement si appelé depuis la CLI
    parser.add_option('--pretty', action='store_true', dest='pretty',
                      default=False, help='Pretty print du JSON')
    parser.add_option('--no-meta-hostvars', action='store_false',
                      dest='meta_hostvars', default=True,
                      help='Retire [\'_meta\'][\'hostvars\'] avec --list')
    options, args = parser.parse_args()


    inventory = get_inventory(options.meta_hostvars)

    # if options.host is not None:
    #     inventory = "get_host(options.host)"
    # else:
    #     inventory = "get_inventory(options.meta_hostvars)"

    json_kwargs = {}
    if options.pretty:
        json_kwargs.update({'indent': 4, 'sort_keys': True})
    json.dump(inventory, sys.stdout, **json_kwargs)


if __name__ == '__main__':
    main()
