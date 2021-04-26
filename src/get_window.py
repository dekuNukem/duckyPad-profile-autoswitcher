import wmi
import time
import win32process
import pygetwindow as gw

c = wmi.WMI()

def get_app_name(hwnd):
    """Get application name given hwnd."""
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        for p in c.query('SELECT Name FROM Win32_Process WHERE ProcessId = %s' % str(pid)):
            exe = p.Name.rsplit('.', 1)[0]
            break
    except:
        return None
    else:
        return exe

# returns a list of (app_name, window_title) tuples
def get_list_of_all_windows():
	ret = set()
	for item in gw.getAllWindows():
		ret.add((get_app_name(item._hWnd), item.title))
	ret = sorted(list(ret), key=lambda x: x[0])
	return ret

# returns a (hWnd, app_name, window_title) tuple
def get_active_window():
	active_window = gw.getActiveWindow()
	if active_window is None:
		return None, None, None
	return (active_window._hWnd, get_app_name(active_window._hWnd), active_window.title)
