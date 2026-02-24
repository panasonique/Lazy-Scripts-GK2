info = {
    "name": "Flatten Y",
    "description": "Выравнивает выделенные вертексы по оси Y",
    "icon": "NONE",
    "type": "button"
}

import bpy

obj = context.active_object

if obj and obj.type == 'MESH' and obj.mode == 'EDIT':
    # value=(X, Y, Z). Ставим 0 для Y.
    bpy.ops.transform.resize(
        value=(1, 0, 1), 
        orient_type='GLOBAL', 
        constraint_axis=(False, True, False), # Ограничиваем осью Y
        mirror=False, 
        use_proportional_edit=False
    )
    context.area.tag_redraw()
else:
    print("Lazy Scripts: Нужно быть в Edit Mode")
