# duckyPad HID Command Protocols

[Get duckyPad](https://duckypad.com) | [Official Discord](https://discord.gg/4sJCBx5)

------------

This article describes duckyPad HID command protocols, and how it can be used to control duckyPad from your PC.

## HID Basics

duckyPad enumerates as 4 HID devices:

* Keyboard

* Mouse

* Keypad with Media Keys

* Counted Buffer

The first three is controlled by duckyScript, while the last one is used for two-way communication between duckyPad and PC.

------

duckyPad has the following HID properties:

**Vendor ID**: 0x0483 (1155)

**Product ID**

* **duckyPad (2020)**: 0xd11c (53532) 

* **duckyPad Pro (2024)**: 0xd11d (53533) 

The `Counted Buffer` device has the usage ID of 0x3a (58).

------

The HID command buffer is **64 Bytes**, meaning you must send a fixed 64B packet to duckyPad, and will receive a fixed 64B response.

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

### Write to duckyPad

Try [this script](hid_example/ex1_open.py) to open duckyPad HID device and write a 64-byte packet asking it to change to the next profile.

### Read from duckyPad

Finally, try [this script](hid_example/ex2_read_write.py) to send duckyPad a command, AND receive its response.

You can use it as the starting point of your own program!

### Using Bash (Linux only)

[This script](hid_example/ex3_bash.sh) talks to duckyPad with shell utils without Python.

## HID Packet Structure

### PC-to-duckyPad

duckyPad expects a **fixed 64-byte** packet from PC:

|   Byte#  |         Description        |
|:--------:|:--------------------------:|
|     0    | HID Usage ID (always 0x05) |
|     1    |       Reserved      |
|     2    |        Command Type      |
| 3 ... 63 |          Payload          |

### duckyPad-to-PC

duckyPad will reply with a **fixed 64-byte** response:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    HID Usage ID (always 0x04)    |
|     1    |          Reserved         |
|     2    | Status<br>0 = SUCCESS<br>1 = ERROR<br>2 = BUSY||
| 3 ... 63 |             Payload             |

* `BUSY` is returned if duckyPad is executing a script, or in a menu.

## HID Commands

### Query Info (0x00)

💬 PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Reserved |
|     2    |        0x00        |
| 3 ... 63 |        0x00        |

💬 duckyPad to PC:

|  Byte# |           Description          |
|:------:|:------------------------------:|
|    0   |              0x04              |
|    1   |         Reserved        |
|    2   |0 = SUCCESS|
|    3   |     Firmware version Major     |
|    4   |     Firmware version Minor     |
|    5   |     Firmware version Patch     |
|    6   |     Hardware revision<br>20 = duckyPad<br>24 = duckyPad Pro     |
| 7 - 10 | Serial number (unsigned 32bit) |
|   11   |     Current profile number     |
|   12   |     is_sleeping  |
| 13-63  |              0x00                 |

-----------

### Goto Profile by **NUMBER** (0x01)

💬 PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Reserved |
|     2    |        0x01        |
|     3    |   Profile number<br>(**1-indexed**)    |
| 4 ... 63 |        0x00        |

💬 duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Reserved         |
|     2    | Status, 0 = SUCCESS |
| 3 ... 63 |             0x00             |

-----------

### Goto Profile by **NAME** (0x17 / 23)

💬 PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Reserved |
|     2    |        0x17        |
|     3 ... 63    |   Profile Name String<br>**Case Sensitive**<br>Zero terminated  |

💬 duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Reserved         |
|     2    | Status, 0 = SUCCESS |
| 3 ... 63 |             0x00             |

-----------

### Previous Profile (0x02)

💬 PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Reserved |
|     2    |        0x02        |
| 3 ... 63 |        0x00        |

💬 duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Reserved         |
|     2    | Status, 0 = SUCCESS |
| 3 ... 63 |             0x00             |


-----------

### Next Profile (0x03)

💬 PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Reserved |
|     2    |        0x03        |
| 3 ... 63 |        0x00        |

💬 duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Reserved         |
|     2    | Status, 0 = SUCCESS |
| 3 ... 63 |             0x00             |

-----------

### Set RGB Colour: Single (0x04)

Change color of a single LED.

* PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Reserved |
|     2    |        0x04        |
|     3    |LED index, 0 to 19  |
|     4    |Red  |
|     5    |Green  |
|     6    |Blue  |
| 7 ... 63 |        0x00        |

-----------



### Software reset (0x14 / 20)

Perform a software reset.

💬 PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Reserved |
|     2    |        0x14        |
|     3    |        Reboot options<br>0 = Normal<br>1 = Reboot into USB MSC mode  |
| 3 ... 63 | 0x00 |

💬 duckyPad to PC:

Nothing, because it's rebooting!

**Wait at least 5 seconds** before trying to talk to it again.

-----------

### Sleep (0x15 / 21)

Make duckyPad go to sleep.

Screen and RGB LEDs are turned off.

💬 PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Reserved |
|     2    |        0x15        |
| 3 ... 63 | 0x00 |

💬 duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Reserved         |
|     2    | Status, 0 = SUCCESS |
| 3 ... 63 | 0x00 |

-----------

### Wake up (0x16 / 22)

Wake up from sleep

💬 PC to duckyPad:

|   Byte#  |   Description   |
|:--------:|:---------------:|
|     0    |        0x05        |
|     1    | Reserved |
|     2    |        0x16        |
| 3 ... 63 | 0x00 |

💬 duckyPad to PC:

|   Byte#  |            Description           |
|:--------:|:--------------------------------:|
|     0    |    0x04    |
|     1    |          Reserved         |
|     2    | Status, 0 = SUCCESS |
| 3 ... 63 | 0x00 |

----------

### ⚠️⚠️⚠️ Commands Below are duckyPad (2020) ONLY ⚠️⚠️⚠️

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

## Questions or Comments?

Please feel free to [open an issue](https://github.com/dekuNukem/duckypad/issues), ask in the [official duckyPad discord](https://discord.gg/4sJCBx5), DM me on discord `dekuNukem#6998`, or email `dekuNukem`@`gmail`.`com` for inquires.
