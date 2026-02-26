info = {
    "name": "Название кнопки",
    "icon": "CUBE",        # Иконка из Blender API
    "description": "Описание при наведении",
    "type": "button",      # Тип по умолчанию
    "prop_id": "int_value",
    "shortcut": "Alt Shift X"
}

import bpy
# Динамическое получение значения: 
# Мы смотрим в info["prop_id"], получаем строку "int_value" 
# и ищем поле с таким именем внутри объекта props
var = getattr(props, info.get("prop_id"), 0.0)

def run():
    # ВАШ КОД ЗДЕСЬ
    print(f"Скрипт выполнен. Значение int_value: {var}")
    # Пример: report({'INFO'}, "Готово!") — если проброшен report

if __name__ == "__main__":
    run()

