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

Finally, try [this script](hid_example/ex1_open.py) to send duckyPad a command, AND receive its response.

You can use it as the starting point of your own program!

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

## Questions or Comments?

Please feel free to [open an issue](https://github.com/dekuNukem/duckypad/issues), ask in the [official duckyPad discord](https://discord.gg/4sJCBx5), DM me on discord `dekuNukem#6998`, or email `dekuNukem`@`gmail`.`com` for inquires.
