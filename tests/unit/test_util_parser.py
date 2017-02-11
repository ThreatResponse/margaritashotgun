import pytest
import os
import sys

from margaritashotgun.util import parser

@pytest.fixture
def tcp_parser_object():
    return parser.ProcNetTcpParser()

def test_split_every_n():
    tcp_parser = tcp_parser_object()
    test_input = '0F02000A'
    expected_output = ['0F', '02', '00', '0A']

    output = tcp_parser._ProcNetTcpParser__split_every_n(2, test_input)
    assert output == expected_output

def test_decode_address():
    tcp_parser = tcp_parser_object()
    test_input = '0F02000A:0016'
    expected_output = "10.0.2.15:22"

    output = tcp_parser._ProcNetTcpParser__decode_address(test_input)
    assert output == expected_output

def test_decode_connection():
    tcp_parser = tcp_parser_object()
    test_input = {'uid': '15379', 'tm->when': '0', 'tr': '00000000',
                  'timeout': '1', 'st': '0A', 'tx_queue': '00000000:00000000',
                  'rem_address': '00000000:0000', 'sl': '0:',
                  'local_address': '00000000:0016', 'rx_queue': '00:00000000',
                  'retrnsmt': '0', 'inode': 'ffff880000114000'}
    expected_output = ('0.0.0.0:22', '0.0.0.0:0')
    output = tcp_parser._ProcNetTcpParser__decode_connection(test_input)
    assert output == expected_output

def test_parse():
    tcp_parser = tcp_parser_object()
    test_input = '''  sl  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode                                                     
   0: 00000000:0016 00000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 15379 1 ffff880000114000 100 0 0 10 0                     
   1: 0100007F:0019 00000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 16012 1 ffff880000114f00 100 0 0 10 0                     
   2: 0F02000A:0016 0202000A:995E 01 00000000:00000000 02:000B04B8 00000000     0        0 24037 4 ffff880000114780 20 4 27 10 -1'''
    expected_output = [('0.0.0.0:22', '0.0.0.0:0'), ('127.0.0.1:25', '0.0.0.0:0')]
    output = tcp_parser.parse(test_input)
    assert output == expected_output
