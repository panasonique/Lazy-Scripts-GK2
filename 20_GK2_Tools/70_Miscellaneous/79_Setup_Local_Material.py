info = {
    "name": "Init Material",
    "description": "Глубокий поиск текстур в папках # и их подпапках",
    "icon": 'MATERIAL',
    "type": "button",
    "shortcut": ""
}

import os
import bpy

def find_texture_deep(base_path, filename):
    """
    Сканирует корень проекта. Если находит папку на #, 
    полностью обыскивает её содержимое (включая все подпапки).
    """
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path) and item.startswith("#"):
            # Нашли входную точку (например, #Gardening), ищем внутри неё всё
            for root, dirs, files in os.walk(item_path):
                if filename in files:
                    return os.path.join(root, filename)
    return None

def run():
    # 1. Валидация окружения
    if not bpy.data.is_saved:
        report({'ERROR'}, "Сначала сохраните .blend файл!")
        return

    obj = context.active_object 
    source_mat = bpy.data.materials.get("#Default Material")

    if not (obj and obj.type == 'MESH'):
        report({'WARNING'}, "Выберите меш-объект")
        return
    
    if not source_mat:
        report({'ERROR'}, "Материал '#Default Material' не найден")
        return

    # 2. Пересоздание локального материала
    target_name = obj.name
    old_mat = bpy.data.materials.get(target_name)
    if old_mat:
        bpy.data.materials.remove(old_mat, do_unlink=True)

    new_mat = source_mat.copy()
    new_mat.name = target_name
    
    if obj.data.materials:
        obj.data.materials[0] = new_mat
    else:
        obj.data.materials.append(new_mat)

    # 3. Поиск текстуры по маске f"{obj.name}.png"
    project_dir = os.path.dirname(bpy.data.filepath)
    img_name = f"{target_name}.png"
    img_path = find_texture_deep(project_dir, img_name)

    new_mat.use_nodes = True
    nodes = new_mat.node_tree.nodes
    links = new_mat.node_tree.links

    tex_node = next((n for n in nodes if n.type == 'TEX_IMAGE'), None)
    if not tex_node:
        tex_node = nodes.new('ShaderNodeTexImage')
        tex_node.location = (-300, 300)
        bsdf = nodes.get("Principled BSDF")
        if bsdf:
            links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])

    loaded_image = None
    if img_path:
        # Репорт найденного пути
        relative_path = os.path.relpath(img_path, project_dir)
        report({'INFO'}, f"Найдено: {relative_path}")
        
        # Обновляем текстуру в памяти
        old_img = bpy.data.images.get(img_name)
        if old_img:
            bpy.data.images.remove(old_img, do_unlink=True)
        
        try:
            loaded_image = bpy.data.images.load(img_path)
            tex_node.image = loaded_image
        except Exception as e:
            report({'ERROR'}, f"Ошибка загрузки: {e}")
    else:
        report({'WARNING'}, f"Файл {img_name} не найден в папках #...")

    # 4. Синхронизация с Geometry Nodes (Blender 4.x)
    gn_mod = next((m for m in obj.modifiers if m.type == 'NODES' and m.node_group), None)
    
    if gn_mod:
        image = loaded_image if loaded_image else bpy.data.images.get(img_name)
        if not image:
            image = bpy.data.images.new(img_name, 1024, 1024)

        target_id = None
        try:
            # Ищем сокет по имени в интерфейсе нод-группы
            for item in gn_mod.node_group.interface.items_tree:
                if item.name == "Texture Image":
                    target_id = item.identifier
                    break
        except:
            # Фолбэк для прямой записи в кастомные свойства модификатора
            for key in gn_mod.keys():
                if "Texture Image" in key:
                    target_id = key
                    break

        if target_id:
            gn_mod[target_id] = image
            if tex_node:
                tex_node.image = image

    context.area.tag_redraw()

run()
