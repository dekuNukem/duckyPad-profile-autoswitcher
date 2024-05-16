import time
import platform

p = platform.system()

if p == 'Windows':
    import ctypes
    import ctwin32
    import ctwin32.ntdll
    import ctwin32.user
    import pygetwindow as gw
elif p == 'Darwin':
    from AppKit import NSWorkspace
    import Quartz
elif p == 'Linux':
    from ewmh import EWMH
    import psutil
    import Xlib
    import subprocess # Used to interact with kdotool in bash
    import os #
    NET_WM_NAME = Xlib.display.Display().intern_atom('_NET_WM_NAME')
    if os.environ.get('DESKTOP_SESSION'): #Check wether plasma kde is running.
        is_plasmawayland = True
    else:
        is_plasmawayland = False

def get_active_window():
    if p == 'Windows':
        return win_get_active_window()
    elif p == 'Darwin':
        return darwin_get_active_window()
    elif p == 'Linux':
        return linux_get_active_window()
    raise 'Platform %s not supported' % p

def get_list_of_all_windows():
    if p == 'Windows':
        return win_get_list_of_all_windows()
    elif p == 'Darwin':
        return darwin_get_list_of_all_windows()
    elif p == 'Linux':
        return linux_get_list_of_all_windows()
    raise 'Platform %s not supported' % p

def linux_get_list_of_all_windows():
    '''
    Added new code for this function, which uses the bash package kdotool for checking all windows and sending them to ret
    whenever the display server is on wayland. As far as I can tell, it grabs xwayland windows as well. This method should only work for KDE,
    and I tested it on Manjaro Linux running plasma 6
    '''
    ret = set()
    ewmh = EWMH()
    if is_plasmawayland: #This part of the function uses kdotool to check for all active windows and sends them to ret.
        for window in list(filter(None, subprocess.check_output(['kdotool', 'search']).decode().split('\n'))):
            try:
                win_pid = int(subprocess.check_output(['kdotool', 'getwindowpid', window]).decode())
            except TypeError:
                win_pid = False
            if win_pid:
                app = psutil.Process(win_pid).name()
            else:
                app = 'Unknown'
            wm_name = subprocess.check_output(['kdotool','getwindowname',window]).decode().strip()
            if not wm_name:
                wm_name = 'Unknown'
            ret.add((app, wm_name))
    else: # Current function for getting window list, runs only of not on wayland.
        for window in ewmh.getClientList():
            try:
                win_pid = ewmh.getWmPid(window)
            except TypeError:
                win_pid = False
            if win_pid:
                app = psutil.Process(win_pid).name()
            else:
                app = 'Unknown'
            wm_name = window.get_wm_name()
            if not wm_name:
                wm_name = window.get_full_property(NET_WM_NAME, 0).value
            if not wm_name:
                wm_name = 'class:{}'.format(window.get_wm_class()[0])
            if isinstance(wm_name, bytes):
                wm_name = wm_name.decode('utf-8')
            ret.add((app, wm_name))
    return ret

def linux_get_active_window():
    '''
    Added a new conditional portion of the function, which uses kdotool to get the active window data when on wayland
    '''
    ret = set()
    ewmh = EWMH()
    if is_plasmawayland:
        active_window = subprocess.check_output(['kdotool', 'getactivewindow']).decode().strip()
        if not active_window:
            return '', ''
        try:
            win_pid = int(subprocess.check_output(['kdotool','getwindowpid',active_window]).decode())
        except TypeError:
            win_pid = False
        wm_name = subprocess.check_output(['kdotool', 'getwindowname', active_window])
    else:
        active_window = ewmh.getActiveWindow()
        if not active_window:
            return '', ''
        try:
            win_pid = ewmh.getWmPid(active_window)
        except TypeError:
            win_pid = False
        except Xlib.error.XResourceError:
            return '', ''
        wm_name = active_window.get_wm_name()
    if not wm_name:
        wm_name = active_window.get_full_property(NET_WM_NAME, 0).value
    if not wm_name:
        wm_name = 'class:{}'.format(active_window.get_wm_class()[0])
    if isinstance(wm_name, bytes):
        wm_name = wm_name.decode('utf-8')
    if win_pid:
        active_app = psutil.Process(win_pid).name()
    else:
        return '', wm_name
    return (active_app, wm_name)

def darwin_get_active_window():
    windows = Quartz.CGWindowListCopyWindowInfo(
        Quartz.kCGWindowListExcludeDesktopElements | Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID)
    for window in windows:
        if window[Quartz.kCGWindowLayer] == 0:
            return window[Quartz.kCGWindowOwnerName], window.get(Quartz.kCGWindowName, 'unknown')
    return '', ''

def darwin_get_list_of_all_windows():
    apps = []
    windows = Quartz.CGWindowListCopyWindowInfo(
        Quartz.kCGWindowListExcludeDesktopElements | Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID)

    for window in windows:
        apps.append((window[Quartz.kCGWindowOwnerName],
                    window.get(Quartz.kCGWindowName, 'unknown')))
    apps = list(set(apps))
    apps = sorted(apps, key=lambda x: x[0])
    return apps

def win_get_app_name(hwnd):
    """Get application name given hwnd."""
    try:
        _, pid = ctwin32.user.GetWindowThreadProcessId(hwnd)
        spii = ctwin32.ntdll.SYSTEM_PROCESS_ID_INFORMATION()
        buffer = ctypes.create_unicode_buffer(0x1000)
        spii.ProcessId = pid
        spii.ImageName.MaximumLength = len(buffer)
        spii.ImageName.Buffer = ctypes.addressof(buffer)
        ctwin32.ntdll.NtQuerySystemInformation(ctwin32.SystemProcessIdInformation, ctypes.byref(spii), ctypes.sizeof(spii), None)
        name = str(spii.ImageName)
        dot = name.rfind('.')
        slash = name.rfind('\\')
        exe = name[slash+1:dot]
    except:
        return 'unknown'
    else:
        return exe

def win_get_list_of_all_windows():
    ret = set()
    for item in gw.getAllWindows():
        ret.add((win_get_app_name(item._hWnd), item.title))
    ret = sorted(list(ret), key=lambda x: x[0])
    return ret

def win_get_active_window():
    active_window = gw.getActiveWindow()
    if active_window is None:
        return '', ''
    return (win_get_app_name(active_window._hWnd), active_window.title)

# print(get_list_of_all_windows())
