#from ..tlu import *
import tlu
import tlu.main
import tlu.bitfile
import tlu.main as tlu
import tlu.bitfile as bf

def main():
    bitfile = bf.open_bitfile('examples/Example1_1000.bit')
    bitarray = bf.modify_bitfile_image(bitfile)

    boards = tlu.find_boards()
    boards[0].reset_8051()
    boards[0].load_bitarray_to_board(bitarray)
    boards[0].close_board()

if __name__ == '__main__':
    main()
