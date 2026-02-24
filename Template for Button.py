info = {
    "name": "Название кнопки",
    "icon": "CUBE",        # Иконка из Blender API
    "description": "Описание при наведении",
    "type": "button",      # Тип по умолчанию
    "shortcut": "Alt Shift X"
}

import bpy

def run():
    # ВАШ КОД ЗДЕСЬ
    print("Скрипт выполнен")
    # Пример: report({'INFO'}, "Готово!") — если проброшен report

if __name__ == "__main__":
    run()
