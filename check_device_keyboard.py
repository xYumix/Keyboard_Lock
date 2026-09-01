import ctypes
import os
import sys

def is_admin():
    return ctypes.windll.shell32.IsUserAnAdmin()

if not is_admin():
    script_path = os.path.abspath(sys.argv[0])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script_path}"', None, 1)
    sys.exit()

# Поиск interception.dll в папке со скриптом
dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "interception.dll")

if not os.path.exists(dll_path):
    print("❌ ОШИБКА: Файл interception.dll не найден!")
    print(f"Поместите его в папку: {os.path.dirname(os.path.abspath(__file__))}")
    input("\nНажмите Enter для выхода...")
    sys.exit()

# Загрузка драйвера
try:
    lib = ctypes.cdll.LoadLibrary(dll_path)
except Exception as e:
    print(f"Критическая ошибка загрузки DLL: {e}")
    input()
    sys.exit()

# Описание структур C++ для Python
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

def main():
    print("Подключение к драйверу ядра...")
    context = lib.interception_create_context()
    if not context:
        print("❌ Ошибка контекста. Убедитесь, что вы перезагрузили ПК после установки драйвера.")
        input()
        sys.exit()

    # Устанавливаем фильтр на перехват всех событий клавиатуры (0xFFFF)
    lib.interception_set_filter(context, is_keyboard, 0xFFFF)
    
    print("\n[УСПЕХ] Драйвер подключен! Нажимайте клавиши на ноутбуке и USB-клавиатуре.")
    print("Для выхода просто закройте это окно.\n")

    stroke = KeyStroke()
    
    try:
        while True:
            # Ждем аппаратный сигнал
            device = lib.interception_wait(context)
            
            if lib.interception_receive(context, device, ctypes.byref(stroke), 1) > 0:
                # 1 - отпускание обычной клавиши, 3 - отпускание расширенной (например, стрелок)
                if stroke.state in (1, 3): 
                    print(f"Отклик от устройства № {device} (Код клавиши: {stroke.code})")
                
                # Обязательно пропускаем пакет дальше в ОС
                lib.interception_send(context, device, ctypes.byref(stroke), 1)
    finally:
        pass # При закрытии окна Windows сама очистит контекст

if __name__ == "__main__":
    main()