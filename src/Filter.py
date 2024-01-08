# Not implemented yet.
'''
The purpose of this class is to provide methods for creating capture/preview filters for tcpdump/wireshark.
For exmaple:

-- tcpdump/tshark capture filter:
'not ((src host 1.1.1.1 and src udp port 443) or (dst host 1.1.1.1 and dst udp port 443))'

-- tshark/wireshark preview filter:
'not ((ip.src == 1.1.1.1 and udp.srcport == 443) or (ip.dst == 1.1.1.1 and udp.dstport == 443))'
'''

purposes = ('capture', 'preview')
directions = ('src', 'dst')

class Filter:

    @staticmethod
    def construct_endpoint_filter(
            purpose, proto=None, addr=None, port=None
    ) -> str:
        if purpose not in purposes:
            raise ValueError(f"Invalid purpose: {purpose}")

        if purpose == 'capture':
            expression = f'''not ({" or ".join(
                [f"({direction} host {addr} and {proto} {direction} port {port})"
                 for direction in directions]
            )})'''
        elif purpose == 'preview':
            expression = f'''not ({" or ".join(
                [f"(ip.{direction} == {addr} and {proto}.{direction}port == {port})"
                 for direction in directions]
            )})'''
        else:
            expression = ''

        return expression
