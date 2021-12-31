"""
duckyPad HID example: HID write

For more details, see:

https://github.com/dekuNukem/duckyPad-profile-autoswitcher/blob/master/HID_details.md

"""

import hid

PC_TO_DUCKYPAD_HID_BUF_SIZE = 64

h = hid.device()

def get_duckypad_path():
	for device_dict in hid.enumerate():
	    if device_dict['vendor_id'] == 0x0483 and device_dict['product_id'] == 0xd11c and device_dict['usage'] == 58:
	    	return device_dict['path']
	    elif device_dict['vendor_id'] == 0x0483 and device_dict['product_id'] == 0xd11c:
	    	return device_dict['path']
	return None

pc_to_duckypad_buf = [0] * PC_TO_DUCKYPAD_HID_BUF_SIZE
pc_to_duckypad_buf[0] = 5	# HID Usage ID, always 5
pc_to_duckypad_buf[1] = 0	# Sequence Number
pc_to_duckypad_buf[2] = 3	# Command type

duckypad_path = get_duckypad_path()

print("----\nsudo is needed on Linux!\n----")
if duckypad_path is None:
	print("duckyPad not found!")
h.open_path(duckypad_path)
h.set_nonblocking(1)
print("\n\nSending to duckyPad:\n", pc_to_duckypad_buf)
h.write(pc_to_duckypad_buf)
h.close()
print('done!')
