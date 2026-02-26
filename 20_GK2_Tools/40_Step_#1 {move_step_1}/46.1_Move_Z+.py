info = {
    "name": "Z +Step",
    "description": "Сдвигает выделенное на заданный шаг. Работает с Undo.",
    "icon": "AXIS_TOP",
    "prop_id": "move_step_1"
}

import bpy

# Динамическое получение значения: 
# Мы смотрим в info["prop_id"], получаем строку "move_step_2" 
# и ищем поле с таким именем внутри объекта props
step = getattr(props, info.get("prop_id"), 0.0)

# Коэффициенты смещения
step_to_pixel = (
    0, #step * 0.01
    0,  #step * 0.0125
    step * 0.0166666 #step * 0.0166666
)

# Вызываем оператор трансформации. 
# В контексте аддона (MY_OT_RunExternalScript) это действие будет записано в историю.
bpy.ops.transform.translate(
    value=step_to_pixel, 
    orient_type='GLOBAL', 
    constraint_axis=(False, False, False), 
    mirror=True, 
    use_proportional_edit=False, 
    snap=False
)

# НИКАКИЕ bmesh.update_edit_mesh и ob.data.update() НЕ НУЖНЫ.
# Оператор bpy.ops.transform сам заботится об обновлении данных и Undo.
