import subprocess
from subprocess import CompletedProcess
from typing import Literal, LiteralString, Union
from functools import partial
from ipaddress import IPv4Network, IPv6Network, ip_network


def execute_command(command_str, dry_run) -> Union[LiteralString, CompletedProcess[bytes]]:
    command_arr = [arg.strip() for arg in command_str.split()]
    if dry_run: return ' '.join(command_arr)
    result = subprocess.run(command_arr, capture_output=True)
    return result

MODE   = Literal['on',  'off']
PROTO  = Literal['tcp', 'udp']
FAMILY = Literal[4, 6]

class Firewalld:

    EXE_PATH = 'firewall-cmd'

    @staticmethod
    def toggle_port(switch: MODE,
            protocol: PROTO, port: int,
            permanent: bool = False,
            quiet:     bool = True,
            dry_run:   bool = False
    ) -> Union[LiteralString, CompletedProcess[bytes]]:
        action = '--add-port' if switch == 'on' else '--remove-port'
        command_str = (
            f"{Firewalld.EXE_PATH} {'-q' if quiet else ''}"
            f" {'--permanent' if permanent else ''}"
            f" {action}={port}/{protocol}"
        )
        return execute_command(command_str, dry_run)
    add_port           = partial(toggle_port, switch='on')
    remove_port        = partial(toggle_port, switch='off')
    add_port_as_str    = partial(add_port,    dry_run=True)
    remove_port_as_str = partial(remove_port, dry_run=True)

    @staticmethod
    def toggle_source_in_trusted_zone(switch: MODE,
            network:   Union[IPv4Network, IPv6Network],
            permanent: bool = False,
            quiet:     bool = True,
            dry_run:   bool = False
    ) -> Union[LiteralString, CompletedProcess[bytes]]:
        try: network = ip_network(network)
        except Exception as e: raise e
        if   switch == 'on':  action = '--add-source'
        elif switch == 'off': action = '--remove-source'
        command_str = (
            f"{Firewalld.EXE_PATH} {'-q' if quiet else ''}"
            f" {'--permanent' if permanent else ''}"
            f" --zone=trusted {action}={network}"
        )
        return execute_command(command_str, dry_run)
    add_source_to_trusted_zone             = partial(toggle_source_in_trusted_zone, switch='on')
    remove_source_from_trusted_zone        = partial(toggle_source_in_trusted_zone, switch='off')
    add_source_to_trusted_zone_as_str      = partial(toggle_source_in_trusted_zone, switch='on', dry_run=True)
    remove_source_from_trusted_zone_as_str = partial(toggle_source_in_trusted_zone, switch='off', dry_run=True)

    @staticmethod
    def toggle_nat_masquerade_rule(switch: MODE,
            network:   Union[IPv4Network, IPv6Network],
            permanent: bool = False,
            quiet:     bool = True,
            dry_run:   bool = False
    ) -> Union[LiteralString, CompletedProcess[bytes]]:
        try: network = ip_network(network)
        except Exception as e: raise e
        if   isinstance(network, IPv4Network): family = 'ipv4'
        elif isinstance(network, IPv6Network): family = 'ipv6'
        else: raise ValueError("How did we get here?!")
        if   switch == 'on':  action = '--add-rule'
        elif switch == 'off': action = '--remove-rule'
        command_str = (
            f"{Firewalld.EXE_PATH} {'-q' if quiet else ''}"
            f" {'--permanent' if permanent else ''}"
            f" --direct {action} {family} nat POSTROUTING 0"
            f" -s {network} ! -d {network} -j MASQUERADE"
        )
        return execute_command(command_str, dry_run)
    add_nat_masquerade_rule           = partial(toggle_nat_masquerade_rule, switch='on')
    remove_nat_masquerade_rule        = partial(toggle_nat_masquerade_rule, switch='off')
    add_nat_masquerade_rule_as_str    = partial(toggle_nat_masquerade_rule, switch='on', dry_run=True)
    remove_nat_masquerade_rule_as_str = partial(toggle_nat_masquerade_rule, switch='off', dry_run=True)

    @staticmethod
    def construct_commands_to_add_rules(
            proto, port, network_v4, network_v6, permanent=True
    ):
        commands_list = [
            Firewalld.add_port_as_str(protocol=proto, port=port),
        ]
        if permanent:
            commands_list.append(
                Firewalld.add_port_as_str(protocol=proto, port=port, permanent=True)
            )
        commands_list_ipv4 = [
            Firewalld.add_source_to_trusted_zone_as_str(network=network_v4),
            Firewalld.add_nat_masquerade_rule_as_str(network=network_v4),
        ]
        if permanent:
            commands_list_ipv4.extend([
                Firewalld.add_source_to_trusted_zone_as_str(network=network_v4, permanent=True),
                Firewalld.add_nat_masquerade_rule_as_str(network=network_v4, permanent=True)
            ])
        if network_v6:
            commands_list_ipv6 = [
                Firewalld.add_source_to_trusted_zone_as_str(network=network_v6),
                Firewalld.add_nat_masquerade_rule_as_str(network=network_v6)
            ]
            if permanent:
                commands_list_ipv6.extend([
                    Firewalld.add_source_to_trusted_zone_as_str(network=network_v6, permanent=True),
                    Firewalld.add_nat_masquerade_rule_as_str(network=network_v6, permanent=True)
                ])
            commands_list.extend(commands_list_ipv4 + commands_list_ipv6)
        else:
            commands_list.extend(commands_list_ipv4)
        return '\n'.join(command for command in commands_list)

    @staticmethod
    def construct_commands_to_remove_rules(
            proto, port, network_v4, network_v6, permanent=True
    ):
        commands_list = [
            Firewalld.remove_port_as_str(protocol=proto, port=port),
            Firewalld.remove_port_as_str(protocol=proto, port=port, permanent=True)
        ]
        commands_list_ipv4 = [
            Firewalld.remove_source_from_trusted_zone_as_str(network=network_v4),
            Firewalld.remove_source_from_trusted_zone_as_str(network=network_v4, permanent=True),
            Firewalld.remove_nat_masquerade_rule_as_str(network=network_v4),
            Firewalld.remove_nat_masquerade_rule_as_str(network=network_v4, permanent=True)
        ]
        commands_list_ipv6 = [
            Firewalld.remove_source_from_trusted_zone_as_str(network=network_v6),
            Firewalld.remove_source_from_trusted_zone_as_str(network=network_v6, permanent=True),
            Firewalld.remove_nat_masquerade_rule_as_str(network=network_v6),
            Firewalld.remove_nat_masquerade_rule_as_str(network=network_v6, permanent=True)
        ]
        commands_list.extend(commands_list_ipv4 + commands_list_ipv6)
        return '\n'.join(command for command in commands_list)


