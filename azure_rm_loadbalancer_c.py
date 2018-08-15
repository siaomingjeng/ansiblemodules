#!/usr/bin/python
#
# Copyright (c) 2016 Thomas Stringer, <tomstr@microsoft.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: azure_rm_loadbalancer_c

version_added: "2.5"

short_description: Manage Azure load balancers.

description:
    - Create, update and delete Azure load balancers including multiple frontends, multiple backends, multiple load balancer rules and multiple NAT rules.

options:
    resource_group:
        description:
            - Name of a resource group where the load balancer exists or will be created.
        required: true
    location:
        description:
            - Valid azure location. Defaults to location of the resource group.
        default: resource_group location
        required: false
    name:
        description:
            - Name of the load balancer.
        required: true
    state:
        description:
            - Assert the state of the load balancer. Use 'present' to create or update a load balancer and 'absent' to delete a load balancer.
        default: present
        choices:
            - absent
            - present
        required: false
    frontend_ip_configs:
        description:
            - Describes a list of frontend ip configurations
        required: false
        suboptions:
            name:
                description:
                    - Name of the frontend ip configuration.
                required: true
            public_ip_name:
                description:
                    - Name of an existing public IP address object to associate with the security group.
                required: false
            private_ip_address:
                description:
                    - The private ipv4 address of the frontend ip configuration.
                required: false
            subnet_name:
                description:
                    - Name of an existing subnet within the specified virtual network. Required when virtual_network_name is given.
                required: false
            resource_group:
                description:
                    - Name of a resource group where the subnet exists.
                required: false
                default: resource_group
            vnet_name:
                description:
                    - Name of an existing virtual network. Required when subnet_name is given.
                required: false
    backend_pools:
        description:
            - a list of names of the backend address pool.
        required: false
    health_probes:
        description:
            - describes a list of health probes
        required: false
        suboptions:
            name:
                description:
                    - Name of the health probe.
                required: true
            port:
                description:
                    - The port that the health probe will use.
                default: 80
                required: false
            protocol:
                description:
                    - The protocol to use for the health probe.
                choices:
                    - Tcp
                    - Http
                default: Tcp
                required: false
            interval:
                description:
                    - How much time (in seconds) to probe the endpoint for health.
                default: 15
                required: false
            fail_count:
                description:
                    - The amount of probe failures for the load balancer to make a health determination.
                default: 3
                required: false
            request_path:
                description:
                    - The URL that an HTTP probe will use (only relevant if probe_protocol is set to Http).
                default: /
                required: false
    load_balancing_rules:
        description:
            - Describes a list of load balancing rules.
        required: false
        suboptions:
            name:
                description:
                    - Name of the load balancing rule.
                required: true
            frontend_name:
                description:
                    - Name of frontend ip configuraton.
                required: true
            backend_name:
                description:
                    - Name of backend pool.
                required: true
            probe_name:
                description:
                    - Name of health probe.
                required: true
            protocol:
                description:
                    - The protocol (TCP or UDP) that the load balancer will use.
                required: false
                choices:
                    - Tcp
                    - Udp
                default: Tcp
            load_distribution:
                description:
                    - The type of load distribution that the load balancer will employ.
                required: false
                default: Default
                choices:
                    - Default
                    - SourceIP
                    - SourceIPProtocol
            frontend_port:
                description:
                    - Frontend port that will be exposed for the load balancer.
                default: 80
                required: false
            backend_port:
                description:
                    - Backend port that will be exposed for the load balancer.
                default: 80
                required: false
            idle_timeout:
                description:
                    - Timeout for TCP idle connection in minutes.
                default: 15
                required: false
            enable_floating_ip:
                description:
                    - We recommend using this feature only when configuring a SQL AlwaysOn Availiabity Group Listerner.
                      It can be. enabled only when creating a rule and if the frontend prot and backend port match.
                default: false
                required: false
    inbound_nat_rules:
        description:
            - Describes a list of inbound NAT rules.
        required: false
        suboptions:
            name:
                description:
                    - Name of the inbound NAT rule. Default to <load balancer>-nat-<index>
                required: true
            frontend_name:
                description:
                    - Name of frontend ip configuraton.
                required: true
            protocol:
                description:
                    - The protocol (TCP or UDP) that the inbount nat rule will use.
                required: false
                choices:
                    - Tcp
                    - Udp
                default: Tcp
            frontend_port:
                description:
                    - Frontend port that will be exposed for the inbound nat rule. Acceptable values range from 1 to 65535.
                required: true
            backend_port:
                description:
                    - Backend port that will be exposed for the inbound nat rule. Default to nat_frontend_port.
                required: true
            enable_floating_ip:
                description:
                    - Configures a virtual machine's endpoint for the floating IP capability required to configure a SQL AlwaysOn Availability Group.
                      This setting is required when using the SQL AlwaysOn Availability Groups in SQL server.
                      This setting can't be changed after you create the
                required: false
                default: fase
            idle_timeout:
                description:
                    - Timeout for TCP idle connection in minutes. The value can be set between 4 and 30 minutes.
                      The default value is 4 minutes. This element is only used when the protocol is set to TCP.
                default: 4
                required: false

