info = {
    "name": "Clean & Remap",
    "description": "Поиск текстур (#-папки) + Ремап на GK_2 + Чистка внешних линков",
    "icon": 'FILE_REFRESH',
    "type": "button",
    "shortcut": ""
}

import bpy
import os
import re

def log(msg):
    print(f"[Lazy Scripts] {msg}")

def find_file_recursive(base_path, filename, filter_hash=False):
    """Рекурсивный поиск файла. Если filter_hash=True, заходит только в папки с '#'"""
    for root, dirs, files in os.walk(base_path):
        if filter_hash:
            # Оставляем только те папки, которые начинаются с #
            dirs[:] = [d for d in dirs if d.startswith("#")]
            # Сбрасываем фильтр для вложенных папок после того, как вошли в #папку
            filter_hash = False 
            
        if filename in files:
            return os.path.join(root, filename)
    return None

def find_addon_texture(filename):
    """Поиск текстуры в директории аддона в папках, начинающихся с '#'"""
    addon_dir = os.path.dirname(__file__) # Путь к текущему файлу скрипта
    # Нам нужно выйти на уровень выше, где лежат папки аддона
    base_addon_path = os.path.dirname(addon_dir) 
    
    # Ищем во всех подпапках аддона, но заходим только в те, что начинаются с #
    for entry in os.listdir(base_addon_path):
        sub_path = os.path.join(base_addon_path, entry)
        if os.path.isdir(sub_path) and entry.startswith("#"):
            found = find_file_recursive(sub_path, filename)
            if found: return found
    return None

def run():
    # 1. Валидация сохранения
    if not bpy.data.is_saved:
        report({'ERROR'}, "Сначала сохраните .blend файл!")
        return

    log("Запуск этапа Clean & Remap...")
    project_dir = os.path.dirname(bpy.data.filepath)
    suffix_re = re.compile(r"\.\d{3}$")
    
    # --- ЭТАП 1: ВОССТАНОВЛЕНИЕ ТЕКСТУР ---
    tex_found = 0
    log("Этап 1: Проверка текстур...")
    for img in bpy.data.images:
        if img.source == 'FILE':
            abs_path = bpy.path.abspath(img.filepath)
            fname = os.path.basename(img.filepath)
            
            # Условие: файл не найден ИЛИ путь ведет "вверх" (//..)
            if not os.path.exists(abs_path) or ".." in img.filepath:
                # Сначала ищем в проекте
                new_p = find_file_recursive(project_dir, fname)
                
                # Если в проекте нет, ищем в папках аддона с префиксом #
                if not new_p:
                    new_p = find_addon_texture(fname)
                
                if new_p:
                    img.filepath = bpy.path.relpath(new_p)
                    img.reload()
                    tex_found += 1
                    log(f"  Текстура восстановлена: {fname}")

    # --- ЭТАП 2: РЕМАП НА GK_2 Library ---
    log("Этап 2: Ремапинг на библиотеку GK_2...")
    main_lib = next((l for l in bpy.data.libraries 
                     if l.filepath.startswith("//") and ".." not in l.filepath and "GK_2 Library" in l.name), None)
    
    remapped_count = 0
    if main_lib:
        lib_path = bpy.path.abspath(main_lib.filepath)
        loc_ng_names = {suffix_re.sub("", ng.name) for ng in bpy.data.node_groups if ng.library is None}
        loc_mat_names = {suffix_re.sub("", m.name) for m in bpy.data.materials if m.library is None}
        
        try:
            with bpy.data.libraries.load(lib_path, link=True) as (data_from, data_to):
                data_to.node_groups = [n for n in data_from.node_groups if n in loc_ng_names]
                data_to.materials = [m for m in data_from.materials if m in loc_mat_names]
        except Exception as e:
            log(f"  Ошибка загрузки библиотеки: {e}")

        linked_ng = {ng.name: ng for ng in bpy.data.node_groups if ng.library == main_lib}
        linked_mat = {m.name: m for m in bpy.data.materials if m.library == main_lib}

        for ng in bpy.data.node_groups:
            if ng.library is None:
                target = linked_ng.get(suffix_re.sub("", ng.name))
                if target: 
                    ng.user_remap(target)
                    remapped_count += 1

        for mat in bpy.data.materials:
            if mat.library is None:
                target = linked_mat.get(suffix_re.sub("", mat.name))
                if target: 
                    mat.user_remap(target)
                    remapped_count += 1
        log(f"  Ремапинг завершен. Заменено объектов: {remapped_count}")
    else:
        log("  Библиотека GK_2 Library не обнаружена в корне проекта.")

    # --- ЭТАП 3: УДАЛЕНИЕ ВНЕШНИХ БИБЛИОТЕК ---
    log("Этап 3: Очистка внешних путей...")
    libs_to_remove = [l for l in bpy.data.libraries if ".." in l.filepath or not l.filepath.startswith("//")]
    libs_deleted = len(libs_to_remove)
    
    for l in libs_to_remove:
        log(f"  Удаление линка: {l.filepath}")
        bpy.data.libraries.remove(l)

    # --- ЭТАП 4: ФИНАЛЬНАЯ ЧИСТКА ---
    log("Этап 4: Глубокая очистка (Purge)...")
    for i in range(3):
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

    # ОТЧЕТ
    report_msg = f"Текстур: {tex_found} | Ремап: {remapped_count} | Удалено линков: {libs_deleted}"
    log(f"Готово! {report_msg}")
    report({'INFO'}, report_msg)
    
    context.area.tag_redraw()

run()

