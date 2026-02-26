info = {
    "name": "Select Close Verts",
    "icon": "VERTEXSEL",
    "description": "Выделить вершины ближе 0.00001",
    "shortcut": "Alt D" 
}

import bpy
import bmesh

def run():
    obj = bpy.context.active_object
    if not obj or obj.type != 'MESH':
        return

    # 1. Переход в Edit Mode
    if obj.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    
    # Устанавливаем режим выделения — Вершины
    bpy.context.tool_settings.mesh_select_mode = (True, False, False)

    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)
    bm.verts.ensure_lookup_table()
    
    # --- ИСПРАВЛЕНИЕ: Полный сброс выделения ---
    # Снимаем выделение со всего (вершины, ребра, грани)
    for v in bm.verts: v.select = False
    for e in bm.edges: e.select = False
    for f in bm.faces: f.select = False
    
    size = len(bm.verts)
    if size < 2: 
        bmesh.update_edit_mesh(mesh)
        return

    # 2. Построение KD-дерева
    from mathutils import kdtree
    kd = kdtree.KDTree(size)
    for i, v in enumerate(bm.verts):
        kd.insert(v.co, i)
    kd.balance()

    # 3. Поиск пар вершин
    dist_threshold = 0.00001
    selected_count = 0
    
    for v in bm.verts:
        # Ищем соседей в радиусе
        neighbors = kd.find_range(v.co, dist_threshold)
        
        # Если найдено больше одной точки (сама вершина + кто-то рядом)
        if len(neighbors) > 1:
            v.select = True
            selected_count += 1

    # 4. Финализация
    if selected_count > 0:
        # Обновляем выделение связанных элементов
        bm.select_flush(True)
        msg = f"Found {selected_count} close vertices"
    else:
        # Принудительно сбрасываем выделение в интерфейсе, если ничего не нашли
        bm.select_flush(False)
        msg = "No close vertices found"

    # Важно: применяем изменения обратно в меш
    bmesh.update_edit_mesh(mesh)
    
    print(msg)
    # Выводим сообщение в статус-бар Blender
    if hasattr(bpy.context.workspace, "status_text_set"):
        bpy.context.workspace.status_text_set(msg)

# Запуск
run()
