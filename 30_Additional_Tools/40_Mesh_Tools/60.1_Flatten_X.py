info = {
    "name": "Flatten X",
    "description": "Выравнивает выделенные вертексы по оси X",
    "icon": "NONE",
    "type": "button"
}

import bpy

# Проверка контекста: работаем только в Edit Mode и только с Mesh
obj = context.active_object

if obj and obj.type == 'MESH' and obj.mode == 'EDIT':
    # Выравнивание по X: масштаб по X ставим в 0, по остальным осям 1
    # value=(X, Y, Z)
    bpy.ops.transform.resize(
        value=(0, 1, 1), 
        orient_type='GLOBAL', 
        constraint_axis=(True, False, False), # Ограничиваем действие осью X
        mirror=False, 
        use_proportional_edit=False
    )
    
    # Принудительно обновляем вьюпорт
    context.area.tag_redraw()
else:
    # Опционально: вывод сообщения в консоль, если режим не тот
    print("Lazy Scripts: Для выравнивания нужно быть в Edit Mode")
