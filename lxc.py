#!/usr/bin/python
# -*- coding: utf-8 -*-

import optparse
import json
import subprocess
import sys

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

    cmd = ["lxc-ls", "-f", "-F", "NAME,STATE,PID,RAM,SWAP,AUTOSTART,GROUPS,IPV4,IPV6"]
    lxc_ls_output = execute_command(cmd)

    for idx,line in enumerate(lxc_ls_output.split('\n')):
        items = line.split()
        if idx == 0:
            headers = [x.lower() for x in items]
        elif len(headers) == len(items):
            container = {}
            for idx,header in enumerate(headers):
                container[header] = items[idx]

            if show_meta_hostvars:
                host_list['_meta']['hostvars'][container['name']] = {
                    "ansible_ssh_host": container['name'],
                    "ansible_host": container['name'],
                    "ansible_connection": "lxc"
                }
                for header in container:
                    if header == "name":
                        continue
                    host_list['_meta']['hostvars'][container['name']][header] = container[header]

            host_list[group]['hosts'].append(container['name'])

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
