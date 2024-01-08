# #TODO: validate IP-related input with built-in types
# from ipaddress import ip_address, IPv4Address, IPv6Address, IPv4Network, IPv6Network

purposes = ('capture', 'preview')
directions = ('src', 'dst')
filter_goals = ('exclude', 'include')

class Filter:

    @staticmethod
    def construct_endpoint_filter(
            purpose, proto=None, addr=None, port=None, filter_goal='exclude'
    ) -> str:

        #TODO: maybe we can come up with a better naming?
        if purpose not in purposes:
            raise ValueError(
                f"Invalid purpose: {purpose}\n"
                f"Choose one of {', '.join(purposes)}"
            )
        if filter_goal not in filter_goals:
            raise ValueError(
                f"Invalid filter_goal: {filter_goal}\n"
                f"Choose one of {', '.join(filter_goals)}"
            )

        inclusion_prefix = 'not ' if filter_goal == 'exclude' else ''

        if purpose == 'capture':
            packet_envelope = [
                f"""({direction} {
                    'host'
                    if len(addr.split('/')) == 1
                    else 'net'
                } {addr} and {proto} {direction} port {port})"""
                for direction in directions
            ]
        elif purpose == 'preview':
            packet_envelope = [
                f"(ip.{direction} == {addr} and {proto}.{direction}port == {port})"
                for direction in directions
            ]

        expression = f'{inclusion_prefix}({" or ".join(packet_envelope)})'

        return expression

    @staticmethod
    def tcpdump_endpoint_filter(**kwargs) -> str:
        return Filter.construct_endpoint_filter(purpose='capture', **kwargs)

    @staticmethod
    def wireshark_endpoint_filter(**kwargs) -> str:
        return Filter.construct_endpoint_filter(purpose='preview', **kwargs)
