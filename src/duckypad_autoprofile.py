import time
from tkinter import *
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
import urllib.request
import tkinter.scrolledtext as ScrolledText
import traceback
import json
import os
import webbrowser
import sys
import threading
import hid_rw
import get_window
import check_update
from platformdirs import *
import subprocess

def is_root():
    return os.getuid() == 0

def ensure_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

# xhost +;sudo python3 duckypad_autoprofile.py 

appname = 'duckypad_autoswitcher_dpp'
appname = 'duckypad_autoswitcher'
appauthor = 'dekuNukem'
save_path = user_data_dir(appname, appauthor, roaming=True)

ensure_dir(save_path)
save_filename = os.path.join(save_path, 'config.txt')

default_button_color = 'SystemButtonFace'
if 'linux' in sys.platform:
    default_button_color = 'grey'

"""
0.0.8 2023 02 20
faster refresh rate 33ms
added HID busy check

0.1.0 2023 10 12
added queue to prevent dropping requests when duckypad is busy

0.2.0
updated window refresh method from pull request?
seems a bit laggy tho

0.3.0
quick edit to work on duckypad pro
switch profile by name instead of number
changed timing to make it less laggy, still feels roughly the same tho

0.4.0
Nov 21 2024
Now detects both duckyPad and duckyPad Pro
supports switching profiles by name or number
UI tweaks

0.4.1
Nov 23 2024
fixed wrong FW update URL

0.4.2
Dec 26 2024
Fixed UI button size for macOS
Updated macOS info URL
Added DUCKYPAD_UI_SCALE environment variable
Exits gracefully instead of crashing when not in sudo on macOS
"""

UI_SCALE = float(os.getenv("DUCKYPAD_UI_SCALE", default=1))

def scaled_size(size: int) -> int:
    return int(size * UI_SCALE)

THIS_VERSION_NUMBER = '0.4.2'
MAIN_WINDOW_WIDTH = scaled_size(640)
MAIN_WINDOW_HEIGHT = scaled_size(660)
PADDING = 10
fw_update_checked = False
is_dpp = False

print("\n\n--------------------------")
print("\n\nWelcome to duckyPad Autoswitcher!\n")
print("This window prints debug information.")

def duckypad_connect(show_box=True):
    # print("def duckypad_connect():")
    global fw_update_checked
    global is_dpp

    if hid_rw.get_duckypad_path(start_fresh=True) is None:
        connection_info_str.set("duckyPad not found")
        connection_info_label.config(foreground='red')
        return

    init_success = True
    try:
        init_success = hid_rw.duckypad_init()
    except Exception as e:
        init_success = False

    if init_success is False:
        connection_info_str.set("duckyPad detected, but I need additional permissions!")
        connection_info_label.config(foreground='red')

    if init_success is False and show_box is False:
        return

    if init_success is False and 'linux' in sys.platform:
        messagebox.showinfo("Info", "duckyPad detected, but please run me in sudo!")
        return

    if init_success is False and 'darwin' in sys.platform:
        box_result = messagebox.askokcancel("Info", "duckyPad detected, but I need additional permissions!\n\nClick OK for instructions.")
        if box_result is True:
            webbrowser.open('https://github.com/dekuNukem/duckyPad-Pro/blob/master/doc/linux_macos_notes.md')
        exit()
        return

    if init_success is False:
        messagebox.showinfo("Info", "Failed to connect to duckyPad")
        return

    try:
        result = hid_rw.duckypad_get_info()
        if result['is_busy']:
            if show_box:
                messagebox.showerror("Error", "duckyPad is busy!\n\nMake sure no script is running.")
            hid_rw.duckypad_close()
            return
        connection_info_label.config(foreground='navy')
        connection_info_str.set(f"Connected!      Model: {result['model']}      Serial: {result['serial']}      Firmware: {result['fw_ver']}")
        if "duckypad pro" in result['model'].lower():
            is_dpp = True
        else:
            is_dpp = False
        if fw_update_checked is False:
            print_fw_update_label(result['fw_ver'])
            fw_update_checked = True
    except Exception as e:
        print(traceback.format_exc())
    hid_rw.duckypad_close()

