info = {
    "name": "Join & Apply",
    "description": "Конвертировать в меш, объединить и применить трансформации",
    "icon": "AUTOMERGE_ON",
    "type": "button",
    "shortcut": ""
}

# Работаем в объектном режиме
if context.active_object:
    # 1. Конвертируем все выделенные объекты в Mesh (применяет модификаторы)
    bpy.ops.object.convert(target='MESH')
    
    # 2. Объединяем выделенные объекты в один активный
    bpy.ops.object.join()
    
    # 3. Применяем все трансформации (Location, Rotation, Scale)
    # После этого Scale станет 1.0, а Rotation 0.0
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    context.area.tag_redraw()
