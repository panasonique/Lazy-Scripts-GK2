info = {
    "name": "Радиус поиска",
    "type": "input_float", # или input_int / input_custom
    "prop_id": "my_unique_radius", # Уникальный ID в коллекции
    "default": 1.0,
    "min": 0.0,
    "max": 100.0,
    "description": "Лимиты проверяются внутри скрипта"
}

import bpy

def run():
    # Получаем доступ к значению
    prop = context.scene.my_addon_vars.get(info['prop_id'])
    if not prop: return

    # Ручной Clamp (так как в UI лимиты отключены для фикса TypeError)
    if prop.value < info['min']: prop.value = info['min']
    if prop.value > info['max']: prop.value = info['max']
    
    val = prop.value
    print(f"Используем значение: {val}")

if __name__ == "__main__":
    run()
