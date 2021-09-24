import logging
import time
from typing import Dict, Union

import hid

PC_TO_DUCKYPAD_HID_BUF_SIZE = 64
DUCKYPAD_TO_PC_HID_BUF_SIZE = 32

DUCKYPAD_VENDOR_ID = 0x0483
DUCKYPAD_PRODUCT_ID = 0xD11C
DUCKYPAD_USAGE = 0x3A

class DuckyPad:

    def __init__(self):
        self.duckypad_hid = hid.device()
        self.is_open = False

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def open(self) -> None:
        duckypad_path = self.get_path()

        if not duckypad_path:
            raise OSError('duckyPad not connected')

        self.duckypad_hid.open_path(duckypad_path)
        self.duckypad_hid.set_nonblocking(1)
        self.is_open = True

    def close(self) -> None:
        self.duckypad_hid.close()
        self.is_open = False

    @staticmethod
    def get_path() -> Union[str, None]:
        logging.info("Getting duckyPad path:")
        for device_dict in hid.enumerate(
            vendor_id=DUCKYPAD_VENDOR_ID, product_id=DUCKYPAD_PRODUCT_ID
        ):
            # logging.info(device_dict))
            if device_dict["usage"] == DUCKYPAD_USAGE:
                return device_dict["path"]
        return None

    def get_info(self) -> Dict[str, str]:
        buffer = [0] * 64
        buffer[0] = 5
        firmware_version = self.write(buffer)
        major, minor, patch = firmware_version[3:6]
        return {
            "model": self.duckypad_hid.get_product_string(),
            "serial": self.duckypad_hid.get_serial_number_string(),
            "fw_ver": f"{major}.{minor}.{patch}"
        }

    def read(self) -> list:
        try:
            return self.duckypad_hid.read(DUCKYPAD_TO_PC_HID_BUF_SIZE, timeout_ms=500)
        except Exception:
            return []

    def write(self, hid_buf_64b: list) -> Union[int, None]:
        if len(hid_buf_64b) != PC_TO_DUCKYPAD_HID_BUF_SIZE:
            raise ValueError("PC-to-duckyPad buffer wrong size, should be exactly 64 Bytes")
            
        result = None

        try:
            self.duckypad_hid.write(hid_buf_64b)
        except Exception as error:
            raise OSError("duckyPad write error") from error
        
        try:
            result = self.read()
        except Exception as error:
            raise OSError("Error reading back result of a write")

        return result

    def previous_profile(self) -> None:
        buffer = [0] * 64
        buffer[0] = 5
        buffer[2] = 2
        self.write(buffer)

    def next_profile(self) -> None:
        buffer = [0] * 64
        buffer[0] = 5
        buffer[2] = 3
        self.write(buffer)
    
    def goto_profile(self, profile_number: int) -> None:
        buffer = [0] * 64
        buffer[0] = 5
        buffer[2] = 1
        buffer[3] = profile_number
        self.write(buffer)