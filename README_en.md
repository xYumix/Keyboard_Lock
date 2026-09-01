# Keyboard_Lock
[🇷🇺 Русский](README.md) | [🇺🇸 English](README_en.md)

[![License: PolyForm Noncommercial 1.0.0](https://img.shields.io/badge/License-PolyForm%20Noncommercial%201.0.0-blue.svg)](https://polyformproject.org/licenses/noncommercial/1.0.0)

This project is a handy program that automatically blocks your laptop's built-in keyboard (for example, on an HP Omen 15 or any other model) so it doesn't get in the way when you connect an external USB keyboard. The program runs quietly in the background and minimizes to the system tray (the icon near the clock in the bottom right corner of the screen).

> *This project uses the Interception API (by Oblita), which is licensed under LGPL for non-commercial purposes.*

---

## ⚠️ Important Warning (Don't be alarmed by system windows!)

Since the program manages real hardware (disabling the keyboard at a deep system level), **administrator privileges are absolutely required** for it to work correctly. 

You won't have to configure this manually — I have already built the automatic privilege request feature into both scripts. 

Therefore, when you run the `check_device_keyboard` or `keyboard_monitor` files, your screen might dim, and Windows will show the standard User Account Control window asking: *"Do you want to allow this app to make changes to your device?"*. 

**Feel free to click "Yes"!** This is completely normal behavior. Without these permissions, Windows simply won't allow the program to block your built-in keyboard.

---

## 🛠 Preparation (What you need to do once)

If you have never worked with programming or scripts, don't be intimidated! Just follow these steps.

**1. Installing Python (the language the program runs on)**
* Go to the official website [python.org](https://www.python.org/downloads/) and download the latest version.
* Run the downloaded file.
* **VERY IMPORTANT:** In the very first installation window, at the very bottom, make sure to check the box **"Add Python to PATH"** (or "Add python.exe to PATH"). Without this, the program won't run! After that, click "Install Now".

**2. Installing (or Uninstalling) the Interception Driver**
* Download this project to your computer (green Code button -> Download ZIP) and make sure to **extract** the archive to a convenient folder.
* Open the `Install Interception Driver` folder inside your downloaded project. Inside, you will find two files to manage the driver: `install driver` (to install) and `uninstall driver` (to uninstall).
* To install, double-click the `install driver` (or `install driver.py`) file.
* The script will ask for administrator privileges (feel free to click "Yes") and automatically run the process. A black console window will confirm a successful installation.
* **VERY IMPORTANT: Be sure to restart your computer** after the installation, otherwise the driver will not work and the keyboard will not be intercepted!
* *(Note: If you ever want to completely remove the driver from your system in the future, open this same folder, run the `uninstall driver` file and restart your computer again).*

---

## ⚙️ Program Setup (Only 2 steps)

The program needs to be told exactly which keyboard to disable (the built-in one) and which one to leave working (the external one). 

**Step 1: Finding the ID (number) of your built-in keyboard**
1. Open the main project folder.
2. Find the file `check_device_keyboard` (it might be named `check_device_keyboard.py`).
3. Run it by double-clicking the left mouse button.
4. A black window (console) will appear. Press any key on your **laptop's built-in keyboard** — the exact one you want to block.
5. Text with the ID (number) of your keyboard will appear in the black window. Write down or copy this number. You can close the window.

**Step 2: Entering the ID into the main program**
1. In the same folder, find the second file — `keyboard_monitor` (or `keyboard_monitor.pyw`).
2. Right-click on it, select **"Open with"** and choose the standard **Notepad**.
3. In the opened text, find the place where you need to enter the ID (it will say `INTERNAL_KB_ID = ...`).
4. Carefully delete the old number (or empty space) and enter the number you got in Step 1. Do not change anything else in the code!
5. In Notepad, click `File -> Save` (or press `Ctrl + S` on your keyboard) and close Notepad.

---

## 🚀 How to Use

Now everything is ready! 

Just run the `keyboard_monitor` file with a double click. Your built-in keyboard will be immediately blocked, and your external one will continue to work. 

Our program's icon will appear in the bottom right corner of the screen (where the clock and volume are). If you ever want to enable the laptop keyboard again, just right-click on this icon and close the program.

---

## 📖 Story of Creation (Why I wrote my own script)

This project came to life because of Windows' stubbornness. Initially, the task seemed elementary: just automatically disable the built-in keyboard on an HP Omen 15 when connecting an external one. 

Searching for ready-made solutions on GitHub yielded scripts that tried to disable the device head-on — via the `pnputil` console utility or Device Manager commands. But in practice, this path turned out to be a dead end. Windows strictly blocks the software disabling of "critical system devices," which includes the built-in keyboard on a PS/2 or ACPI bus. Existing third-party solutions threw access errors or were simply ignored by the system.

Since the OS wouldn't let me disable the hardware itself, I changed the approach and decided to jam its signals. Using the `interception` driver at the kernel level and the `ctypes` library, I taught the script to recognize the unique hardware ID of the built-in keyboard and physically block its keystrokes. External USB devices remain unaffected. The result is this lightweight program with a system tray icon that does exactly what is needed.
