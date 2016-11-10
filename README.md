#Python driver for TLU FPGA

The bitfile to be loaded onto the board can be found in the folder bitfiles. The bitfile is supposed to switch on a LED if loaded succesfully.

The file constants.py holds all the endpoints, requests, and eeprom addresses necessary to operate the board.

The bitstream, read from the bitfile, is correctly loaded onto the board, atleast according to the length returned from usb.core.write(). Upon reading the config status from the board, line 130 in main.py, pyUSB returns an error:
```bash
Traceback (most recent call last):
  File "main.py", line 155, in <module>
    main()
  File "main.py", line 151, in main
    boards[0].load_bitfile_to_board()
  File "main.py", line 132, in load_bitfile_to_board
    timeout=1000)))
  File "/usr/lib/python3.5/site-packages/usb/core.py", line 1043, in ctrl_transfer
    self.__get_timeout(timeout))
  File "/usr/lib/python3.5/site-packages/usb/backend/libusb1.py", line 883, in ctrl_transfer
    timeout))
  File "/usr/lib/python3.5/site-packages/usb/backend/libusb1.py", line 595, in _check
    raise USBError(_strerror(ret), ret, _libusb_errno[ret])
usb.core.USBError: [Errno 110] Operation timed out
```
