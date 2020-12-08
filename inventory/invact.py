#!/usr/bin/env python
# This inventory file only returns VM's with running status.

import os
import sys
import yaml
import argparse
import json
import re
import configparser
from os.path import expanduser
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.network import NetworkManagementClient
import logging
logger=logging.getLogger('msrestazure.azure_active_directory')
logger.addHandler(logging.NullHandler())

AZURE_CREDENTIAL_ENV_MAPPING = dict(
    subscription_id='AZURE_SUBSCRIPTION_ID',
    client_id='AZURE_CLIENT_ID',
    secret='AZURE_SECRET',
    tenant='AZURE_TENANT'
)
def get_resource_group(file, sec):
    'Get the correct name of resource group used for VM!'
    with open(file,'r') as f:
        vars=yaml.safe_load(f)
    rg=vars
    for e in sec.split('.'):
        rg=rg.get(e)
    
    # rg-{{region}}{{env.hyphen[project]}}api --> rg-aus{{env.hyphen[project]}}api
    sub=re.findall(r'(?<={{)\w*?(?=}})',rg) 
    for s in sub:
        rg=rg.replace('{{'+s+'}}', vars.get(s))

    # rg-aus{{env.hyphen[project]}}api --> rg-aus{{env.hyphen.dev}}api
    sub=re.findall(r'(?<=\[)\w*(?=\])',rg)   # get [*], return ['project'] # rg-{{region}}{{env.hyphen[project]}}api
    for s in sub:
        rg=rg.replace('['+s+']', '.'+vars.get(s))

    # rg-aus{{env.hyphen.dev}}api --> rg-aus-dev-api
    sub=re.findall(r'(?<={{)[\w.]*?(?=}})',rg)
    for s in sub:
        tmp = vars
        for e in s.split('.'):
            tmp=tmp.get(e)
        rg=rg.replace('{{'+s+'}}', tmp)
    return rg

VARFILE=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'all-variables.yml')
RESOURCE_GROUP = get_resource_group(VARFILE,'common.rg')

class Inventory(object):
    def __init__(self):
        self.inventory = dict(_meta=dict(hostvars=dict()), azure_running=[])
        self.read_cli_args()
        self.credentials = self.get_profile()
        self.subscription_id = self.credentials['subscription_id']

        self.azure_credentials = ServicePrincipalCredentials(
                client_id=self.credentials['client_id'],
                secret=self.credentials['secret'],
                tenant=self.credentials['tenant'])
        self.network_client = NetworkManagementClient(self.azure_credentials,
                                                      self.subscription_id)
        self.compute_client = ComputeManagementClient(self.azure_credentials,
                                                      self.subscription_id)
        self.vm_list = self.compute_client.virtual_machines.list(
                self.args.rg)
        try:
            self.get_inventory(self.vm_list)
        except Exception as exc:
            pass
        print(json.dumps(self.inventory, indent=2))

    def _parse_ref_id(self, reference):
        response = {}
        keys = reference.strip('/').split('/')
        for index in range(len(keys)):
            if index < len(keys) - 1 and index % 2 == 0:
                response[keys[index]] = keys[index + 1]
        return response

    def _add_host(self, vars):
        if self.args.public:
            host_name = vars['public_ip']
        else:
            host_name = vars['private_ip']
        self.inventory['_meta']['hostvars'][host_name] = vars
        self.inventory['azure_running'].append(host_name)

    def get_inventory(self, vmlist):
        for vm in vmlist:
            running_status = self.compute_client.virtual_machines.get(self.args.rg, vm.name ,expand='instanceView').instance_view.statuses[1].display_status
            if "running" in running_status:
                host_vars = dict(
                    location=vm.location,
                    name=vm.name,
                    id=vm.id,
                    tags=vm.tags,
                    public_ip=None,
                    private_ip=None
                )
                for interface in vm.network_profile.network_interfaces:
                    interface_reference = self._parse_ref_id(interface.id)
                    network_interface = self.network_client.network_interfaces.\
                        get(interface_reference['resourceGroups'],
                            interface_reference['networkInterfaces'])
                    if network_interface.primary:
                        for ip_config in network_interface.ip_configurations:
                            host_vars['private_ip'] = ip_config.private_ip_address
                            if ip_config.public_ip_address:
                                public_ip_reference = self._parse_ref_id(
                                    ip_config.public_ip_address.id)
                                public_ip_address = self.network_client.\
                                    public_ip_addresses.get(
                                        public_ip_reference['resourceGroups'],
                                        public_ip_reference['publicIPAddresses'])
                                host_vars['public_ip'] = public_ip_address.\
                                    ip_address
                self._add_host(host_vars)

    # Empty inventory for testing.
    def empty_inventory(self):
        return {'_meta': {'hostvars': {}}}

    # Read the command line args passed to the script.
    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action='store_true',
                            help='Ansible calls with `--list`')
        parser.add_argument('--host', action='store',
                            help='Unimplemented due to _meta in `--list`')
        parser.add_argument('--rg', action='store',
                            default=RESOURCE_GROUP,
                            help='Resource Group: default='+RESOURCE_GROUP)
        parser.add_argument('--public', action='store_true',
                            help='Use public ip in inventory.')
        self.args = parser.parse_args()

    def get_profile(self, profile="default"):
        credentials = dict()
        if os.getenv('AZURE_CLIENT_ID') and os.getenv('AZURE_SECRET') and os.getenv('AZURE_SUBSCRIPTION_ID') and os.getenv('AZURE_TENANT'):
            credentials['subscription_id'] = os.getenv('AZURE_SUBSCRIPTION_ID')
            credentials['client_id'] = os.getenv('AZURE_CLIENT_ID')
            credentials['secret'] = os.getenv('AZURE_SECRET')
            credentials['tenant'] = os.getenv('AZURE_TENANT')
            return credentials

        path = expanduser("~")
        path += "/.azure/credentials"
        try:
            config = ConfigParser.ConfigParser()
            config.read(path)
        except Exception as exc:
            self.fail("Failed to access {0}. ERR: {1}".format(path, str(exc)))
        for key in AZURE_CREDENTIAL_ENV_MAPPING:
            try:
                credentials[key] = config.get(profile, key, raw=True)
            except:
                self.fail("Failed to get {0}".format(key))
        return credentials

    def fail(self, msg):
        raise Exception(msg)

# Get the inventory.
if __name__ == '__main__':
    Inventory()
