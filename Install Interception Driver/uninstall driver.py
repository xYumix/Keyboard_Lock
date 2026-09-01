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
    """Запускает установщик драйвера Interception с нужными параметрами."""
    # Получаем путь к папке, где лежит сам скрипт install_driver.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Формируем путь к файлу install-interception.exe
    installer_path = os.path.join(script_dir, "install-interception.exe")

    if not os.path.exists(installer_path):
        print(f"Ошибка: Не найден файл {installer_path}")
        print("Убедитесь, что скрипт находится в правильной папке.")
        input("Нажмите Enter для выхода...")
        return

    print("Запуск удаления драйвера Interception...")
    try:
        # Запускаем exe-файл с флагом /install
        subprocess.run([installer_path, "/uninstall"], check=True)
        print("\nУдаление успешно завершено!")
        print("ПОЖАЛУЙСТА, ПЕРЕЗАГРУЗИТЕ КОМПЬЮТЕР, чтобы изменения вступили в силу.")
    except subprocess.CalledProcessError as e:
        print(f"\nПроизошла ошибка при установке. Код ошибки: {e.returncode}")
    except Exception as e:
        print(f"\nНепредвиденная ошибка: {e}")
        
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    if is_admin():
        # Если права есть, запускаем установку
        run_installer()
    else:
        # Если прав нет, перезапускаем скрипт с запросом прав администратора
        print("Запрос прав администратора...")
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            sys.executable, 
            f'"{__file__}"', 
            None, 
            1
        )