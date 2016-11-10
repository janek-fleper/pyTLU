import logging
import time
import sys
import os
import struct
from threading import Lock
from enum import Enum

import array
import numpy as np
import usb.core
import usb.util

from constants import *

# enable logging, from pyUSB tutorial
os.environ["PYUSB_DEBUG"] = "critical"
os.environ["PYUSB_LOG_FILENAME"] = "log/pyTLU.log"

class Board:
    def __init__(self, device=None):
        # device is not None if usb.core.find() does not find any boards
        self.dev = device

        device.set_configuration()

        self.lock = Lock()

    def read_eeprom(self, address):
        return self.dev.ctrl_transfer(EP_CTRL_READ, VR_READ_EEPROM,
                                        address, 0, 3)

    def get_card_id(self):
        return self.read_eeprom(EEPROM_CARDID_ADDRESS)[2]

    def get_fpga_type(self):
        return self.read_eeprom(EEPROM_FPGA_ADDRESS)[2]

    def get_serial_number(self):
        return np.array([self.read_eeprom(EEPROM_SERIAL_ADDRESS + i)[2]
                            for i in range(4)])

    def get_memory_size(self):
        return np.array([self.read_eeprom(EEPROM_MEMORY_SIZE_ADDRESS + i)[2]
                            for i in range(4)])

    def get_firmware_version(self):
        return np.array(self.dev.ctrl_transfer(EP_CTRL_READ,
                            VR_GET_FIRMWARE_VER, 0, 0, 3)[0:3:])

    def get_info(self):
        print('card_id: {}'.format(self.get_card_id()))
        print('fpga_type: {}'.format(self.get_fpga_type()))
        print('serial_number: {}'.format(self.get_serial_number()))
        print('memory_size: {}'.format(self.get_memory_size()))
        print('firmware_version: {}?'.format(self.get_firmware_version()))

    def reset_8051(self):
        ret = np.array([0, 0])
        ret[0] = self.dev.ctrl_transfer(EP_CTRL_WRITE, ANCHOR_LOAD_INTERNAL,
                CPUCS_REG_FX2, 0, [1])
        ret[1] = self.dev.ctrl_transfer(EP_CTRL_WRITE, ANCHOR_LOAD_INTERNAL,
                CPUCS_REG_FX2, 0, [0])
        print('reset_8051: {}'.format(ret))

    def byteshift(self, array):
        shifted_sum = 0
        for i in range(len(array)):
            shifted_sum += array[i] * 2**(8 * (len(array) - 1 - i))

        return shifted_sum

    # the length of the section is saved in len_bytes
    def read_bitfile_section(self, f, len_bytes):
        length = [struct.unpack('B', f.read(1))[0] for i in range(len_bytes)]
        length = self.byteshift(length)
        return length, f.read(length)

    def open_bitfile(self):
        ret = {}

        with open('bitfiles/Example1_1000.bit', mode='rb') as f:
            byte = f.read(1)
            while byte:
                value = struct.unpack('B', byte)[0]

                if value == BITFILE_NAME:
                    ret['name'] = self.read_bitfile_section(f, 2)
                if value == BITFILE_PART:
                    ret['part'] = self.read_bitfile_section(f, 2)
                if value == BITFILE_DATE:
                    ret['date'] = self.read_bitfile_section(f, 2)
                if value is BITFILE_TIME:
                    ret['time'] = self.read_bitfile_section(f, 2)
                if value is BITFILE_IMAGE:
                    ret['image'] = self.read_bitfile_section(f, 4)

                byte = f.read(1)

        return ret

    def transfer_bitstream_at_once(self, bitstream):
        print('bulk_write: {}'.format(
            self.dev.write(EP_CONFIG_WRITE, bitstream[0:], timeout=10000)))

    def transfer_bitstream_in_parts(self, bitstream):
        pos = int(0)
        print('len(bitstream) = {}'.format(len(bitstream)))
        while pos < len(bitstream):
            next_pos = pos + int(MAX_TRANSFER_LENGTH)
            print('bulk_write: {}'.format(self.dev.write(EP_CONFIG_WRITE,
                    bitstream[pos:next_pos], timeout=1000)))
            pos = next_pos
            print('pos = {}'.format(pos))

    def load_bitfile_to_board(self):
        self.reset_8051()

        bitfile = self.open_bitfile()
        bitstream = array.array('B', bitfile['image'][1])

        # both variants seem to work, not really sure what that measn
        print('vr_start_config: {}'.format(self.dev.ctrl_transfer(
            EP_CTRL_READ, VR_START_CONFIG, 6, 10240, 2, timeout=1000)))
            #EP_CTRL_READ, VR_START_CONFIG, 4096, 4096, 2)))

        self.transfer_bitstream_at_once(bitstream)
        #self.transfer_bitstream_in_parts(bitstream)

        print('vr_config_status: {}'.format(self.dev.ctrl_transfer( \
                            EP_CTRL_READ, VR_CONFIG_STATUS, 0, 0, 3, \
                            timeout=1000)))


    def close_board(self):
        print('clear fpga: {}'.format(self.dev.ctrl_transfer(
            EP_CTRL_READ, VR_START_CONFIG, 4096, 4096, 2)))

        self.reset_8051()

def find_boards():
    # devs is not None if no boards are found
    # dev is None, use find_all=False
    devs = usb.core.find(find_all=True, idVendor=VENDOR_ID,
                            idProduct=PRODUCT_ID)

    return [Board(device=dev) for dev in devs]

def main():
    boards = find_boards()
    boards[0].load_bitfile_to_board()
#    boards[0].close_board()

if __name__ == '__main__':
    main()
