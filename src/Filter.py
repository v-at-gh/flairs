'''
The purpose of this class is to provide methods to construct capture/preview filters for tcpdump/wireshark.

'''

class Filter:

    @staticmethod
    def return_capture_filter(
        iface=None,
        process=None,
        destination=None,
        proto=None
    ):
        capture_filter = ''
        return capture_filter

    @staticmethod
    def return_preview_filter():
        preview_filter = ''
        return preview_filter