def update_windows(textbox):
    # print("def update_windows(textbox):")
    windows_str = 'Application' + ' '*14 + "Window Title\n"
    windows_str += "-------------------------------------\n"
    for item in get_window.get_list_of_all_windows():
        gap = 25 - len(item[0])
        windows_str += str(item[0]) + ' '*gap + str(item[1]) + '\n'
    textbox.config(state=NORMAL)
    textbox.delete(1.0, "end")
    textbox.insert(1.0, windows_str)
    textbox.config(state=DISABLED)

DP_WRITE_OK = 0
DP_WRITE_FAIL = 1
DP_WRITE_BUSY = 2

def duckypad_write_with_retry(data_buf):
    print(data_buf)
    try:
        hid_rw.duckypad_init()
        if hid_rw.duckypad_get_info()['is_busy']:
            return DP_WRITE_BUSY
        hid_rw.duckypad_hid_write(data_buf)
        hid_rw.duckypad_close()
        return DP_WRITE_OK
    except Exception as e:
        # print("first exception:", traceback.format_exc())
        try:
            duckypad_connect(show_box=False)
            hid_rw.duckypad_init()
            if hid_rw.duckypad_get_info()['is_busy']:
                return DP_WRITE_BUSY
            hid_rw.duckypad_hid_write(data_buf)
            hid_rw.duckypad_close()
            return DP_WRITE_OK
        except Exception as e:
            pass
            # print("second exception:", traceback.format_exc())
    return DP_WRITE_FAIL

def prev_prof_click():
    # print("def prev_prof_click():")
    buffff = [0] * 64
    buffff[0] = 5
    buffff[2] = 2
    duckypad_write_with_retry(buffff)

def next_prof_click():
    # print("def next_prof_click():")
    buffff = [0] * 64
    buffff[0] = 5
    buffff[2] = 3
    duckypad_write_with_retry(buffff)

root = Tk()
root.title("duckyPad autoswitcher " + THIS_VERSION_NUMBER)
root.geometry(f"{MAIN_WINDOW_WIDTH}x{MAIN_WINDOW_HEIGHT}")
root.resizable(width=FALSE, height=FALSE)

# --------------------

connection_info_str = StringVar()
connection_info_str.set("<--- Press Connect button")
connection_info_lf = LabelFrame(root, text="Connection", width=scaled_size(620), height=scaled_size(60))
connection_info_lf.place(x=scaled_size(PADDING), y=scaled_size(0)) 
connection_info_label = Label(master=connection_info_lf, textvariable=connection_info_str)
connection_info_label.place(x=scaled_size(110), y=scaled_size(5))
connection_info_label.config(foreground='orange red')

connection_button = Button(connection_info_lf, text="Connect", command=duckypad_connect)
connection_button.place(x=scaled_size(PADDING), y=scaled_size(5), width=scaled_size(90))

# --------------------

discord_link_url = "https://raw.githubusercontent.com/dekuNukem/duckyPad/master/resources/discord_link.txt"

def open_user_manual():
    # print("def open_user_manual():")
    webbrowser.open('https://github.com/dekuNukem/duckyPad-profile-autoswitcher/blob/master/README.md#user-manual')

def open_discord():
    # print("def open_discord():")
    try:
        webbrowser.open(str(urllib.request.urlopen(discord_link_url).read().decode('utf-8')).split('\n')[0])
    except Exception as e:
        messagebox.showerror("Error", "Failed to open discord link!\n"+str(e))

def refresh_autoswitch():
    # print("def refresh_autoswitch():")
    if config_dict['autoswitch_enabled']:
        autoswitch_status_var.set("Profile Autoswitch: ACTIVE     Click me to stop")
        autoswitch_status_label.config(fg='white', bg='green', cursor="hand2")
    else:
        autoswitch_status_var.set("Profile Autoswitch: STOPPED    Click me to start")
        autoswitch_status_label.config(fg='white', bg='orange red', cursor="hand2")

