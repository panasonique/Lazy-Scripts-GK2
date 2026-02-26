info = {
    "name": "Init Material",
    "description": "Создает локальный материал и синхронизирует текстуру с GN модификатором",
    "icon": "MATERIAL",
    "type": "button",
    "shortcut": ""
}

import os
import bpy

def run():
    # 1. Проверяем, сохранен ли .blend файл
    if not bpy.data.is_saved:
        print("Ошибка: Сначала сохраните .blend файл!")
        return

    obj = bpy.context.active_object
    source_mat = bpy.data.materials.get("#Default Material")

    if not (obj and obj.type == 'MESH' and source_mat):
        if not source_mat: print("Ошибка: '#Default Material' не найден.")
        return

    target_name = obj.name
    
    # 2. Пересоздание материала
    old_mat = bpy.data.materials.get(target_name)
    if old_mat:
        bpy.data.materials.remove(old_mat, do_unlink=True)

    new_mat = source_mat.copy()
    new_mat.name = target_name
    
    if obj.data.materials:
        obj.data.materials[0] = new_mat
    else:
        obj.data.materials.append(new_mat)

    # 3. Работа с текстурой
    project_dir = os.path.dirname(bpy.data.filepath)
    textures_dir = os.path.join(project_dir, "#Textures")
    img_name = f"{target_name}.png"
    img_path = os.path.join(textures_dir, img_name)

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
    if os.path.exists(img_path):
        old_img = bpy.data.images.get(img_name)
        if old_img:
            bpy.data.images.remove(old_img, do_unlink=True)
        
        try:
            loaded_image = bpy.data.images.load(img_path)
            tex_node.image = loaded_image
            loaded_image.reload()
        except Exception as e:
            print(f"Ошибка загрузки: {e}")

    # --- 4. СИНХРОНИЗАЦИЯ С GEOMETRY NODES (Метод прямого перебора ID-блоков) ---
    gn_mod = next((m for m in obj.modifiers if m.type == 'NODES' and m.node_group), None)
    
    if gn_mod:
        print(f"--- Синхронизация с {gn_mod.name} ---")
        
        # 1. Подготовка картинки (как кнопка Open/New)
        img_name = f"{obj.name}.png"
        image = bpy.data.images.get(img_name)
        if not image:
            project_dir = os.path.dirname(bpy.data.filepath)
            img_path = os.path.join(project_dir, "#Textures", img_name)
            image = bpy.data.images.load(img_path) if os.path.exists(img_path) else bpy.data.images.new(img_name, 1024, 1024)

        # 2. ПОИСК ПО "СКРЫТЫМ" КЛЮЧАМ (Обход всех ошибок API 4.x)
        # Мы ищем идентификатор сокета, который называется 'Texture Image'
        target_id = None
        
        # Сначала пробуем найти идентификатор через саму нодовую группу (через дерево)
        # В 4.x у дерева есть входы, доступные через .inputs (в некоторых сборках еще осталось)
        # или через прямое перечисление ID-данных
        try:
            # Прямой перебор структуры сокетов (без слова items)
            for i in range(len(gn_mod.node_group.interface.items_tree)):
                item = gn_mod.node_group.interface.items_tree[i]
                if item.name == "Texture Image":
                    target_id = item.identifier
                    break
        except:
            # Если дерево заблокировано намертво, ищем по именам в самом модификаторе
            for key in gn_mod.keys():
                if "Texture Image" in key or "Input" in key:
                    target_id = key
                    break

        # 3. ПРИНУДИТЕЛЬНАЯ ЗАПИСЬ (Аналог выбора из списка)
        if target_id and image:
            # Запись по системному ключу инициализирует поле в "свежем" модификаторе
            gn_mod[target_id] = image
            if tex_node:
                tex_node.image = image
            print(f"УСПЕХ: Картинка '{image.name}' назначена в сокет '{target_id}'")
        else:
            # Если поле СОВСЕМ не найдено (модификатор только что добавлен и пуст)
            # Мы пробуем записать в самый первый подходящий по типу слот 'Socket_1' и т.д.
            print("ВНИМАНИЕ: Поле не найдено. Попробуйте вручную один раз выбрать картинку в GN.")

    bpy.context.area.tag_redraw()



    bpy.context.area.tag_redraw()

run()
