import bpy
import bmesh

info = {
    "name": "UV Bleed Fix",
    "description": "Сдвиг вертексов граней на границе текстуры по оси X",
    "type": "button",
    "icon": "GRID",
    "shortcut": "Ctrl Shift X"
}

obj = context.active_object

if obj and obj.type == 'MESH':
    if obj.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')

    bm = bmesh.from_edit_mesh(obj.data)
    bm.normal_update() 
    
    grid_step = 0.01
    offset = 0.0001
    precision = 0.00001
    found_count = 0

    for v in bm.verts:
        v.select = False

    for face in bm.faces:
        # 1. Проверка нормали по X
        if abs(face.normal.x) > (1.0 - precision):
            
            # 2. Проверка, что грань плоская по X
            x_coords = [v.co.x for v in face.verts]
            if (max(x_coords) - min(x_coords)) < precision:
                
                # 3. Проверка выравнивания по сетке 0.01
                # Используем round для устранения погрешности float
                current_x = x_coords[0]
                if abs(current_x % grid_step) < precision or abs(grid_step - (current_x % grid_step)) < precision:
                    
                    move_dir = -offset if face.normal.x > 0 else offset
                    
                    for v in face.verts:
                        v.co.x += move_dir
                        v.select = True
                    found_count += 1

    bmesh.update_edit_mesh(obj.data)
    print(f"Lazy Scripts: Сдвинуто граней: {found_count}")
    context.area.tag_redraw()