def toggle_autoswitch(whatever):
    # print("def toggle_autoswitch(whatever):")
    config_dict['autoswitch_enabled'] = not config_dict['autoswitch_enabled']
    save_config()
    refresh_autoswitch()
    
def open_save_folder():
    # print("def open_save_folder():")
    messagebox.showinfo("Info", "* Copy config.txt elsewhere to make a backup!\n\n* Close the app then copy it back to restore.")
    if 'darwin' in sys.platform:
        subprocess.Popen(["open", save_path])
    elif 'linux' in sys.platform:
        subprocess.Popen(["xdg-open", save_path])
    else:
        webbrowser.open(save_path)

dashboard_lf = LabelFrame(root, text="Dashboard", width=scaled_size(620), height=scaled_size(95))
dashboard_lf.place(x=scaled_size(PADDING), y=scaled_size(60)) 
prev_profile_button = Button(dashboard_lf, text="Prev Profile", command=prev_prof_click)
prev_profile_button.place(x=scaled_size(410), y=scaled_size(5), width=scaled_size(90))

next_profile_button = Button(dashboard_lf, text="Next Profile", command=next_prof_click)
next_profile_button.place(x=scaled_size(510), y=scaled_size(5), width=scaled_size(90))

user_manual_button = Button(dashboard_lf, text="User Manual", command=open_user_manual)
user_manual_button.place(x=scaled_size(PADDING), y=scaled_size(5), width=scaled_size(90))

discord_button = Button(dashboard_lf, text="Discord", command=open_discord)
discord_button.place(x=scaled_size(110), y=scaled_size(5), width=scaled_size(90))

discord_button = Button(dashboard_lf, text="Backup", command=open_save_folder)
discord_button.place(x=scaled_size(210), y=scaled_size(5), width=scaled_size(90))

autoswitch_status_var = StringVar()
autoswitch_status_label = Label(master=dashboard_lf, textvariable=autoswitch_status_var, font='TkFixedFont', cursor="hand2")
autoswitch_status_label.place(x=scaled_size(10), y=scaled_size(40))
autoswitch_status_label.bind("<Button-1>", toggle_autoswitch)

# --------------------

current_app_name_var = StringVar()
current_app_name_var.set("Current app name:")

current_window_title_var = StringVar()
current_window_title_var.set("Current Window Title:")

PC_TO_DUCKYPAD_HID_BUF_SIZE = 64

def duckypad_goto_profile_by_name(profile_name):
    profile_name = profile_name[:32]
    buffff = [0] * PC_TO_DUCKYPAD_HID_BUF_SIZE
    buffff[0] = 5
    buffff[2] = 23
    for index, item in enumerate(profile_name):
        buffff[index+3] = ord(item)
    return duckypad_write_with_retry(buffff)

def duckypad_goto_profile_by_index(profile_index):
    buffff = [0] * PC_TO_DUCKYPAD_HID_BUF_SIZE
    buffff[0] = 5
    buffff[2] = 1
    buffff[3] = profile_index
    return duckypad_write_with_retry(buffff)

def duckypad_goto_profile(profile_target):
    try:
        return duckypad_goto_profile_by_index(int(profile_target))
    except Exception as e:
        # print('Not a number:', e)
        pass
    return duckypad_goto_profile_by_name(profile_target)

profile_switch_queue = []
last_switch = None

def t1_worker():
    global last_switch
    while(1):
        time.sleep(0.033)
        if len(profile_switch_queue) == 0:
            continue
        queue_head = profile_switch_queue[0]
        result = duckypad_goto_profile(queue_head)
        if result == DP_WRITE_BUSY:
            print("DUCKYPAD IS BUSY! Retrying later")
        elif result == DP_WRITE_OK:
            print("switch success")
            profile_switch_queue.pop(0)
            last_switch = queue_head
            print(profile_switch_queue)
        
