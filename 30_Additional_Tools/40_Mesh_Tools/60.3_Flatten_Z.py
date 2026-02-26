info = {
    "name": "Flatten Z",
    "description": "Выравнивает выделенные вертексы по оси Z",
    "icon": "NONE",
    "type": "button"
}

import bpy

obj = context.active_object

if obj and obj.type == 'MESH' and obj.mode == 'EDIT':
    # value=(X, Y, Z). Ставим 0 для Z.
    bpy.ops.transform.resize(
        value=(1, 1, 0), 
        orient_type='GLOBAL', 
        constraint_axis=(False, False, True), # Ограничиваем осью Z
        mirror=False, 
        use_proportional_edit=False
    )
    context.area.tag_redraw()
else:
    print("Lazy Scripts: Нужно быть в Edit Mode")
