import hid
import time
import logging

PC_TO_DUCKYPAD_HID_BUF_SIZE = 64
DUCKYPAD_TO_PC_HID_BUF_SIZE = 32

h = hid.device()
is_hid_open = False

def duckypad_init():
    global h
    global is_hid_open
    logging.info("def duckypad_init():")
    h.close()
    duckypad_path = get_duckypad_path()
    if duckypad_path is None:
        return False
    h.open_path(duckypad_path)
    h.set_nonblocking(1)
    is_hid_open = True
    return True

def duckypad_get_info():
    logging.info("def duckypad_get_info():")
    global is_hid_open
    if is_hid_open is False:
        raise OSError('duckyPad not connected')
    dpinfo = {}
    dpinfo['model'] = h.get_product_string()
    dpinfo['serial'] = h.get_serial_number_string()
    buffff = [0] * 64
    buffff[0] = 5
    result = duckypad_hid_write(buffff)
    dpinfo['fw_ver'] = f'{result[3]}.{result[4]}.{result[5]}'
    return dpinfo

def duckypad_hid_close():
    h.close()

def get_duckypad_path():
    logging.info("def get_duckypad_path():")
    for device_dict in hid.enumerate():
        logging.info(str(device_dict))
        if device_dict['vendor_id'] == 0x0483 and device_dict['product_id'] == 0xd11c and device_dict['usage'] == 58:
            return device_dict['path']
        elif device_dict['vendor_id'] == 0x0483 and device_dict['product_id'] == 0xd11c:
            return device_dict['path']
    return None

def hid_read():
    logging.info("def hid_read():")
    read_start = time.time()
    while time.time() - read_start <= 0.5:
        result = h.read(DUCKYPAD_TO_PC_HID_BUF_SIZE)
        if len(result) > 0:
            return result
        time.sleep(0.01)
    return []

def duckypad_hid_write(hid_buf_64b):
    logging.info("def duckypad_hid_write(hid_buf_64b):")
    global is_hid_open
    if is_hid_open is False:
        raise OSError('duckyPad not connected')
    if len(hid_buf_64b) != PC_TO_DUCKYPAD_HID_BUF_SIZE:
        raise ValueError('PC-to-duckyPad buffer wrong size, should be exactly 64 Bytes')
    result = None
    try:
        h.write(hid_buf_64b)
        result = hid_read()
    except Exception as e:
        h.close()
        is_hid_open = False
        raise OSError('duckyPad write error')
    return result