def switch_queue_add(profile_target_name):
    global last_switch
    if profile_target_name is None or len(profile_target_name) == 0:
        return
    if profile_target_name == last_switch:
        return
    if len(profile_switch_queue) > 0 and profile_switch_queue[-1] == profile_target_name:
        return
    profile_switch_queue.append(profile_target_name)

WINDOW_CHECK_FREQUENCY_MS = 100

def update_current_app_and_title():
    # print("def update_current_app_and_title():")

    root.after(WINDOW_CHECK_FREQUENCY_MS, update_current_app_and_title)

    # if hid_rw.is_hid_open is False and button_pressed is True:
    #     connection_info_str.set("duckyPad not found")
    #     connection_info_label.config(foreground='red')

    app_name, window_title = get_window.get_active_window()
    current_app_name_var.set("App name:      " + str(app_name))
    current_window_title_var.set("Window title:  " + str(window_title))

    if rule_window is not None and rule_window.winfo_exists():
        return
    if config_dict['autoswitch_enabled'] is False:
        return

    highlight_index = None
    for index, item in enumerate(config_dict['rules_list']):
        if item['enabled'] is False:
            continue
        app_name_condition = True
        if len(item['app_name']) > 0:
            app_name_condition = item['app_name'].lower() in app_name.lower()
        window_title_condition = True
        if len(item['window_title']) > 0:
            window_title_condition = item['window_title'].lower() in window_title.lower()
        if app_name_condition and window_title_condition:
            switch_queue_add(str(item['switch_to']))
            highlight_index = index
            break

    for index, item in enumerate(config_dict['rules_list']):
        if index == highlight_index:
            profile_lstbox.itemconfig(index, fg='white', bg='green')
        else:
            profile_lstbox.itemconfig(index, fg='black', bg='white')

# ----------------

app_name_entrybox = None
window_name_entrybox = None
switch_to_entrybox = None
config_dict = {}
config_dict['rules_list'] = []
config_dict['autoswitch_enabled'] = True

def clean_input(str_input):
    # print("def clean_input(str_input):")
    return str_input.strip()

invalid_filename_characters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

def clean_input(str_input, len_limit=None):
    result = ''.join([x for x in str_input if 32 <= ord(x) <= 126 and x not in invalid_filename_characters])
    while('  ' in result):
        result = result.replace('  ', ' ')
    if len_limit is not None:
        result = result[:len_limit]
    return result.strip()

def check_profile_name_or_number(raw_str):
    return clean_input(raw_str)

def make_rule_str(rule_dict):
    # print("def make_rule_str(rule_dict):")
    rule_str = ''
    if rule_dict['enabled']:
        rule_str += "  * "
    else:
        rule_str += "    "
    if len(rule_dict['app_name']) > 0:
        rule_str += "     " + rule_dict['app_name']
    else:
        rule_str += "     " + "[Any]"

    next_item = rule_dict['window_title']
    if len(next_item) <= 0:
        next_item = "[Any]"
    gap = 26 - len(rule_str)
    rule_str += ' '*gap + next_item

    gap = 50 - len(rule_str)
    rule_str += ' '*gap + str(rule_dict['switch_to'])

    return rule_str

def update_rule_list_display():
    # print("def update_rule_list_display():")
    profile_var.set([make_rule_str(x) for x in config_dict['rules_list']])

def save_config():
    # print("def save_config():")
    try:
        ensure_dir(save_path)
        with open(save_filename, 'w', encoding='utf8') as save_file:
            save_file.write(json.dumps(config_dict, sort_keys=True))
    except Exception as e:
        messagebox.showerror("Error", "Save failed!\n\n"+str(traceback.format_exc()))

