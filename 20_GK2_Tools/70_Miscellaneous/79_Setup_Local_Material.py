info = {
    "name": "Init Material",
    "description": "Поиск текстур в любых папках '#' и синхронизация с GN",
    "icon": 'MATERIAL',
    "type": "button",
    "shortcut": ""
}

import os
import bpy

def find_texture_recursive(base_path, filename):
    """Рекурсивно ищет файл в папках, начинающихся с #"""
    for root, dirs, files in os.walk(base_path):
        # Оставляем для обхода только те папки, которые начинаются с #
        # (Проверяем только текущий уровень dirs, чтобы os.walk шел дальше)
        dirs[:] = [d for d in dirs if d.startswith("#")]
        
        if filename in files:
            return os.path.join(root, filename)
    return None

def run():
    if not bpy.data.is_saved:
        report({'ERROR'}, "Сначала сохраните .blend файл!")
        return

    obj = context.active_object # Используем проброшенный context из аддона
    source_mat = bpy.data.materials.get("#Default Material")

    if not (obj and obj.type == 'MESH'):
        return
    
    if not source_mat:
        report({'ERROR'}, "'#Default Material' не найден.")
        return

    target_name = obj.name
    
    # --- 1. Работа с материалом ---
    old_mat = bpy.data.materials.get(target_name)
    if old_mat:
        bpy.data.materials.remove(old_mat, do_unlink=True)

    new_mat = source_mat.copy()
    new_mat.name = target_name
    
    if obj.data.materials:
        obj.data.materials[0] = new_mat
    else:
        obj.data.materials.append(new_mat)

    # --- 2. Поиск текстуры (Новая логика) ---
    project_dir = os.path.dirname(bpy.data.filepath)
    img_name = f"{target_name}.png"
    img_path = find_texture_recursive(project_dir, img_name)

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
        # Очистка старой версии из памяти Blender
        old_img = bpy.data.images.get(img_name)
        if old_img:
            bpy.data.images.remove(old_img, do_unlink=True)
        
        try:
            loaded_image = bpy.data.images.load(img_path)
            tex_node.image = loaded_image
            loaded_image.reload()
            print(f"Найдено: {img_path}")
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
    else:
        print(f"Файл {img_name} не найден ни в одной папке #...")

    # --- 3. Синхронизация с Geometry Nodes ---
    gn_mod = next((m for m in obj.modifiers if m.type == 'NODES' and m.node_group), None)
    
    if gn_mod and (loaded_image or img_path):
        # Если картинка не была загружена выше (не было файла), создаем пустую
        image = loaded_image
        if not image:
            image = bpy.data.images.new(img_name, 1024, 1024)

        target_id = None
        try:
            # Поиск идентификатора сокета в 4.x
            for item in gn_mod.node_group.interface.items_tree:
                if item.name == "Texture Image":
                    target_id = item.identifier
                    break
        except:
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
