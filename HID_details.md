# duckyPad HID Command Protocols

[Get duckyPad](https://www.tindie.com/products/21984/) | [Official Discord](https://discord.gg/4sJCBx5) | [Project Main Page](https://github.com/dekuNukem/duckyPad)

This article describes duckyPad HID command protocols, and how it can be used to control duckyPad from your PC.

## HID Basics

After firmware 0.18.0, duckyPad will enumerate as 4 HID devices:

* Keyboard

* Mouse

* Keypad with Media Keys

* Counted Buffer

The first three is controlled by duckyScript, while the last one is used for two-way communication between duckyPad and PC.

------

duckyPad has the following HID properties:

**Vendor ID**: 0x0483 (1155)

**Product ID**: 0xd11c (53532)

The `Counted Buffer` device has the usage ID of 0x3a (58).

------

The HID command buffer from **PC to duckyPad** is **64 Bytes**, meaning you must send a fixed 64B packet to duckyPad.

The HID command buffer from **duckyPad to PC** is also **64 Bytes**, meaning duckyPad will reply with a fixed 64B response.

## HID Examples

I used [`cython-hidapi`](https://github.com/trezor/cython-hidapi) Python library for HID communication. You can install it with `pip3 install hidapi`.

A couple of [example scripts](hid_example) are provided.

### List HID Devices

First off, try [this script](hid_example/ex0_list.py) to list all available HID devices.

duckyPad should look something like this:

```
manufacturer_string : dekuNukem
path : b'\\\\?\\hid#vid_0483&pid_d11c&col04#8&3a0783ae&0&0003#{4d1e55b2-f16f-11cf-88cb-001111000030}'
product_id : 53532
product_string : duckyPad(2020)
release_number : 512
serial_number : DP20_78426107
usage : 58
usage_page : 1
vendor_id : 1155
```

### Writing to duckyPad

Try [this script](hid_example/ex1_open.py) to open duckyPad HID device and write a 64-byte packet asking it to change to the next profile.

Details about the protocols are discussed in the next section.

### Reading from duckyPad

Finally, try [this script](hid_example/ex2_read_write.py) to send duckyPad a command, AND receive its response.

You can use it as the starting point of your own program!

### Using from a shell script (Linux only)

You can take a look at [this script](hid_example/ex3_bash.sh) for a way how you can communicate with duckyPad using standard shell utils on Linux. This can be useful to users running systems where python cannot be easily installed.

## HID Packet Layout

### PC-to-duckyPad

As mentioned before, duckyPad expects a **fixed 64-byte** packet from PC:


|   Byte#  |         Description        |
|:--------:|:--------------------------:|
|     0    | HID Usage ID (always 0x05) |
|     1    |       Sequence number      |
|     2    |        Command type        |
| 3 ... 63 |          Payloads          |

* Byte 0 is always 0x05

* Byte 1 is sequence number, can be anything from 0 to 255.

* Byte 2 is command type, [introduced below](#hid-commands).

* The rest of the buffer is **payload**, set to 0 for unused portion.

### duckyPad-to-PC

Once received a packet from PC, duckyPad will reply with a **fixed 64-byte** response:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    HID Usage ID (always 0x04)    |
|     1    |          Sequence number         |
|     2    | Status. 0 = SUCCESS, 1 = ERROR. 2 = BUSY |
| 3 ... 63 |             Payloads             |

* Byte 0 is always 0x04

* Byte 1 is the **same** sequence number from PC's command. Can be used to track missed packets.

* Byte 2 is status, can be SUCCESS, ERROR, or BUSY. The latter is returned if duckyPad is executing a script, or in a menu.

* The rest of the buffer is **payload**, will be 0 if unused.

## HID Commands

### Info (0x00)

If command type is 0x00, duckyPad will return its device information.

* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x00        |
| 3 ... 63 |        0x00        |

* duckyPad to PC:

|  Byte# |           Description          |
|:------:|:------------------------------:|
|    0   |              0x04              |
|    1   |         Sequence number        |
|    2   |                0x00               |
|    3   |     Firmware version Major     |
|    4   |     Firmware version Minor     |
|    5   |     Firmware version Patch     |
| 7 - 10 | Serial number (unsigned 32bit) |
|   11   |     Current profile number     |
| 12-63  |              0x00                 |

### Goto Profile (0x01)

If command type is 0x01, duckyPad will jump to a particular profile.

* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x01        |
|     3    |   Profile number to jump to        |
| 4 ... 63 |        0x00        |

* duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Sequence number         |
|     2    | 0 = SUCCESS, 1 = ERROR, 2 = BUSY |
| 3 ... 63 |             0x00             |

### Previous Profile (0x02)

If command type is 0x02, duckyPad will go to the previous profile.

* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x02        |
| 3 ... 63 |        0x00        |

* duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Sequence number         |
|     2    | 0 = SUCCESS, 1 = ERROR, 2 = BUSY |
| 3 ... 63 |             0x00             |


### Next Profile (0x03)

If command type is 0x03, duckyPad will go to the next profile.

* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x03        |
| 3 ... 63 |        0x00        |

* duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Sequence number         |
|     2    | 0 = SUCCESS, 1 = ERROR, 2 = BUSY |
| 3 ... 63 |             0x00             |

### Reload Current Profile (0x04)

To be implemented...

### Change RGB LED Colour (0x05)

To be implemented...

### Print Text (0x06)

To be implemented...

### Print Bitmap (0x07)

To be implemented...

### Clear Screen (0x08)

To be implemented...

### Update Screen (0x09)

To be implemented...

### List files (0x0a)

If command type is 0x0a, duckyPad will start listing the files and directories on the SD card. Names are ASCII-encoded.

* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x0a        |
| 3 ... 63 | relative path (ASCII-encoded) or 0x00 for root-dir listing |

* duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Sequence number         |
|     2    | 0 = SUCCESS, 1 = ERROR, 2 = BUSY, 3 = EOF |
| 3 ... 63 | file or directory name (ASCII-encoded) |

As each byte is only 64 bytes the following entry must be requested via Resume operation (0x0c). End of listing is indicated by EOF (0x03) while data chunk contains NULL bytes.

### Read file (0x0b)

If command type is 0x0b, duckyPad will read and return its content.


* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x0a        |
| 3 ... 63 | relative path to file (ASCII-encoded) |

* duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Sequence number         |
|     2    | 0 = SUCCESS, 1 = ERROR, 2 = BUSY, 3 = EOF |
| 3 ... 62 | 60B chunk of data |
| 63       | 0x00 |

Only 60 bytes of data are returned per each call thus next chunk must be requested via Resume operation (0x0c). End of file is indicated by EOF (0x03) while data chunk contains NULL bytes.

### Resume operation (0x0c)

If command type is 0x0c, duckyPad will - depending on the previous operation - either get another chunk of data (read file) or retrieve another line of file/dir listing (list files).


* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x0c        |
| 3 ... 63 | 0x00 |

* duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Sequence number         |
|     2    | 0 = SUCCESS, 1 = ERROR, 2 = BUSY |
| 3 ... 62 | data chunk / file or directory name  |
| 63       | 0x00 |

Only 60 bytes of data are returned per each call. This call should be repeated until byte[2] equals EOF (0x03) which indicates end of output.

### Abort operation (0x0d)

TODO

### Open file for writing (0x0e)

If command type is 0x0e, duckyPad will open a specified filename in write-mode. This is a required operation before the actual write command is called.

* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x0e        |
| 3 ... 63 | path to file (ASCII, path components are separated using '/') |

* duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Sequence number         |
|     2    | 0 = SUCCESS, 1 = ERROR, 2 = BUSY |
| 3 ... 63 | 0x00 |

### Write to file (0x0f)

If command type is 0x0f, duckyPad will write 60 bytes of data in payload to a file previously opened by "Open file for writing" command. Repeated call results in payload being appended. In order to finish the transfer, file must be closed.

* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x0f        |
| 3 ... 62 | data to be written |
|     63   |        0x00        |


* duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Sequence number         |
|     2    | 0 = SUCCESS, 1 = ERROR, 2 = BUSY |
| 3 ... 63 | 0x00 |

### Close file (0x10)

If command type is 0x10, duckyPad will close currently opened (in write mode) file.

* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x10        |
| 3 ... 63 | 0x00 |


* duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Sequence number         |
|     2    | 0 = SUCCESS, 1 = ERROR, 2 = BUSY |
| 3 ... 63 | 0x00 |

### Delete file (0x11)

If command type is 0x11, duckyPad will delete file name specified in the payload.

* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x11        |
| 3 ... 63 | relative path to a file (ASCII, path components are separated using '/') |

* duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Sequence number         |
|     2    | 0 = SUCCESS, 1 = ERROR, 2 = BUSY |
| 3 ... 63 | 0x00 |

### Create dir (0x12)

If command type is 0x12, duckyPad will create a directory with name specified in the payload.

* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x12        |
| 3 ... 63 | relative path to a directory (ASCII, path components are separated using '/') |

* duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Sequence number         |
|     2    | 0 = SUCCESS, 1 = ERROR, 2 = BUSY |
| 3 ... 63 | 0x00 |

### Delete dir (0x13)

If command type is 0x13, duckyPad will create a directory with name specified in the payload.

* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x13        |
| 3 ... 63 | relative path to a directory (ASCII, path components are separated using '/') |

* duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Sequence number         |
|     2    | 0 = SUCCESS, 1 = ERROR, 2 = BUSY |
| 3 ... 63 | 0x00 |

### Software reset (0x14)

If command type is 0x13, duckyPad will reset.

* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Sequence number |
|     2    |        0x14        |
| 3 ... 63 | 0x00 |

* duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Sequence number         |
|     2    | 0 = SUCCESS, 1 = ERROR, 2 = BUSY |
| 3 ... 63 | 0x00 |

## Questions or Comments?

Please feel free to [open an issue](https://github.com/dekuNukem/duckypad/issues), ask in the [official duckyPad discord](https://discord.gg/4sJCBx5), DM me on discord `dekuNukem#6998`, or email `dekuNukem`@`gmail`.`com` for inquires.
