import sys
import os

import array
import numpy as np
import usb.core
import usb.util
import usb.backend.libusb1

from tlu.constants import *

class Board:
# device is not None if usb.core.find() does not find any boards
    def __init__(self, device=None):
        self.dev = device

        device.set_configuration()

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
#        print('reset_8051: {}'.format(ret))

# Not certain if it is really necessary. According to the original driver
# one should send a 4096 byte dummy configuration if the first configuration
# fails. Default should be to use reset_8051() instead of open_card().
    def open_card(self):
        self.reset_8051()

        ret = self.dev.ctrl_transfer(EP_CTRL_READ, VR_START_CONFIG, 
                wValue=4096, wIndex=4096,
                data_or_wLength=array.array('B', [0, 0]), timeout=1000)
#        print('ctrl_transfer: {}'.format(ret))

        Buffer = np.full(4096, 0, dtype=np.uint16)
        Buffer = array.array('B', Buffer)

        ret = self.dev.write(EP_CONFIG_WRITE, Buffer, timeout=1000)
#        print('bulk_write: {}'.format(ret))

        self.reset_8051()

    def load_bitarray_to_board(self, bitarray):
        self.reset_8051()

        length = len(bitarray)
#        bitfile = self.open_bitfile()
#        bitarray, length = self.modify_bitfile_image(bitfile)

        wValue = (length>>16)&0xffff
        wIndex = length&0xffff
        ret = self.dev.ctrl_transfer(EP_CTRL_READ, VR_START_CONFIG, 
                wValue=wValue, wIndex=wIndex,
                data_or_wLength=array.array('B', [0, 0]), timeout=1000)
#        print('ctrl_transfer: {}'.format(ret))

        ret = self.dev.write(EP_CONFIG_WRITE, bitarray, timeout=1000)
#        print('bulk_write: {}'.format(ret))

        ret = self.dev.ctrl_transfer(EP_CTRL_READ, VR_CONFIG_STATUS, 
                wValue=0, wIndex=0,
                data_or_wLength=array.array('B', [0, 0, 0]), timeout=1000)
#        print('ctrl_transfer: {}'.format(ret))

    def close_board(self):
        ret = self.dev.ctrl_transfer(EP_CTRL_READ, VR_START_CONFIG, 
                wValue=4096, wIndex=4096,
                data_or_wLength=array.array('B', [0, 0]), timeout=1000)
#        print('ctrl_transfer: {}'.format(ret))

        self.reset_8051()


# find_all=True: devs is not None if no boards are found, so it's pointless to
# check if any boards were found
# find_all=False: dev is None if no board is found
# the usb backend can be changed if required
def find_boards():
#    backend = usb.backend.libusb1.get_backend(find_library=lambda x:
#                                               "/usr/lib/libusb-1.0.so")
#    devs = usb.core.find(find_all=True, idVendor=VENDOR_ID,
#                            idProduct=PRODUCT_ID, backend=backend)

    devs = usb.core.find(find_all=True, idVendor=VENDOR_ID,
                            idProduct=PRODUCT_ID)

    return [Board(device=dev) for dev in devs]

#def main():
#    boards = find_boards()
#    boards[0].open_card()
#    boards[0].reset_8051()
#    boards[0].load_bitfile_to_board()
#    boards[0].close_board()
#
#if __name__ == '__main__':
#    main()
