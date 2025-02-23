import hid
import time

PC_TO_DUCKYPAD_HID_BUF_SIZE = 64
DUCKYPAD_TO_PC_HID_BUF_SIZE = 64

h = hid.device()

def duckypad_init():
    duckypad_path = get_duckypad_path()
    if duckypad_path is None:
        return False
    try:
        h.open_path(duckypad_path)
    except Exception as e:
        if "already open" in str(e).lower():
            return True
        else:
            raise RuntimeError("open_path failed")
    h.set_nonblocking(1)
    return True

def duckypad_close():
    h.close()

def duckypad_get_info():
    dpinfo = {}
    dpinfo['model'] = h.get_product_string()
    dpinfo['serial'] = h.get_serial_number_string()
    buffff = [0] * 64
    buffff[0] = 5
    result = duckypad_hid_write(buffff)
    dpinfo['fw_ver'] = f'{result[3]}.{result[4]}.{result[5]}'
    dpinfo['is_busy'] = result[2]
    return dpinfo

duckypad_pid = 0xd11c
duckypad_pro_pid = 0xd11d
valid_pid_list = [duckypad_pro_pid, duckypad_pid]

def get_duckypad_path_uncached():
    path_dict = {}
    for device_dict in hid.enumerate():
        if device_dict['vendor_id'] == 0x0483 and device_dict['product_id'] in valid_pid_list:
            path_dict[device_dict['usage']] = device_dict['path']
    if len(path_dict) == 0:
        return None
    if 58 in path_dict:
        return path_dict[58]
    return list(path_dict.values())[0]

last_dp_path = None
def get_duckypad_path(start_fresh=False):
    global last_dp_path
    if start_fresh:
        last_dp_path = None
    if last_dp_path is None:
        last_dp_path = get_duckypad_path_uncached()
    return last_dp_path

def hid_read():
    read_start = time.time()
    while time.time() - read_start <= 0.5:
        result = h.read(DUCKYPAD_TO_PC_HID_BUF_SIZE)
        if len(result) > 0:
            return result
        time.sleep(0.01)
    return []

def duckypad_hid_write(hid_buf_64b):
    if len(hid_buf_64b) != PC_TO_DUCKYPAD_HID_BUF_SIZE:
        raise ValueError('PC-to-duckyPad buffer wrong size, should be exactly 64 Bytes')
    result = None
    try:
        h.write(hid_buf_64b)
        result = hid_read()
    except Exception as e:
        h.close()
        raise OSError('duckyPad write error')
    return result

