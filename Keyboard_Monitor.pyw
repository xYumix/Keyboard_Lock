import ctypes
import os
import sys
import time
import threading
import win32com.client
import pythoncom
import pystray
from PIL import Image, ImageDraw

# === НАСТРОЙКИ ===
INTERNAL_KB_ID = 1 

def is_admin():
    return ctypes.windll.shell32.IsUserAnAdmin()

if not is_admin():
    script_path = os.path.abspath(sys.argv[0])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script_path}"', None, 1)
    sys.exit()

dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "interception.dll")
if not os.path.exists(dll_path):
    ctypes.windll.user32.MessageBoxW(0, f"Файл interception.dll не найден в папке:\n{os.path.dirname(os.path.abspath(__file__))}", "Ошибка запуска", 0x10)
    sys.exit()

lib = ctypes.cdll.LoadLibrary(dll_path)

# --- C-структуры и функции драйвера ---
class KeyStroke(ctypes.Structure):
    _fields_ = [
        ("code", ctypes.c_ushort),
        ("state", ctypes.c_ushort),
        ("information", ctypes.c_uint)
    ]

lib.interception_create_context.restype = ctypes.c_void_p
lib.interception_wait.argtypes = [ctypes.c_void_p]
lib.interception_wait.restype = ctypes.c_int
lib.interception_receive.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(KeyStroke), ctypes.c_uint]
lib.interception_receive.restype = ctypes.c_int
lib.interception_send.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(KeyStroke), ctypes.c_uint]
lib.interception_send.restype = ctypes.c_int

PredicateFunc = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int)

@PredicateFunc
def is_keyboard(device):
    return lib.interception_is_keyboard(device)

lib.interception_set_filter.argtypes = [ctypes.c_void_p, PredicateFunc, ctypes.c_int]

# --- Основная логика ---
class SmartKeyboardBlocker:
    def __init__(self, internal_id):
        self.internal_id = internal_id
        self.is_blocking = False
        self.icon = None  # Сюда мы передадим нашу иконку из трея
        
        self.context = lib.interception_create_context()
        if not self.context:
            ctypes.windll.user32.MessageBoxW(0, "Не удалось создать контекст Interception. Перезагрузите ПК.", "Ошибка драйвера", 0x10)
            sys.exit()
            
        lib.interception_set_filter(self.context, is_keyboard, 0xFFFF)

    def get_usb_keyboards(self):
        try:
            wmi = win32com.client.GetObject("winmgmts:")
            keyboards = wmi.ExecQuery("SELECT * FROM Win32_Keyboard")
            return [kb.DeviceID for kb in keyboards if kb.DeviceID and 'USB' in kb.DeviceID.upper()]
        except:
            return []

    def update_tray_text(self, is_external_connected):
        """Обновляет текст при наведении на иконку в трее"""
        if not self.icon:
            return
            
        if is_external_connected:
            self.icon.title = "   Авто-отключение клавиатуры\n\nПодключена внешняя клавиатура\nКлавиатура ноутбука ОТКЛЮЧЕНА"
        else:
            self.icon.title = "   Авто-отключение клавиатуры\n\nВнешняя клавиатура не найдена\nКлавиатура ноутбука РАБОТАЕТ"

    def monitor_usb_state(self):
        pythoncom.CoInitialize()
        try:
            # Делаем первичную проверку при запуске
            usb_kbs = self.get_usb_keyboards()
            self.is_blocking = bool(usb_kbs)
            self.update_tray_text(self.is_blocking)
            
            while True:
                usb_kbs = self.get_usb_keyboards()
                if usb_kbs and not self.is_blocking:
                    self.is_blocking = True
                    self.update_tray_text(True)
                elif not usb_kbs and self.is_blocking:
                    self.is_blocking = False
                    self.update_tray_text(False)
                time.sleep(2)
        finally:
            pythoncom.CoUninitialize()

    def run_interception(self):
        stroke = KeyStroke()
        while True:
            device = lib.interception_wait(self.context)
            if lib.interception_receive(self.context, device, ctypes.byref(stroke), 1) > 0:
                if device == self.internal_id and self.is_blocking:
                    continue
                lib.interception_send(self.context, device, ctypes.byref(stroke), 1)

# --- Системный трей ---
def create_tray_icon_image():
    size = 64
    image = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    kb_outline = (220, 220, 220, 255)
    kb_bg = (50, 54, 62, 255)
    red_sign = (237, 66, 69, 255)
    
    draw.rectangle((10, 20, 54, 44), fill=kb_bg, outline=kb_outline, width=2)
    draw.rectangle((14, 24, 20, 30), fill=kb_outline)
    draw.rectangle((24, 24, 30, 30), fill=kb_outline)
    draw.rectangle((34, 24, 40, 30), fill=kb_outline)
    draw.rectangle((44, 24, 50, 30), fill=kb_outline)
    draw.rectangle((14, 34, 20, 40), fill=kb_outline)
    draw.rectangle((24, 34, 40, 40), fill=kb_outline)
    draw.rectangle((44, 34, 50, 40), fill=kb_outline)
    
    draw.ellipse((4, 4, 60, 60), outline=red_sign, width=6)
    draw.line((14, 14, 50, 50), fill=red_sign, width=6)
    
    return image

def exit_action(icon, item):
    icon.stop()

def main():
    blocker = SmartKeyboardBlocker(INTERNAL_KB_ID)
    menu = pystray.Menu(pystray.MenuItem('Закрыть блокировщик', exit_action))
    
    # Создаем иконку с первоначальным текстом загрузки
    icon = pystray.Icon("omen_kb_blocker", create_tray_icon_image(), "Авто-отключение клавиатуры\nИнициализация...", menu)
    
    # Передаем объекту блокировщика ссылку на иконку, чтобы он мог менять в ней текст
    blocker.icon = icon
    
    t_wmi = threading.Thread(target=blocker.monitor_usb_state, daemon=True)
    t_wmi.start()
    
    t_intercept = threading.Thread(target=blocker.run_interception, daemon=True)
    t_intercept.start()
    
    icon.run()

if __name__ == "__main__":
    main()