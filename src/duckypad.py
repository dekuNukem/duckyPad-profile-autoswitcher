from typing import Dict, List, Optional

import hid

PC_TO_DUCKYPAD_HID_BUF_SIZE = 64
DUCKYPAD_TO_PC_HID_BUF_SIZE = 32

DUCKYPAD_VENDOR_ID = 0x0483
DUCKYPAD_PRODUCT_ID = 0xD11C
DUCKYPAD_USAGE = 0x3A


class DuckyPad:
    """
    HID connection wrapper for duckyPad.

    Handles opening and closing of HID connections, and provides
    a high-level API over PC-to-DuckyPad communication.

    Designed to be used as a context manager that wraps opening
    and closing connections. E.g.:

    ```
    with DuckyPad() as duckypad:
        duckypad.previous_profile()
    ```
    """

    def __init__(self):
        self.duckypad_hid = hid.device()
        self.is_open = False
        self.has_been_closed = False

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def open(self) -> None:
        """
        Opens a HID connection to duckyPad.

        Cannot be called if this instance has been `.close`d before.
        """

        # Don't allow opening more than once
        # https://github.com/trezor/cython-hidapi/issues/4
        if self.has_been_closed:
            raise IOError(
                "Cannot open the DuckyPad HID device twice. "
                "Instantiate a new DuckyPad object instead"
            )

        duckypad_path = self.get_path()

        if not duckypad_path:
            raise OSError("duckyPad not connected")

        self.duckypad_hid.open_path(duckypad_path)
        self.duckypad_hid.set_nonblocking(1)
        self.is_open = True

    def close(self) -> None:
        """
        Closes this instance's HID connection to duckyPad.
        """

        self.duckypad_hid.close()
        self.is_open = False
        self.has_been_closed = True

    @staticmethod
    def get_path() -> Optional[str]:
        """
        Returns the HID path of the first duckyPad that can be found, or
        `None` if duckyPad cannot be found.
        """

        for device_dict in hid.enumerate(
            vendor_id=DUCKYPAD_VENDOR_ID, product_id=DUCKYPAD_PRODUCT_ID
        ):
            if device_dict["usage"] == DUCKYPAD_USAGE:
                return device_dict["path"]
        return None

    def get_info(self) -> Dict[str, str]:
        """
        Gets metadata about the connected duckyPad.
        """

        buffer = [0] * 64
        buffer[0] = 5
        firmware_version = self.write(buffer)
        major, minor, patch = firmware_version[3:6]
        return {
            "model": self.duckypad_hid.get_product_string(),
            "serial": self.duckypad_hid.get_serial_number_string(),
            "fw_ver": f"{major}.{minor}.{patch}",
        }

    def read(self) -> list:
        """
        Attempts to read a response from the duckyPad HID connection.
        """

        try:
            return self.duckypad_hid.read(DUCKYPAD_TO_PC_HID_BUF_SIZE, timeout_ms=500)
        except Exception:
            return []

    def write(self, hid_buf_64b: List[int]) -> List[int]:
        """
        Writes a given list of 64 bytes (as `int`s) to the duckyPad HID
        device.

        Returns the Duckypad's response as an array of 32 `int`s.

        See the following links for information on the packet format and
        commands:

        - https://github.com/dekuNukem/duckyPad-profile-autoswitcher/blob/master/HID_details.md#hid-packet-layout
        - https://github.com/dekuNukem/duckyPad-profile-autoswitcher/blob/master/HID_details.md#hid-commands
        """

        if len(hid_buf_64b) != PC_TO_DUCKYPAD_HID_BUF_SIZE:
            raise ValueError(
                "PC-to-duckyPad buffer wrong size, should be exactly 64 Bytes"
            )

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
        """
        Switches duckyPad to the next profile.
        """

        buffer = [0] * 64
        buffer[0] = 5
        buffer[2] = 2
        self.write(buffer)

    def next_profile(self) -> None:
        """
        Switches duckyPad to the next profile.
        """

        buffer = [0] * 64
        buffer[0] = 5
        buffer[2] = 3
        self.write(buffer)

    def goto_profile(self, profile_number: int) -> None:
        """
        Set's duckyPad's current profile to the given profile number.

        `profile_number` must be an `int` within the interval (1,32)
        """
        buffer = [0] * 64
        buffer[0] = 5
        buffer[2] = 1
        buffer[3] = profile_number
        self.write(buffer)
