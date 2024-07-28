import csv
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from ..common import CAPINFOS_BINARY

class _Capinfos_field_types:
    int_keys = {'Number of packets', 'File size (bytes)', 'Data size (bytes)'}
    float_keys = {
        'Capture duration (seconds)',
        'Data byte rate (bytes/sec)', 'Data bit rate (bits/sec)',
        'Average packet size (bytes)',
        'Average packet rate (packets/sec)'
    }
    datetime_keys = {'Start time', 'End time'}


class Capinfos_processor:

    @staticmethod
    def _convert_capinfos_value(key, value) -> int | float | datetime | str:
        if key in _Capinfos_field_types.int_keys:
            return int(value)
        elif key in _Capinfos_field_types.float_keys:
            return float(value)
        elif key in _Capinfos_field_types.datetime_keys:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
        else:
            return value

    @staticmethod
    def get_all_capinfos(pcap_file_path):
        command = [CAPINFOS_BINARY, "-ATMmQ", pcap_file_path]
        try:
            capinfos_csv = subprocess.run(command,
                capture_output=True, text=True, encoding='utf-8'
            ).stdout.strip()
            return capinfos_csv
        except subprocess.CalledProcessError as e:
            print(f"Error running capinfos: {e}")
            return ""

    @staticmethod
    def parse_capinfos_csv_to_dict(capinfos_csv):
        reader = csv.reader(capinfos_csv, dialect='unix')
        reader_lists = list(reader)[::2]
        columns_count = len(reader_lists) // 2
        pcap_stats = {}
        for k, v in zip(reader_lists[:columns_count],
                        reader_lists[columns_count:]):
            key = k[0]
            value = v[0]
            pcap_stats[key] = Capinfos_processor._convert_capinfos_value(key, value)
        return pcap_stats


@dataclass
class Pcapinfo:
    file_name: str = None
    file_type: str = None
    file_encapsulation: str = None
    file_time_precision: str = None
    packet_size_limit: str = None
    packet_size_limit_min__inferred: str = None
    packet_size_limit_max__inferred: str = None
    number_of_packets: int = None
    file_size__in_bytes: int = None
    data_size__in_bytes: int = None
    capture_duration__in_seconds: float = None
    start_time: datetime = None
    end_time: datetime = None
    data_byte_rate__in_bytes_per_sec: float = None
    data_bit_rate__in_bits_per_sec: float = None
    average_packet_size__in_bytes: float = None
    average_packet_rate__in_packets_per_sec: float = None
    sha256: str = None
    sha1: str = None
    strict_time_order: str = None
    capture_hardware: str = None
    capture_opersys: str = None
    capture_application: str = None
    capture_comment: str = None

    @classmethod
    def from_pcap_file(cls, pcap_file_path):
        capinfos_csv = Capinfos_processor.get_all_capinfos(pcap_file_path)
        pcap_stats = Capinfos_processor.parse_capinfos_csv_to_dict(capinfos_csv).values()
        return cls(*pcap_stats)

    @classmethod
    def from_csv(cls, csv_obj):
        data = Capinfos_processor.parse_capinfos_csv_to_dict(csv_obj).values()
        return cls(*data)

    @classmethod
    def from_json(cls, json_obj):
        data = json.loads(json_obj)

        if 'Start time' in data and data['Start time']:
            data['Start time'] = datetime.strptime(data['Start time'], '%Y-%m-%d %H:%M:%S.%f')
        if 'End time' in data and data['End time']:
            data['End time'] = datetime.strptime(data['End time'], '%Y-%m-%d %H:%M:%S.%f')

        return cls(
            file_name=data.get('File name'),
            file_type=data.get('File type'),
            file_encapsulation=data.get('File encapsulation'),
            file_time_precision=data.get('File time precision'),
            packet_size_limit=data.get('Packet size limit'),
            packet_size_limit_min__inferred=data.get('Packet size limit min (inferred)'),
            packet_size_limit_max__inferred=data.get('Packet size limit max (inferred)'),
            number_of_packets=data.get('Number of packets'),
            file_size__in_bytes=data.get('File size (bytes)'),
            data_size__in_bytes=data.get('Data size (bytes)'),
            capture_duration__in_seconds=data.get('Capture duration (seconds)'),
            start_time=data.get('Start time'),
            end_time=data.get('End time'),
            data_byte_rate__in_bytes_per_sec=data.get('Data byte rate (bytes/sec)'),
            data_bit_rate__in_bits_per_sec=data.get('Data bit rate (bits/sec)'),
            average_packet_size__in_bytes=data.get('Average packet size (bytes)'),
            average_packet_rate__in_packets_per_sec=data.get('Average packet rate (packets/sec)'),
            sha256=data.get('SHA256'),
            sha1=data.get('SHA1'),
            strict_time_order=data.get('Strict time order'),
            capture_hardware=data.get('Capture hardware'),
            capture_opersys=data.get('Capture oper-sys'),
            capture_application=data.get('Capture application'),
            capture_comment=data.get('Capture comment')
        )

    def to_dict(self):
        capinfos_dict = {
            'File name': self.file_name,
            'File type': self.file_type,
            'File encapsulation': self.file_encapsulation,
            'File time precision': self.file_time_precision,
            'Packet size limit': self.packet_size_limit,
            'Packet size limit min (inferred)': self.packet_size_limit_min__inferred,
            'Packet size limit max (inferred)': self.packet_size_limit_max__inferred,
            'Number of packets': self.number_of_packets,
            'File size (bytes)': self.file_size__in_bytes,
            'Data size (bytes)': self.data_size__in_bytes,
            'Capture duration (seconds)': self.capture_duration__in_seconds,
            'Start time': self.start_time.__str__(),
            'End time': self.end_time.__str__(),
            'Data byte rate (bytes/sec)': self.data_byte_rate__in_bytes_per_sec,
            'Data bit rate (bits/sec)': self.data_bit_rate__in_bits_per_sec,
            'Average packet size (bytes)': self.average_packet_size__in_bytes,
            'Average packet rate (packets/sec)': self.average_packet_rate__in_packets_per_sec,
            'SHA256': self.sha256,
            'SHA1': self.sha1,
            'Strict time order': self.strict_time_order,
            'Capture hardware': self.capture_hardware,
            'Capture oper-sys': self.capture_opersys,
            'Capture application': self.capture_application,
            'Capture comment': self.capture_comment,
        }
        return capinfos_dict

    def to_csv(self, out_file=None):
        #TODO implement
        pass

    def to_json(self, out_file=None):
        if out_file:
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False)
        else:
            return json.dumps(self.to_dict(), ensure_ascii=False)
