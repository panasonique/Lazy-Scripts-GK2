info = {
    "name": "Verts → Empties",
    "description": "Создать пустышки (Empty) в мировых координатах выделенных вершин",
    "icon": "EMPTY_AXIS",
    "type": "button",
    "shortcut": ""
}

import bmesh

obj = context.active_object
if obj and obj.type == 'MESH' and obj.mode == 'EDIT':
    bm = bmesh.from_edit_mesh(obj.data)
    
    # Матрица мира для перевода локальных координат в глобальные
    matrix = obj.matrix_world
    
    # Собираем мировые координаты выделенных вершин
    points = [matrix @ v.co for v in bm.verts if v.select]
    
    # Создаем пустышки
    for p in points:
        # 'None' в аргументе data создает именно Empty
        empty_obj = bpy.data.objects.new("VertexPoint", None)
        context.collection.objects.link(empty_obj)
        empty_obj.location = p
        
    # Обновляем вьюпорт
    context.area.tag_redraw()