def save_rule_click(window, this_rule):
    # print("def save_rule_click(window, this_rule):")
    if this_rule is None:
        rule_dict = {}
        rule_dict["app_name"] = clean_input(app_name_entrybox.get())
        rule_dict["window_title"] = clean_input(window_name_entrybox.get())
        rule_dict["switch_to"] = check_profile_name_or_number(switch_to_entrybox.get())
        rule_dict["enabled"] = True
        if rule_dict not in config_dict['rules_list']:
            config_dict['rules_list'].append(rule_dict)
            update_rule_list_display()
            save_config()
            window.destroy()
    elif this_rule is not None:
        this_rule["app_name"] = clean_input(app_name_entrybox.get())
        this_rule["window_title"] = clean_input(window_name_entrybox.get())
        this_rule["switch_to"] = check_profile_name_or_number(switch_to_entrybox.get())
        update_rule_list_display()
        save_config()
        window.destroy()

rule_window = None
RULE_WINDOW_WIDTH = scaled_size(640)
RULE_WINDOW_HEIGHT = scaled_size(510)

def create_rule_window(existing_rule=None):
    # print("def create_rule_window(existing_rule=None):")
    global rule_window
    global app_name_entrybox
    global window_name_entrybox
    global switch_to_entrybox
    rule_window = Toplevel(root)
    rule_window.title("Edit rules")
    rule_window.geometry(f"{RULE_WINDOW_WIDTH}x{RULE_WINDOW_HEIGHT}")
    rule_window.resizable(width=FALSE, height=FALSE)
    rule_window.grab_set()

    rule_edit_lf = LabelFrame(rule_window, text="Rules", width=scaled_size(620), height=scaled_size(130))
    rule_edit_lf.place(x=scaled_size(10), y=scaled_size(5))

    app_name_label = Label(master=rule_window, text="IF app name contains:")
    app_name_label.place(x=scaled_size(20), y=scaled_size(25))
    app_name_entrybox = Entry(rule_window)
    app_name_entrybox.place(x=scaled_size(250), y=scaled_size(25), width=scaled_size(200))
    
    window_name_label = Label(master=rule_window, text="AND window title contains:")
    window_name_label.place(x=scaled_size(20), y=scaled_size(50))
    window_name_entrybox = Entry(rule_window)
    window_name_entrybox.place(x=scaled_size(250), y=scaled_size(50), width=scaled_size(200))

    switch_to_label = Label(master=rule_window, text="THEN jump to profile (Name or #):")
    switch_to_label.place(x=scaled_size(20), y=scaled_size(75))
    switch_to_entrybox = Entry(rule_window)
    switch_to_entrybox.place(x=scaled_size(250), y=scaled_size(75), width=scaled_size(200))

    if existing_rule is not None:
        app_name_entrybox.insert(0, existing_rule["app_name"])
        window_name_entrybox.insert(0, existing_rule["window_title"])
        if existing_rule["switch_to"] is None:
            switch_to_entrybox.insert(0, "")
        else:
            switch_to_entrybox.insert(0, str(existing_rule["switch_to"]))

    rule_done_button = Button(rule_edit_lf, text="Save", command=lambda:save_rule_click(rule_window, existing_rule))
    rule_done_button.place(x=scaled_size(30), y=scaled_size(80), width=scaled_size(550))

    match_all_label = Label(master=rule_window, text="(leave blank to match all)")
    match_all_label.place(x=scaled_size(470), y=scaled_size(25))
    match_all_label2 = Label(master=rule_window, text="(leave blank to match all)")
    match_all_label2.place(x=scaled_size(470), y=scaled_size(50))
    match_all_label3 = Label(master=rule_window, text="(leave blank for no action)")
    match_all_label3.place(x=scaled_size(470), y=scaled_size(75))

    current_window_lf = LabelFrame(rule_window, text="Active window", width=scaled_size(620), height=scaled_size(80))
    current_window_lf.place(x=scaled_size(PADDING), y=scaled_size(140))

    current_app_name_label = Label(master=current_window_lf, textvariable=current_app_name_var, font='TkFixedFont')
    current_app_name_label.place(x=scaled_size(10), y=scaled_size(5))
    current_window_title_label = Label(master=current_window_lf, textvariable=current_window_title_var, font='TkFixedFont')
    current_window_title_label.place(x=scaled_size(10), y=scaled_size(30))

    window_list_lf = LabelFrame(rule_window, text="All windows", width=scaled_size(620), height=scaled_size(270))
    window_list_lf.place(x=scaled_size(PADDING), y=scaled_size(195+30)) 
    window_list_fresh_button = Button(window_list_lf, text="Refresh", command=lambda:update_windows(windows_list_text_area))
    window_list_fresh_button.place(x=scaled_size(30), y=scaled_size(220), width=scaled_size(550))
    windows_list_text_area = ScrolledText.ScrolledText(window_list_lf, wrap='none', width=scaled_size(73), height=scaled_size(13))
    windows_list_text_area.place(x=scaled_size(5), y=scaled_size(5))
    root.update()
    update_windows(windows_list_text_area)

