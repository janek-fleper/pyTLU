import struct
import array

BITFILE_NAME = 0x61
BITFILE_PART = 0x62
BITFILE_DATE = 0x63
BITFILE_TIME = 0x64
BITFILE_IMAGE = 0x65

# convert array [AB, CD, ...]  to ABCD... (in hex)
def byteshift(array):
    shifted_sum = 0
    for i in range(len(array)):
        shifted_sum += array[i] * 2**(8 * (len(array) - 1 - i))

    return shifted_sum

# the length of the section is saved in len_bytes
def read_bitfile_section(f, len_bytes):
    length = [struct.unpack('B', f.read(1))[0] for i in range(len_bytes)]
    length = self.byteshift(length)
    return length, f.read(length)
    
# 16 bytes per row, similar to wireshark capture
def print_bitfile_to_file(bitfile, length):
    f_out = open('f_out.txt', 'w')
    for i in range(0, length, 16):
        if ((length - i) < 16):
            j_max = length - i
        else:
            j_max = 16
        for j in range(j_max):
            f_out.write('{:02X} '.format(bitfile[i + j]))
        f_out.write('\n')
    f_out.close()

# "while byte:" loops over the bitfile until the end is reached
# struct.unpack converts byte to a readable format
def open_bitfile(path_to_file):
    ret = {}

    with open(path_to_file, mode='rb') as f:
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

#        self.print_bitfile_to_file(ret['image'][1], ret['image'][0])
    
    return ret

# weird size modification, no idea why it is necessary
def modify_bitfile_image(bitfile):
    image_size = bitfile['image'][0]
    length = (image_size + 511 + 512)&~511

    bitarray = [0] * length
    for i in range(image_size):
        bitarray[i] = bitfile['image'][1][i]

    return bitarray, length