extends_documentation_fragment:
    - azure
    - azure_tags

author:
    - "Xiaoming Zheng (@siaomingjeng)"
'''

EXAMPLES = '''
    - name: Create a load balancer configuring the frontend using internal private IP from a subnet of a different resource group.
      azure_rm_loadbalancer:
        name: myloadbalancer
'''

RETURN = '''
state:
    description: Current state of the load balancer
    returned: always
    type: dict
changed:
    description: Whether or not the resource has changed
    returned: always
    type: bool
'''

from ansible.module_utils.azure_rm_common import AzureRMModuleBase

try:
    from msrestazure.azure_exceptions import CloudError
    from azure.mgmt.network.models import (
        LoadBalancer,
        FrontendIPConfiguration,
        BackendAddressPool,
        Probe,
        LoadBalancingRule,
        SubResource,
        InboundNatPool,
        InboundNatRule,
        Subnet
    )
except ImportError:
    # This is handled in azure_rm_common
    pass


class DiffErr(Exception):
    """Used to stop value compare when finding one"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class AzureRMLoadBalancer(AzureRMModuleBase):
    """Configuration class for an Azure RM load balancer resource"""

    def __init__(self):
        self.module_args = dict(
            resource_group=dict(type='str', required=True),
            name=dict(type='str', required=True),
            state=dict(type='str', required=False, default='present', choices=['present', 'absent']),
            location=dict(type='str', required=False),
            frontend_ip_configs=dict(type='list'),
            backend_pools=dict(type='list'),
            health_probes=dict(type='list'),
            load_balancing_rules=dict(type='list'),
            inbound_nat_rules=dict(type='list'),
        )

        self.resource_group = None
        self.name = None
        self.location = None
        self.state = None
        self.frontend_ip_configs = None
        self.backend_pools = None
        self.health_probes = None
        self.load_balancing_rules = None
        self.inbound_nat_rules = None
        self.tags = None

        self.results = dict(changed=False, state=dict())

        super(AzureRMLoadBalancer, self).__init__(
            derived_arg_spec=self.module_args,
            supports_check_mode=True
        )

    def exec_module(self, **kwargs):
        """Main module execution method"""
        for key in list(self.module_args.keys()) + ['tags']:
            setattr(self, key, kwargs[key])

        if self.state == 'absent':
            try:
                self.network_client.load_balancers.delete(resource_group_name=self.resource_group, load_balancer_name=self.name).wait()
                changed = True
            except CloudError:
                changed = False
            self.results['changed'] = changed
            return self.results

        # From now on, suppose state==present

        # INPUT CHECK TO BE COMPLETED!!!

        results = dict()
        changed = False
        pip = None
        subnet = None
        load_balancer_props = dict()

        try:
            resource_group = self.get_resource_group(self.resource_group)
        except CloudError:
            self.fail('resource group {0} not found'.format(self.resource_group))
        if not self.location:
            self.location = resource_group.location
        load_balancer_props['location'] = self.location

        # CHECK INPUT AND SET DEFAULT VALUE:
        self.frontnamelist = []
        for front in self.frontend_ip_configs:
            if not front.get('name') or front['name'] in self.frontnamelist:
                self.fail('name is not provided correctly in one of frontend_ip_configs.')
            self.frontnamelist.append(front['name'])
            if not front.get('public_ip_name') and not (front.get('subnet_name') and front.get('vnet_name')):
                self.fail('frontend_ip_configs error: neither public_ip_name nor the combination of subnet_name and vnet_name is provided.')
            if not front.get('resource_group'):
                front['resource_group'] = self.resource_group
        self.probenamelist = []
        for probe in self.health_probes:
            if not probe.get('name') or probe['name'] in self.probenamelist:
                self.fail('name is not provided correctly in one of health_probes.')
            self.probenamelist.append(probe['name'])
            if not probe.get('fail_count'):
                probe['fail_count'] = 3
            if not probe.get('interval'):
                probe['interval'] = 15
            if not probe.get('port'):
                probe['port'] = 80
            if not probe.get('protocol'):
                probe['protocol'] = 'Tcp'
            if not probe.get('request_path'):
                probe['request_path'] = '/'
        self.rulenamelist = []
        for rule in self.load_balancing_rules:
            if not rule.get('name') or rule['name'] in self.rulenamelist:
                self.fail('name is not provided in one of load_balancing_rules.')
            self.rulenamelist.append(rule['name'])
            if not rule.get('frontend_name') or rule['frontend_name'] not in self.frontnamelist:
                self.fail('frontend_name is not provied correctly in one of load_balancing_rules.')
            if not rule.get('backend_name') or rule['backend_name'] not in self.backend_pools:
                self.fail('backend_name is not provied correctly in one of load_balancing_rules.')
            if not rule.get('probe_name') or rule['probe_name'] not in self.probenamelist:
                self.fail('probe_name is not provied correctly in one of load_balancing_rules.')
            if not rule.get('load_distribution'):
                rule['load_distribution'] = 'Default'
            if not rule.get('frontend_port'):
                rule['frontend_port'] = 80
            if not rule.get('backend_port'):
                rule['backend_port'] = rule['frontend_port']
            if not rule.get('protocol'):
                rule['protocol'] = 'Tcp'
            if rule.get('enable_floating_ip') in ['True', 'true', 'Yes', 'yes']:
                rule['enable_floating_ip'] = True
            else:
                rule['enable_floating_ip'] = False
            if not rule.get('idle_timeout'):
                rule['idle_timeout'] = 15
        self.natnamelist = []
        for nat in self.inbound_nat_rules:
            if not nat.get('name') or nat['name'] in self.natnamelist:
                self.fail('name is not provided in one of inbound_nat_rules.')
            self.natnamelist.append(nat['name'])
            if not nat.get('frontend_name') or nat['frontend_name'] not in self.frontnamelist:
                self.fail('frontend_name is not provided correctly in one of inbound_nat_rules.')
            if not nat.get('frontend_port'):
                self.fail('frontend_port is not provided in one of inbound_nat_rules.')
            if not nat.get('backend_port'):
                self.fail('backend_port is not provided in one of inbound_nat_rules.')
            if not nat.get('protocol'):
                nat['protocol'] = 'Tcp'
            if nat.get('enable_floating_ip') in ['True', 'true', 'Yes', 'yes']:
                nat['enable_floating_ip'] = True
            else:
                nat['enable_floating_ip'] = False
            if not nat.get('idle_timeout'):
                nat['idle_timeout'] = 4

        # handle present status
        try:
            # before we do anything, we need to attempt to retrieve the load balancer and compare with current parameters
            self.log('Fetching load balancer {0}'.format(self.name))
            load_balancer = self.network_client.load_balancers.get(self.resource_group, self.name)
            self.log('Load balancer {0} exists'.format(self.name))
            self.check_provisioning_state(load_balancer, self.state)
            results = load_balancer_to_dict(load_balancer)
            self.log(results, pretty_print=True)
            update_tags, load_balancer_props['tags'] = self.update_tags(results['tags'])
            if update_tags:
                changed = True
            # Check difference with current status
            # Check frontend ip configurations: subnet_id, name, public_ip_address, private_ip_address, private_ip_allocation_method.
            param_fronts = list_to_dict(self.frontend_ip_configs, 'name')
            results_fronts = list_to_dict(results['frontend_ip_configurations'], 'name')
            for front in param_fronts.keys():
                results_fronts[front].update(azureid_to_dict(results_fronts[front]['subnet']['id']))
                if param_fronts[front].get('public_ip_name') and param_fronts[front]['public_ip_name'] != results_fronts[front]['public_ip_address']:
                    raise DiffErr('Load balancer {0} frontend {1} parameter public_ip_name differs: {2} vs {3}'.format(
                        self.name, front, param_fronts[front]['public_ip_name'], results_fronts[front]['public_ip_address']))
                if param_fronts[front].get('private_ip_address'):
                    if param_fronts[front]['private_ip_address'] != results_fronts[front]['private_ip_address'] or \
                       results_fronts[front]['private_ip_allocation_method'] != 'Static':
                        raise DiffErr('Load balancer {0} frontend {1} parameter private_ip_address differs: {2} vs {3}'.format(
                            self.name, front, param_fronts[front]['private_ip_address'], results_fronts[front]['private_ip_address']))
                else:
                    if results_fronts[front]['private_ip_allocation_method'] != 'Dynamic':
                        raise DiffErr('Load balancer {0} frontend {1} differs. None private ip means dynamic!'.format(self.name, front))
                if param_fronts[front].get('subnet_name') and param_fronts[front]['subnet_name'] != results_fronts[front]['subnets']:
                    raise DiffErr('Load balancer {0} frontend {1} parameter subnet_name differs: {2} vs {3}'.format(
                        self.name, front, param_fronts[front]['subnet_name'], results_fronts[front]['subnets']))
                if param_fronts[front].get('vnet_name') and param_fronts[front]['vnet_name'] != results_fronts[front]['virtualNetworks']:
                    raise DiffErr('Load balancer {0} frontend {1} parameter vnet_name differs: {2} vs {3}'.format(
                        self.name, front, param_fronts[front]['vnet_name'], results_fronts[front]['virtualNetworks']))
                if param_fronts[front].get('resource_group') and param_fronts[front]['resource_group'] != results_fronts[front]['resourceGroups']:
                    raise DiffErr('Load balancer {0} frontend {1} parameter resource_group differs: {2} vs {3}'.format(
                        self.name, front, param_fronts[front]['resource_group'], results_fronts[front]['resourceGroups']))
            # Check backend address pool configuration: name only, which will be used by NIC module
            if self.backend_pools:
                results_backs = list_to_dict(results['backend_address_pools'], 'name').keys()
                results_backs.sort()
                self.backend_pools.sort()
                if results_backs[0] != self.backend_pools[0]:
                    raise DiffErr('Load balancer {0} backend name list differs!'.format(self.name))

            # Check probe configurations: port, protocol, interval, number of probes, request_path, name
            param_probes = list_to_dict(self.health_probes, 'name')
            results_probes = list_to_dict(results['probes'], 'name')
            for probe in param_probes.keys():
                if param_probes[probe].get('port') and param_probes[probe]['port'] != results_probes[probe]['port']:
                    raise DiffErr('Load balancer {0} probe {1} parameter port differs: {2} vs {3}'.format(
                        self.name, probe, param_probes[probe]['port'], results_probes[probe]['port']))
                if param_probes[probe].get('protocol') and param_probes[probe]['protocol'] != results_probes[probe]['protocol']:
                    raise DiffErr('Load balancer {0} probe {1} parameter protocal differs: {2} vs {3}'.format(
                        self.name, probe, param_probes[probe]['protocol'], results_probes[probe]['protocol']))
                if param_probes[probe].get('interval') and param_probes[probe]['interval'] != results_probes[probe]['interval_in_seconds']:
                    raise DiffErr('Load balancer {0} probe {1} parameter interval differs: {2} vs {3}'.format(
                        self.name, probe, param_probes[probe]['interval'], results_probes[probe]['interval_in_seconds']))
                if param_probes[probe].get('fail_count') and param_probes[probe]['fail_count'] != results_probes[probe]['number_of_probes']:
                    raise DiffErr('Load balancer {0} probe {1} fail_count differs: {2} vs {3}'.format(
                        self.name, probe, param_probes[probe]['fail_count'], results_probes[probe]['number_of_probes']))
                if param_probes[probe].get('protocol') == 'Http' and param_probes[probe].get('request_path') and \
                   param_probes[probe]['request_path'] != results_probes[probe]['request_path']:
                    raise DiffErr('Load balancer {0} probe {1} requst_path differs: {2} vs {3}'.format(
                        self.name, probe, param_probes[probe]['request_path'], results_probes['request_path']))
            # Check load balancing rule configurations: protocol, distribution, frontend port, backend port, idle, name
            param_rules = list_to_dict(self.load_balancing_rules, 'name')
            results_rules = list_to_dict(results['load_balancing_rules'], 'name')
            for rule in param_rules.keys():
                results_rules[rule].update(azureid_to_dict(results_rules[rule]['frontend_ip_configuration_id']))
                results_rules[rule].update(azureid_to_dict(results_rules[rule]['probe_id']))
                results_rules[rule].update(azureid_to_dict(results_rules[rule]['backend_address_pool_id']))
                if param_rules[rule].get('frontend_name') and param_rules[rule]['frontend_name'] != results_rules[rule]['frontendIPConfigurations']:
                    raise DiffErr('Load balancer {0} rule {1} frontend_name differs: {2} vs {3}!'.format(
                        self.name, rule, param_rules[rule]['frontend_name'], results_rules[rule]['frontendIPConfigurations']))
                if param_rules[rule].get('backend_name') and param_rules[rule]['backend_name'] != results_rules[rule]['backendAddressPools']:
                    raise DiffErr('Load balancer {0} rule {1} backend_name differs: {2} vs {3}!'.format(
                        self.name, rule, param_rules[rule]['backend_name'], results_rules[rule]['backendAddressPools']))
                if param_rules[rule].get('probe_name') and param_rules[rule]['probe_name'] != results_rules[rule]['probes']:
                    raise DiffErr('Load balancer {0} rule {1} probe_name differs: {2} vs {3}!'.format(
                        self.name, rule, param_rules[rule]['probe_name'], results_rules[rule]['probes']))
                if param_rules[rule].get('protocol') and param_rules[rule]['protocol'] != results_rules[rule]['protocol']:
                    raise DiffErr('Load balancer {0} rule {1} protocol differs: {2} vs {3}!'.format(
                        self.name, rule, param_rules[rule]['protocol'], results_rules[rule]['protocol']))
                if param_rules[rule].get('load_distribution') and param_rules[rule]['load_distribution'] != results_rules[rule]['load_distribution']:
                    raise DiffErr('Load balancer {0} rule {1} load_distribution differs: {2} vs {3}!'.format(
                        self.name, rule, param_rules[rule]['load_distribution'], results_rules[rule]['load_distribution']))
                if param_rules[rule].get('frontend_port') and param_rules[rule]['frontend_port'] != results_rules[rule]['frontend_port']:
                    raise DiffErr('Load balancer {0} rule {1} frontend_port differs: {2} vs {3}!'.format(
                        self.name, rule, param_rules[rule]['frontend_port'], results_rules[rule]['frontend_port']))
                if param_rules[rule].get('backend_port') and param_rules[rule]['backend_port'] != results_rules[rule]['backend_port']:
                    raise DiffErr('Load balancer {0} rule {1} backend_port differs: {2} vs {3}!'.format(
                        self.name, rule, param_rules[rule]['backend_port'], results_rules[rule]['backend_port']))
                if param_rules[rule].get('idle_timeout') and param_rules[rule]['idle_timeout'] != results_rules[rule]['idle_timeout_in_minutes']:
                    raise DiffErr('Load balancer {0} rule {1} idle_timeout differs: {2} vs {3}!'.format(
                        self.name, rule, param_rules[rule]['idle_timeout'], results_rules[rule]['idle_timeout_in_minutes']))
                if param_rules[rule].get('enable_floating_ip') and param_rules[rule]['enable_floating_ip'] != results_rules[rule]['enable_floating_ip']:
                    raise DiffErr('Load balancer {0} rule {1} enable_floating_ip differs: {2} vs {3}!'.format(
                        self.name, rule, param_rules[rule]['enable_floating_ip'], results_rules[rule]['enable_floating_ip']))
            # Check inbound nat rule:
            param_nats = list_to_dict(self.inbound_nat_rules, 'name')
            results_nats = list_to_dict(results['inbound_nat_rules'], 'name')
            for nat in param_nats:
                results_nats[nat].update(azureid_to_dict(results_nats[nat]['frontend_ip_configuration_id']))
                if param_nats[nat].get('protocol') and param_nats[nat]['protocol'] != results_nats[nat]['protocol']:
                    raise DiffErr('Load balancer {0} NAT {1} protocol differs: {2} vs {3}!'.format(
                        self.name, nat, param_nats[nat]['protocol'], results_nats[nat]['protocol']))
                if param_nats[nat].get('frontend_port') and param_nats[nat]['frontend_port'] != results_nats[nat]['frontend_port']:
                    raise DiffErr('Load balancer {0} NAT {1} frontend_port differs: {2} vs {3}!'.format(
                        self.name, nat, param_nats[nat]['frontend_port'], results_nats[nat]['frontend_port']))
                if param_nats[nat].get('backend_port') and param_nats[nat]['backend_port'] != results_nats[nat]['backend_port']:
                    raise DiffErr('Load balancer {0} NAT {1} backend_port differs: {2} vs {3}!'.format(
                        self.name, nat, param_nats[nat]['backend_port'], results_nats[nat]['backend_port']))
                if param_nats[nat].get('frontend_name') and param_nats[nat]['frontend_name'] != results_nats[nat]['frontendIPConfigurations']:
                    raise DiffErr('Load balancer {0} NAT {1} frontend_name differs: {2} vs {3}!'.format(
                        self.name, nat, param_nats[nat]['frontend_name'], results_nats[nat]['frontendIPConfigurations']))
                if param_nats[nat].get('idle_timeout') and param_nats[nat]['idle_timeout'] != results_nats[nat]['idle_timeout_in_minutes']:
                    raise DiffErr('Load balancer {0} NAT {1} idle_timeout differs: {2} vs {3}!'.format(
                        self.name, nat, param_nats[nat]['idle_timeout'], results_nats[nat]['idle_timeout_in_minutes']))
                # DUE TO SDK LIBRARY ERROR, enable_floating_ip is not checked.
                # if param_nats[nat].get('enable_floating_ip') and param_nats[nat]['enable_floating_ip'] != results_nats[nat]['enable_floating_point_ip']:
                #     raise DiffErr('Load balancer {0} NAT {1} enable_floating_ip differs: {2} vs {3}!'.format(
                #        self.name, nat, param_nats[nat]['enable_floating_ip'], results_nats[nat]['enable_floating_point_ip']))

        except (IndexError, KeyError, DiffErr) as e:
            self.log('CHANGED: {0}'.format(e))
            changed = True
        except CloudError:
            self.log('CHANGED: load balancer {0} does not exist but requested status \'present\''.format(self.name))
            changed = True

        if not changed or self.check_mode:
            self.results['changed'] = changed
            self.results['state'] = results
            return self.results

        # From now changed==True
        if self.tags:
            load_balancer_props['tags'] = self.tags

        if self.frontend_ip_configs:
            load_balancer_props['frontend_ip_configurations'] = []
            for front in self.frontend_ip_configs:
                if front.get('public_ip_name'):
                    pip = self.get_public_ip_address(front['public_ip_name'])
                    load_balancer_props['frontend_ip_configurations'].append(FrontendIPConfiguration(
                        name=front['name'],
                        public_ip_address=pip
                    ))
                elif front.get('vnet_name') and front.get('subnet_name'):
                    if front.get('private_ip_address'):
                        load_balancer_props['frontend_ip_configurations'].append(FrontendIPConfiguration(
                            name=front['name'],
                            private_ip_address=front['private_ip_address'],
                            private_ip_allocation_method='Static',
                            subnet=get_subnet(self, front['resource_group'], front['vnet_name'], front['subnet_name'])
                        ))
                    else:
                        load_balancer_props['frontend_ip_configurations'].append(FrontendIPConfiguration(
                            name=front['name'],
                            private_ip_allocation_method='Dynamic',
                            subnet=get_subnet(self, front['resource_group'], front['vnet_name'], front['subnet_name'])
                        ))

        if self.backend_pools:
            load_balancer_props['backend_address_pools'] = []
            for backend in self.backend_pools:
                load_balancer_props['backend_address_pools'].append(BackendAddressPool(name=backend))
        if self.health_probes:
            load_balancer_props['probes'] = []
            for probe in self.health_probes:
                if probe['protocol'] == 'Http':
                    load_balancer_props['probes'].append(Probe(
                        name=probe['name'],
                        protocol=probe['protocol'],
                        port=probe['port'],
                        interval_in_seconds=probe['interval'],
                        number_of_probes=probe['fail_count'],
                        request_path=probe['request_path']
                    ))
                else:
                    load_balancer_props['probes'].append(Probe(
                        name=probe['name'],
                        protocol=probe['protocol'],
                        port=probe['port'],
                        interval_in_seconds=probe['interval'],
                        number_of_probes=probe['fail_count']
                    ))

        if self.load_balancing_rules:
            load_balancer_props['load_balancing_rules'] = []
            for rule in self.load_balancing_rules:
                frontend_ip_config_id = frontend_ip_configuration_id(
                    subscription_id=self.subscription_id,
                    resource_group_name=self.resource_group,
                    load_balancer_name=self.name,
                    name=rule['frontend_name']
                )
                backend_addr_pool_id = backend_address_pool_id(
                    subscription_id=self.subscription_id,
                    resource_group_name=self.resource_group,
                    load_balancer_name=self.name,
                    name=rule['backend_name']
                )
                prb_id = probe_id(
                    subscription_id=self.subscription_id,
                    resource_group_name=self.resource_group,
                    load_balancer_name=self.name,
                    name=rule['probe_name']
                )
                load_balancer_props['load_balancing_rules'].append(LoadBalancingRule(
                    name=rule['name'],
                    frontend_ip_configuration=SubResource(id=frontend_ip_config_id),
                    backend_address_pool=SubResource(id=backend_addr_pool_id),
                    probe=SubResource(id=prb_id),
                    protocol=rule['protocol'],
                    load_distribution=rule['load_distribution'],
                    frontend_port=rule['frontend_port'],
                    backend_port=rule['backend_port'],
                    idle_timeout_in_minutes=rule['idle_timeout'],
                    enable_floating_ip=rule['enable_floating_ip']
                ))

        if self.inbound_nat_rules:
            load_balancer_props['inbound_nat_rules'] = []
            for nat in self.inbound_nat_rules:
                frontend_ip_config_id = frontend_ip_configuration_id(
                    subscription_id=self.subscription_id,
                    resource_group_name=self.resource_group,
                    load_balancer_name=self.name,
                    name=nat['frontend_name']
                )
                load_balancer_props['inbound_nat_rules'].append(InboundNatRule(
                    name=nat['name'],
                    frontend_ip_configuration=SubResource(id=frontend_ip_config_id),
                    frontend_port=nat['frontend_port'],
                    backend_port=nat['backend_port'],
                    protocol=nat['protocol'],
                    enable_floating_ip=nat['enable_floating_ip'],
                    idle_timeout_in_minutes=nat['idle_timeout']
                ))

        self.results['changed'] = changed
        self.results['state'] = load_balancer_to_dict(LoadBalancer(**load_balancer_props))

        try:
            self.network_client.load_balancers.create_or_update(
                resource_group_name=self.resource_group,
                load_balancer_name=self.name,
                parameters=LoadBalancer(**load_balancer_props)
            ).wait()
        except CloudError as err:
            self.fail('Error creating load balancer {0}'.format(err))

        return self.results

    def get_public_ip_address(self, name):
        """Get a reference to the public ip address resource"""

        self.log('Fetching public ip address {0}'.format(name))
        try:
            public_ip = self.network_client.public_ip_addresses.get(self.resource_group, name)
        except CloudError as err:
            self.fail('Error fetching public ip address {0} - {1}'.format(name, str(err)))
        return public_ip


def load_balancer_to_dict(load_balancer):
    """Seralialize a LoadBalancer object to a dict"""

    result = dict(
        id=load_balancer.id,
        name=load_balancer.name,
        location=load_balancer.location,
        tags=load_balancer.tags,
        provisioning_state=load_balancer.provisioning_state,
        etag=load_balancer.etag,
        frontend_ip_configurations=[],
        backend_address_pools=[],
        load_balancing_rules=[],
        probes=[],
        inbound_nat_rules=[],
        inbound_nat_pools=[],
        outbound_nat_rules=[]
    )

    if load_balancer.frontend_ip_configurations:
        result['frontend_ip_configurations'] = [dict(
            id=_.id,
            name=_.name,
            etag=_.etag,
            provisioning_state=_.provisioning_state,
            private_ip_address=_.private_ip_address,
            private_ip_allocation_method=_.private_ip_allocation_method,
            subnet=dict(
                id=_.subnet.id,
                name=_.subnet.name,
                address_prefix=_.subnet.address_prefix
            ) if _.subnet else None,
            public_ip_address=dict(
                id=_.public_ip_address.id,
                location=_.public_ip_address.location,
                public_ip_allocation_method=_.public_ip_address.public_ip_allocation_method,
                ip_address=_.public_ip_address.ip_address
            ) if _.public_ip_address else None
        ) for _ in load_balancer.frontend_ip_configurations]

    if load_balancer.backend_address_pools:
        result['backend_address_pools'] = [dict(
            id=_.id,
            name=_.name,
            provisioning_state=_.provisioning_state,
            etag=_.etag
        ) for _ in load_balancer.backend_address_pools]

    if load_balancer.load_balancing_rules:
        result['load_balancing_rules'] = [dict(
            id=_.id,
            name=_.name,
            protocol=_.protocol,
            frontend_ip_configuration_id=_.frontend_ip_configuration.id,
            backend_address_pool_id=_.backend_address_pool.id,
            probe_id=_.probe.id,
            load_distribution=_.load_distribution,
            frontend_port=_.frontend_port,
            backend_port=_.backend_port,
            idle_timeout_in_minutes=_.idle_timeout_in_minutes,
            enable_floating_ip=_.enable_floating_ip,
            provisioning_state=_.provisioning_state,
            etag=_.etag
        ) for _ in load_balancer.load_balancing_rules]

    if load_balancer.probes:
        result['probes'] = [dict(
            id=_.id,
            name=_.name,
            protocol=_.protocol,
            port=_.port,
            interval_in_seconds=_.interval_in_seconds,
            number_of_probes=_.number_of_probes,
            request_path=_.request_path,
            provisioning_state=_.provisioning_state
        ) for _ in load_balancer.probes]

    if load_balancer.inbound_nat_rules:
        result['inbound_nat_rules'] = [dict(
            id=_.id,
            name=_.name,
            frontend_ip_configuration_id=_.frontend_ip_configuration.id,
            protocol=_.protocol,
            frontend_port=_.frontend_port,
            backend_port=_.backend_port,
            idle_timeout_in_minutes=_.idle_timeout_in_minutes,
            enable_floating_point_ip=_.enable_floating_point_ip if hasattr(_, 'enable_floating_point_ip') else None,
            provisioning_state=_.provisioning_state,
            etag=_.etag
        ) for _ in load_balancer.inbound_nat_rules]

    if load_balancer.inbound_nat_pools:
        result['inbound_nat_pools'] = [dict(
            id=_.id,
            name=_.name,
            frontend_ip_configuration_id=_.frontend_ip_configuration.id,
            protocol=_.protocol,
            frontend_port_range_start=_.frontend_port_range_start,
            frontend_port_range_end=_.frontend_port_range_end,
            backend_port=_.backend_port,
            provisioning_state=_.provisioning_state,
            etag=_.etag
        ) for _ in load_balancer.inbound_nat_pools]

    if load_balancer.outbound_nat_rules:
        result['outbound_nat_rules'] = [dict(
            id=_.id,
            name=_.name,
            allocated_outbound_ports=_.allocated_outbound_ports,
            frontend_ip_configuration_id=_.frontend_ip_configuration.id,
            backend_address_pool=_.backend_address_pool.id,
            provisioning_state=_.provisioning_state,
            etag=_.etag
        ) for _ in load_balancer.outbound_nat_rules]

    return result


def frontend_ip_configuration_id(subscription_id, resource_group_name, load_balancer_name, name):
    """Generate the id for a frontend ip configuration"""
    return '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Network/loadBalancers/{2}/frontendIPConfigurations/{3}'.format(
        subscription_id,
        resource_group_name,
        load_balancer_name,
        name
    )


def backend_address_pool_id(subscription_id, resource_group_name, load_balancer_name, name):
    """Generate the id for a backend address pool"""
    return '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Network/loadBalancers/{2}/backendAddressPools/{3}'.format(
        subscription_id,
        resource_group_name,
        load_balancer_name,
        name
    )


def probe_id(subscription_id, resource_group_name, load_balancer_name, name):
    """Generate the id for a probe"""
    return '/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Network/loadBalancers/{2}/probes/{3}'.format(
        subscription_id,
        resource_group_name,
        load_balancer_name,
        name
    )


def get_subnet(self, resource_group, vnet_name, subnet_name):
    self.log("Fetching subnet {0} in virtual network {1}".format(subnet_name, vnet_name))
    try:
        subnet = self.network_client.subnets.get(resource_group, vnet_name, subnet_name)
    except Exception as exc:
        self.fail("Error: fetching subnet {0} in virtual network {1} - {2}".format(subnet_name, vnet_name, str(exc)))
    return subnet


def list_to_dict(listin, key):
    dictout = {}
    for l in listin:
        dictout[l[key]] = l
    return dictout


def azureid_to_dict(id):
    pieces = id.strip('/').split('/')
    result = {}
    index = 0
    while index < len(pieces) - 1:
        result[pieces[index]] = pieces[index + 1]
        index += 2
    return result


def main():
    """Main execution"""
    AzureRMLoadBalancer()

if __name__ == '__main__':
    main()
