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
        firmware_version = self.duckypad_hid.write([5] + ([0] * 63))
        major, minor, patch = firmware_version[3:5]
        return {
            "model": self.duckypad_hid.get_product_string(),
            "serial": self.duckypad_hid.get_serial_number_string(),
            "fw_ver": f"{major}.{minor}.{patch}"
        }

    def read(self) -> list:
        read_start = time.time()
        while time.time() - read_start <= 0.5:
            result = self.duckypad_hid.read(DUCKYPAD_TO_PC_HID_BUF_SIZE)
            if len(result) > 0:
                return result
            time.sleep(0.01)
        return []

    def write(self, hid_buf_64b: list) -> Union[list, None]:
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