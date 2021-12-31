# duckyPad Profile Auto-switcher

[Get duckyPad](https://www.tindie.com/products/21984/) | [Official Discord](https://discord.gg/4sJCBx5) | [Project Main Page](https://github.com/dekuNukem/duckyPad)

This app allows your duckyPad to **switch profiles automatically** based on **current active window**.

![Alt text](resources/switch.gif)

⚠️ This software is fairly new, and there might be some bugs or rough edges. [Let me know](#questions-or-comments) if you run into any problems!

## User Manual

### Download and Launch the App

[Head over here](https://github.com/dekuNukem/duckyPad-profile-autoswitcher/releases) and download the latest release.

Extract the `.zip` file and launch the app by clicking `duckypad_autoprofile.exe`:

![Alt text](resources/app.png)

### Linux Users

Linux users might need to [apply a udev rule](https://github.com/dekuNukem/duckyPad/blob/master/app_posix.md#udev-rule), then launch the program with:

```
xhost +; sudo python3 duckypad_autoprofile.py 
```

Use `pip3` to install any missing packages.

Arch Linux users can find this application in [AUR](https://aur.archlinux.org/packages/duckypad-profile-autoswitcher-git/) and may use tool such as `yay` for a quick installation.

### "Untrusted App" Warnings

When trying to run the app, your system might complain about this software being untrusted. This is because I haven't had the code digitally signed, which costs hundreds of dollars a year.

Feel free to [review the code](https://github.com/dekuNukem/duckyPad-profile-autoswitcher/tree/master/src), you can also run `duckypad_autoprofile.py` directly with Python3. 

For Windows 10, click `More info` and then `Run anyway`.

![Alt text](resources/defender.png)

For macOS, **`RIGHT CLICK`** on the app and select `Open`. You might have to do it twice.

![Alt text](resources/macos_warning.png)

### Using the App

Once plugged in, your duckyPad should show up in the `Connection` section.

If not, make sure you duckyPad [is running the latest firmware](https://github.com/dekuNukem/duckyPad/blob/master/firmware_updates_and_version_history.md) (0.18.0 and above).

![Alt text](resources/empty.png)

You can use the buttons in `dashboard` section to open user manual, [discord](https://discord.gg/4sJCBx5), make backups, switch profiles, and start/pause profile autoswitching. 

![Alt text](resources/dash.png)

Profile autoswitching is based on a list of *rules*.

To create a new rule, click `New rule...` button:

![Alt text](resources/rulebox.png)

A new window should pop up:

![Alt text](resources/rulewin.png)

Each rule contains **application name**, **window title**, and the **profile number** to switch to.

Type in the keywords you want to match in the text box. They are **case-insensitive**, leave blank to match all.

Current active window and a list of all windows are provided for reference.

Click `Save` when done.

-------

Back to the main window, duckyPad should now automatically switch profile once a rule is matched!

![Alt text](resources/active_rules.png)

* Rules are evaluated **from top to bottom**, and **stops at first match**!

* Currently matched rule will turn green. 

* Select a rule and click `Move up` and `Move down` to rearrange its priority.

* Click `On/Off` button to enable/disable a rule.

That's pretty much it! Just leave the app running and duckyPad will do its thing!

## Launch Autoswitcher on Windows Startup

If you want to launch autoswitcher with Windows, The easiest way is to place a shortcut in the Startup folder:

* Select the autoswitcher app and press `Ctrl+C`.

* Press `Win+R` to open the `Run...` dialog, enter `shell:startup` and click OK. This will open the Startup folder.

* Right click inside the window, and click "Paste Shortcut". 

## HID Command Protocol

Of course, now that duckyPad supports HID communication, you can write your own program to control it from PC!

[Click me for details](HID_details.md)!

## Questions or Comments?

Please feel free to [open an issue](https://github.com/dekuNukem/duckypad/issues), ask in the [official duckyPad discord](https://discord.gg/4sJCBx5), DM me on discord `dekuNukem#6998`, or email `dekuNukem`@`gmail`.`com` for inquires.