class IPTables:

    #TODO: implement a setter for constants,
    # and a function to find executables if run on VPN server
    V4_EXE_PATH = '/usr/sbin/iptables'
    V6_EXE_PATH = '/usr/sbin/ip6tables'

    @staticmethod
    def toggle_port(switch: MODE,
            protocol: PROTO, port: int,
            dry_run:  bool = False
    ) -> Union[LiteralString, CompletedProcess[bytes]]:
        action = '-I' if switch == 'on' else '-D'
        command_str = (
            f"{IPTables.V4_EXE_PATH} {action} INPUT"
            f" -p {protocol} --dport {port} -j ACCEPT"
        )
        return execute_command(command_str, dry_run)
    insert_port        = partial(toggle_port, switch='on')
    delete_port        = partial(toggle_port, switch='off')
    insert_port_as_str = partial(toggle_port, switch='on', dry_run=True)
    delete_port_as_str = partial(toggle_port, switch='off', dry_run=True)

    @staticmethod
    def toggle_nat_rule(switch: MODE,
            network:   Union[IPv4Network, IPv6Network],
            dry_run:   bool = False
    ) -> Union[LiteralString, CompletedProcess[bytes]]:
        try: network = ip_network(network)
        except Exception as e: raise e
        if   isinstance(network, IPv4Network): iptables_exe = IPTables.V4_EXE_PATH
        elif isinstance(network, IPv6Network): iptables_exe = IPTables.V6_EXE_PATH
        else: raise ValueError("How did we get here?!")
        if   switch == 'on':  action = '-A'
        elif switch == 'off': action = '-D'
        command_str = (
            f"{iptables_exe} -t nat {action} POSTROUTING"
            f" -s {network} ! -d {network} -j MASQUERADE"
        )
        return execute_command(command_str, dry_run)
    append_nat_rule        = partial(toggle_nat_rule, switch='on')
    delete_nat_rule        = partial(toggle_nat_rule, switch='off')
    append_nat_rule_as_str = partial(append_nat_rule, dry_run=True)
    delete_nat_rule_as_str = partial(delete_nat_rule, dry_run=True)

    @staticmethod
    def toggle_match_state_rule(switch: MODE,
            network:   Union[IPv4Network, IPv6Network],
            dry_run:   bool = False
    ) -> Union[LiteralString, CompletedProcess[bytes]]:
        try: network = ip_network(network)
        except Exception as e: raise e
        if   isinstance(network, IPv4Network): iptables_exe = IPTables.V4_EXE_PATH
        elif isinstance(network, IPv6Network): iptables_exe = IPTables.V6_EXE_PATH
        else: raise ValueError("How did we get here?!")
        if   switch == 'on':  action = '-I'
        elif switch == 'off': action = '-D'
        command_str = (
            f"{iptables_exe} {action} FORWARD -m state"
            " --state RELATED,ESTABLISHED -j ACCEPT"
        )
        return execute_command(command_str, dry_run)
    insert_match_state_rule        = partial(toggle_match_state_rule, switch='on')
    delete_match_state_rule        = partial(toggle_match_state_rule, switch='off')
    insert_match_state_rule_as_str = partial(toggle_match_state_rule, switch='on', dry_run=True)
    delete_match_state_rule_as_str = partial(toggle_match_state_rule, switch='off', dry_run=True)

    @staticmethod
    def toggle_fwd_src_rule(switch: MODE,
            network:   Union[IPv4Network, IPv6Network],
            dry_run:   bool = False
    ) -> Union[LiteralString, CompletedProcess[bytes]]:
        try: network = ip_network(network)
        except Exception as e: raise e
        if   isinstance(network, IPv4Network): iptables_exe = IPTables.V4_EXE_PATH
        elif isinstance(network, IPv6Network): iptables_exe = IPTables.V6_EXE_PATH
        else: raise ValueError("How did we get here?!")
        if   switch == 'on':  action = '-I'
        elif switch == 'off': action = '-D'
        command_str = (
            f"{iptables_exe} {action} FORWARD -s {network} -j ACCEPT"
        )
        return execute_command(command_str, dry_run)
    insert_fwd_src_rule        = partial(toggle_fwd_src_rule, switch='on')
    delete_fwd_src_rule        = partial(toggle_fwd_src_rule, switch='off')
    insert_fwd_src_rule_as_str = partial(toggle_fwd_src_rule, switch='on', dry_run=True)
    delete_fwd_src_rule_as_str = partial(toggle_fwd_src_rule, switch='off', dry_run=True)

    @staticmethod
    def construct_commands_to_add_rules(
            proto, port, network_v4, network_v6, permanent=True
    ):
        commands_list = [
            IPTables.insert_port_as_str(protocol=proto, port=port),
        ]
        commands_list_ipv4 = [
            IPTables.append_nat_rule_as_str(network=network_v4),
            IPTables.insert_match_state_rule_as_str(network=network_v4),
            IPTables.insert_fwd_src_rule_as_str(network=network_v4),
        ]
        if network_v6:
            commands_list_ipv6 = [
                IPTables.append_nat_rule_as_str(network=network_v6),
                IPTables.insert_match_state_rule_as_str(network=network_v6),
                IPTables.insert_fwd_src_rule_as_str(network=network_v6),
            ]
            commands_list.extend(commands_list_ipv4 + commands_list_ipv6)
        else:
            commands_list.extend(commands_list_ipv4)
        if permanent:
            return '\n'.join(f"ExecStart={command}" for command in commands_list)
        else:
            return '\n'.join(command for command in commands_list)

    @staticmethod
    def construct_commands_to_del_rules(
            proto, port, network_v4, network_v6, permanent=True
    ):
        commands_list = [
            IPTables.delete_port_as_str(protocol=proto, port=port),
        ]
        commands_list_ipv4 = [
            IPTables.delete_nat_rule_as_str(network=network_v4),
            IPTables.delete_match_state_rule_as_str(network=network_v4),
            IPTables.delete_fwd_src_rule_as_str(network=network_v4),
        ]
        if network_v6:
            commands_list_ipv6 = [
                IPTables.delete_nat_rule_as_str(network=network_v6),
                IPTables.delete_match_state_rule_as_str(network=network_v6),
                IPTables.delete_fwd_src_rule_as_str(network=network_v6),
            ]
            commands_list.extend(commands_list_ipv4 + commands_list_ipv6)
        else:
            commands_list.extend(commands_list_ipv4)
        if permanent:
            return '\n'.join(f"ExecStop={command}" for command in commands_list)
        else:
            return '\n'.join(command for command in commands_list)

    @staticmethod
    def construct_systemd_unit(
        proto, port, network_v4, network_v6
    ):
        unit_header = "[Unit]\nBefore=network.target\n[Service]\nType=oneshot"
        start_commands = IPTables.construct_commands_to_add_rules(proto, port, network_v4, network_v6, permanent=True)
        stop_commands  = IPTables.construct_commands_to_del_rules(proto, port, network_v4, network_v6, permanent=True)
        unit_footer = "RemainAfterExit=yes\n[Install]\nWantedBy=multi-user.target"
        unit = '\n'.join([unit_header, start_commands, stop_commands, unit_footer])
        return unit

default_parameters_wg = {
    'proto'     : 'udp',
    'port'      : 51820,
    'network_v4': '10.7.0.0/24',
    'network_v6': 'fddd:2c4:2c4:2c4::/64'
}

default_parameters_ovpn = {
    'proto'     : 'udp',
    'port'      : 1194,
    'network_v4': '10.8.0.0/24',
    'network_v6': 'fddd:1194:1194:1194::/64'
}

default_parameters_ovpn_tcp = {
    'proto'     : 'tcp',
    'port'      : 1194,
    'network_v4': '10.8.0.0/24',
    'network_v6': 'fddd:1194:1194:1194::/64'
}

print(Firewalld.construct_commands_to_add_rules(**default_parameters_wg))
