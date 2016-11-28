import ZestSC1.main as zest

def main():
    bitfile = zest.open_bitfile('examples/Example1_1000.bit')
    bitarray = zest.modify_bitfile_image(bitfile)

    boards = zest.find_boards()
    boards[0].open_card()
#    boards[0].reset_8051()
    boards[0].load_bitarray_to_board(bitarray)
    boards[0].close_board()

if __name__ == '__main__':
    main()
