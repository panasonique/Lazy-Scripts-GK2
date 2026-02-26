info = {
    "name": "Clean & Remap",
    "description": "Поиск текстур + Ремап на библиотеку GK_2 Library.blend + Удаление внешних библиотек после Append",
    "icon": 'FILE_REFRESH',
    "type": "button",
    "shortcut": ""
}

import bpy
import os
import re

def find_file_recursive(base_path, filename):
    """Рекурсивный поиск файла в подпапках"""
    for root, dirs, files in os.walk(base_path):
        if filename in files:
            return os.path.join(root, filename)
    return None

def run():
    # 1. Валидация сохранения
    if not bpy.data.is_saved:
        report({'ERROR'}, "Сначала сохраните .blend файл!")
        return

    project_dir = os.path.dirname(bpy.data.filepath)
    suffix_re = re.compile(r"\.\d{3}$")
    
    # --- ЭТАП 1: ВОССТАНОВЛЕНИЕ ТЕКСТУР (Умный поиск) ---
    tex_found = 0
    for img in bpy.data.images:
        # Работаем только с внешними файлами (не Render/Viewer)
        if img.source == 'FILE':
            abs_path = bpy.path.abspath(img.filepath)
            
            # Проверяем, существует ли файл. Если нет — ищем замену.
            if not os.path.exists(abs_path):
                fname = os.path.basename(img.filepath)
                new_p = find_file_recursive(project_dir, fname)
                
                if new_p:
                    # Устанавливаем относительный путь
                    img.filepath = bpy.path.relpath(new_p)
                    img.reload()
                    tex_found += 1

    # --- ЭТАП 2: ПОИСК И РЕМАП НА GK_2 ---
    # Находим библиотеку БЕЗ ".." (строго в корне проекта или вложенных папках)
    main_lib = next((l for l in bpy.data.libraries 
                     if l.filepath.startswith("//") and ".." not in l.filepath and "GK_2 Library" in l.name), None)
    
    remapped_count = 0
    if main_lib:
        lib_path = bpy.path.abspath(main_lib.filepath)
        
        # Собираем имена локальных данных, которые нужно заменить на библиотечные
        loc_ng_names = {suffix_re.sub("", ng.name) for ng in bpy.data.node_groups if ng.library is None}
        loc_mat_names = {suffix_re.sub("", m.name) for m in bpy.data.materials if m.library is None}
        
        # Подтягиваем оригиналы из библиотеки (Link)
        try:
            with bpy.data.libraries.load(lib_path, link=True) as (data_from, data_to):
                data_to.node_groups = [n for n in data_from.node_groups if n in loc_ng_names]
                data_to.materials = [m for m in data_from.materials if m in loc_mat_names]
        except: pass

        # Создаем маппинг залинкованных данных
        linked_ng = {ng.name: ng for ng in bpy.data.node_groups if ng.library == main_lib}
        linked_mat = {m.name: m for m in bpy.data.materials if m.library == main_lib}

        # Ремапим нодовые группы
        for ng in bpy.data.node_groups:
            if ng.library is None:
                target = linked_ng.get(suffix_re.sub("", ng.name))
                if target: 
                    ng.user_remap(target)
                    remapped_count += 1

        # Ремапим материалы
        for mat in bpy.data.materials:
            if mat.library is None:
                target = linked_mat.get(suffix_re.sub("", mat.name))
                if target: 
                    mat.user_remap(target)
                    remapped_count += 1

    # --- ЭТАП 3: УДАЛЕНИЕ ВНЕШНИХ БИБЛИОТЕК (Чистка ссылок) ---
    # Удаляем всё, что ведет за пределы проекта (содержит "..") или абсолютные пути (C:\)
    libs_to_remove = [l for l in bpy.data.libraries if ".." in l.filepath or not l.filepath.startswith("//")]
    libs_deleted = len(libs_to_remove)
    
    for l in libs_to_remove:
        bpy.data.libraries.remove(l)

    # --- ЭТАП 4: ФИНАЛЬНАЯ ГЛУБОКАЯ ЧИСТКА ---
    # 3 итерации гарантируют удаление цепочек зависимостей
    for i in range(3):
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

    # ИТОГОВЫЙ ОТЧЕТ В СТАТУС-БАР
    report_msg = f"Текстур: {tex_found} | Ремап: {remapped_count} | Удалено линков: {libs_deleted}"
    report({'INFO'}, report_msg)
    
    context.area.tag_redraw()

run()