def delete_rule_click():
    # print("def delete_rule_click():")
    selection = profile_lstbox.curselection()
    if len(selection) <= 0:
        return
    config_dict['rules_list'].pop(selection[0])
    update_rule_list_display()
    save_config()

def edit_rule_click():
    # print("def edit_rule_click():")
    selection = profile_lstbox.curselection()
    if len(selection) <= 0:
        return
    create_rule_window(config_dict['rules_list'][selection[0]])

def toggle_rule_click():
    # print("def toggle_rule_click():")
    selection = profile_lstbox.curselection()
    if len(selection) <= 0:
        return
    config_dict['rules_list'][selection[0]]['enabled'] = not config_dict['rules_list'][selection[0]]['enabled']
    update_rule_list_display()
    save_config()

def rule_shift_up():
    # print("def rule_shift_up():")
    selection = profile_lstbox.curselection()
    if len(selection) <= 0 or selection[0] == 0:
        return
    source = selection[0]
    destination = selection[0] - 1
    config_dict['rules_list'][destination], config_dict['rules_list'][source] = config_dict['rules_list'][source], config_dict['rules_list'][destination]
    update_rule_list_display()
    profile_lstbox.selection_clear(0, len(config_dict['rules_list']))
    profile_lstbox.selection_set(destination)
    update_rule_list_display()
    save_config()

def rule_shift_down():
    # print("def rule_shift_down():")
    selection = profile_lstbox.curselection()
    if len(selection) <= 0 or selection[0] == len(config_dict['rules_list']) - 1:
        return
    source = selection[0]
    destination = selection[0] + 1
    config_dict['rules_list'][destination], config_dict['rules_list'][source] = config_dict['rules_list'][source], config_dict['rules_list'][destination]
    update_rule_list_display()
    profile_lstbox.selection_clear(0, len(config_dict['rules_list']))
    profile_lstbox.selection_set(destination)
    update_rule_list_display()
    save_config()

rules_lf = LabelFrame(root, text="Autoswitch rules", width=scaled_size(620), height=scaled_size(410))
rules_lf.place(x=scaled_size(PADDING), y=scaled_size(160)) 

profile_var = StringVar()
profile_lstbox = Listbox(rules_lf, listvariable=profile_var, height=scaled_size(20), exportselection=0)
profile_lstbox.place(x=scaled_size(PADDING), y=scaled_size(30), width=scaled_size(500))
profile_lstbox.config(font='TkFixedFont')
profile_lstbox.bind('<FocusOut>', lambda e: profile_lstbox.selection_clear(0, END))

rule_header_label = Label(master=rules_lf, text="Enabled   App              Window                 Profile", font='TkFixedFont')
rule_header_label.place(x=scaled_size(5), y=scaled_size(5))

new_rule_button = Button(rules_lf, text="New rule...", command=create_rule_window)
new_rule_button.place(x=scaled_size(520), y=scaled_size(30), width=scaled_size(90))

edit_rule_button = Button(rules_lf, text="Edit rule...", command=edit_rule_click)
edit_rule_button.place(x=scaled_size(520), y=scaled_size(70), width=scaled_size(90))

move_up_button = Button(rules_lf, text="Move up", command=rule_shift_up)
move_up_button.place(x=scaled_size(520), y=scaled_size(150), width=scaled_size(90))

