info = {
    "name": "Round to Pixel",
    "description": "Создает обезьяну и настраивает свет. Работает с Undo.", # Текст подсказки
    "shortcut": "Alt X",  # ТАК ПРОСТО!
    "icon": "SNAP_GRID",
    "prop_id": "move_step"
}

import bpy
import bmesh

# Получаем объект и bmesh
ob = bpy.context.active_object

# Проверка, что мы в Edit Mode и объект — меш
if ob and ob.type == 'MESH' and ob.mode == 'EDIT':
    bm = bmesh.from_edit_mesh(ob.data)

    # Оптимизация: берем только выделенные вертексы сразу
    selected_verts = [v for v in bm.verts if v.select]

    for v in selected_verts:
        # Округление X (шаг 0.01)
        v.co.x = round(v.co.x / 0.01) * 0.01
        
        # Округление Y (шаг 0.0125)
        v.co.y = round(v.co.y / 0.0125) * 0.0125
        
        # Округление Z (шаг 1/60 или 0.01666...)
        # Использование дроби 1/60 точнее, чем десятичная дробь
        v.co.z = round(v.co.z / (1/60)) * (1/60)

    # КРИТИЧЕСКИ ВАЖНО ДЛЯ UNDO:
    # Обновляем меш, чтобы Blender увидел изменения
    bmesh.update_edit_mesh(ob.data)
    
    # Сообщаем Blender, что данные меша изменились (для стека Undo)
    ob.data.update()

    print(f"Сетка выровнена для {len(selected_verts)} вершин")
else:
    print("Объект должен быть в режиме редактирования (Edit Mode)")
