info = {
    "name": "Step Value 1 (px)",
    "description": "Значение на которое работает сдвиг в пикселях (px)",
    "type": "input_custom",
    "prop_id": "move_step_1",
    "default": 1.0,
    "min": 0.0,
    "max": 192.0,
    "icon": "SETTINGS"
}

import bpy

prop_item = context.scene.my_addon_vars.get(info['prop_id'])

if prop_item:
    val = prop_item.value
    # 1. Лимиты теперь проверяются в update_step_logic аддона автоматически, 
    # но можно оставить для страховки или если нужно немедленное отражение.
    
    # 2. ХИТРОЕ ОКРУГЛЕНИЕ: только здесь
    if val > 1.0 or val < -1.0:
        new_val = float(round(val))
        if prop_item.value != new_val:
            prop_item.value = new_val
    
    # Теперь при значении 0.5 оно НЕ превратится в 1.0 или 0.0
    print(f"Актуальный шаг: {prop_item.value}")