toggle_rule_button = Button(rules_lf, text="On/Off", command=toggle_rule_click)
toggle_rule_button.place(x=scaled_size(520), y=scaled_size(190), width=scaled_size(90))

move_down_button = Button(rules_lf, text="Move down", command=rule_shift_down)
move_down_button.place(x=scaled_size(520), y=scaled_size(230), width=scaled_size(90))

delete_rule_button = Button(rules_lf, text="Delete rule", command=delete_rule_click)
delete_rule_button.place(x=scaled_size(520), y=scaled_size(300), width=scaled_size(90))

try:
    with open(save_filename) as json_file:
        temp = json.load(json_file)
        if isinstance(temp, list):
            config_dict['rules_list'] = temp
        elif isinstance(temp, dict):
            config_dict = temp
        else:
            raise ValueError("not a valid config file")
    update_rule_list_display()
except Exception as e:
    print(traceback.format_exc())

refresh_autoswitch()

# ------------------

def fw_update_click(what):
    # print("def fw_update_click(what):")
    if is_dpp:
        webbrowser.open('https://github.com/dekuNukem/duckyPad-Pro/blob/master/doc/firmware_updates_and_version_history.md')
    else:
        webbrowser.open('https://github.com/dekuNukem/duckyPad/blob/master/firmware_updates_and_version_history.md')

def app_update_click(event):
    # print("def app_update_click(event):")
    webbrowser.open('https://github.com/dekuNukem/duckyPad-profile-autoswitcher/releases')

def print_fw_update_label(this_version):
    # print("def print_fw_update_label(this_version):")
    fw_result = check_update.get_firmware_update_status(this_version, is_dpp)
    if fw_result == 0:
        dp_fw_update_label.config(text='duckyPad firmware (' + str(this_version) +'): Up to date', fg='black', bg=default_button_color)
        dp_fw_update_label.unbind("<Button-1>")
    elif fw_result == 1:
        dp_fw_update_label.config(text='duckyPad firmware (' + str(this_version) +'): Update available! Click me!', fg='black', bg='orange', cursor="hand2")
        dp_fw_update_label.bind("<Button-1>", fw_update_click)
    else:
        dp_fw_update_label.config(text='duckyPad firmware: Unknown', fg='black', bg=default_button_color)
        dp_fw_update_label.unbind("<Button-1>")

updates_lf = LabelFrame(root, text="Updates", width=scaled_size(620), height=scaled_size(80))
updates_lf.place(x=scaled_size(PADDING), y=scaled_size(570))

pc_app_update_label = Label(master=updates_lf)
pc_app_update_label.place(x=scaled_size(5), y=scaled_size(5))
update_stats = check_update.get_pc_app_update_status(THIS_VERSION_NUMBER)

if update_stats == 0:
    pc_app_update_label.config(text='This app (' + str(THIS_VERSION_NUMBER) + '): Up to date', fg='black', bg=default_button_color)
    pc_app_update_label.unbind("<Button-1>")
elif update_stats == 1:
    pc_app_update_label.config(text='This app (' + str(THIS_VERSION_NUMBER) + '): Update available! Click me!', fg='black', bg='orange', cursor="hand2")
    pc_app_update_label.bind("<Button-1>", app_update_click)
else:
    pc_app_update_label.config(text='This app (' + str(THIS_VERSION_NUMBER) + '): Unknown', fg='black', bg=default_button_color)
    pc_app_update_label.unbind("<Button-1>")

dp_fw_update_label = Label(master=updates_lf, text="duckyPad firmware: Unknown")
dp_fw_update_label.place(x=scaled_size(5), y=scaled_size(30))

# ------------------

# messagebox.showinfo("Info", "Now supporting switching profile by name!\n\nCase sensitive, duckyPad Pro only (for now).\n\n")
duckypad_connect()

t1 = threading.Thread(target=t1_worker, daemon=True)
t1.start()

root.after(WINDOW_CHECK_FREQUENCY_MS, update_current_app_and_title)
root.mainloop()
