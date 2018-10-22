# -*- coding: utf-8 -*-

import os
from bluepy import btle


def rebootGateway():
    os.system('reboot')


def onBluetooth():
    os.system('hciconfig hci0 up')


def offBluetooth():
    os.system('hciconfig hci0 down')


def scan_for_devices():
    """
    Scan for bluetooth low energy devices.
    """
    scanner = btle.Scanner()
    result = []
    scan_data = []
    addr_list = []
    temp_dict = {}

    #BLE device scan
    for device in scanner.scan():
        scan_data.append(device.scanData)
        addr_list.append(device.addr)

    #scanEntry 가공
    for i in range(len(scan_data)):
        if 9 in scan_data[i]:
            temp_dict = {'addr':addr_list[i], 'name':scan_data[i][9].decode('utf-8')}
        else:
            temp_dict = {'addr':addr_list[i], 'name':'no name'}
        result.append(temp_dict)
    print(result)

    return result
