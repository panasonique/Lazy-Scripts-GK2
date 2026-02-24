info = {
    "name": "Z –Step",
    "description": "Сдвигает выделенное на шаг из prop_id. Работает с Undo.",
    "icon": "AXIS_TOP",
    "prop_id": "move_step_2"
}

import bpy

# Динамическое получение значения: 
# Мы смотрим в info["prop_id"], получаем строку "move_step_2" 
# и ищем поле с таким именем внутри объекта props
step = getattr(props, info.get("prop_id"), 0.0)

# Коэффициенты смещения
step_to_pixel = (0, 0, step * -0.0166666)

# Вызов трансформации
bpy.ops.transform.translate(
    value=step_to_pixel, 
    orient_type='GLOBAL', 
    mirror=True
)