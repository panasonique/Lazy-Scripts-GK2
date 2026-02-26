info = {
    "name": "Step Value 2 (px)",
    "description": "Значение на которое работает сдвиг в пикселях (px)",
    "type": "input_custom", # Оставляем метку для интерфейса
    "prop_id": "move_step_2",
    "default": 24.0,
    "min": 0.0,
    "max": 192.0,
    "icon": "SETTINGS"
}

import bpy

# Получаем текущее значение напрямую из коллекции сцены
prop_item = context.scene.my_addon_vars.get(info['prop_id'])

if prop_item:
    val = prop_item.value
    
    # ПРОВЕРКА ЛОГИКИ:
    if val > 1.0 or val < -1.0:
        # Если вышли за пределы 1, округляем до целого
        new_val = float(round(val))
        if prop_item.value != new_val:
            prop_item.value = new_val
    
    print(f"Актуальный шаг: {prop_item.value}")