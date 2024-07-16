from ipaddress import ip_network, ip_address

def is_ip_address(item: str) -> bool:
    try: ip_address(item); return True
    except: return False

def is_ip_network(item: str, strict: bool = False) -> bool:
    if not strict:
        try: ip_network(item); return True
        except: return False
    else:
        if is_ip_network(item) and not is_ip_address(item):
            return True
        else:
            return False
