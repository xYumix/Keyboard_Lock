import os
import sys
import ctypes
import subprocess

def is_admin():
    """Проверяет, запущен ли скрипт с правами администратора."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_installer():
    """Запускает оригинальный установщик драйвера Interception без скрытых параметров."""
    # Получаем путь к папке, где лежит сам скрипт install_driver.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Формируем путь к файлу install-interception.exe
    installer_path = os.path.join(script_dir, "", "install-interception.exe")
    
    if not os.path.exists(installer_path):
        print(f"Ошибка: Не найден файл {installer_path}")
        print("Убедитесь, что скрипт находится в правильной папке.")
        input("Нажмите Enter для выхода...")
        return

    print("Запуск установщика драйвера Interception...")
    try:
        # Запускаем exe-файл напрямую, оставляя выбор пользователю
        subprocess.run([installer_path, "/install"], check=True)
        print("\nУстановка успешно завершена!")
        print("ПОЖАЛУЙСТА, ПЕРЕЗАГРУЗИТЕ КОМПЬЮТЕР, чтобы изменения вступили в силу.")
    except subprocess.CalledProcessError as e:
        print(f"\nПроизошла ошибка при запуске. Код ошибки: {e.returncode}")
    except Exception as e:
        print(f"\nНепредвиденная ошибка: {e}")
        
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    if is_admin():
        run_installer()
    else:
        print("Запрос прав администратора...")
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            sys.executable, 
            f'"{__file__}"', 
            None, 
            1
        )