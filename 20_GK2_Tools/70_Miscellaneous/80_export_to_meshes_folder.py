import bpy
import os
import re

info = {
    "name": "Export to #Meshes",
    "icon": "EXPORT",
    "description": "Имя из [...] активной коллекции объекта",
    "type": "button"
}

# Используем bpy.data.objects для надежности
for obj in context.scene.objects:
    # Работаем только с мешами, у которых есть данные
    if obj.type == 'MESH' and obj.data:
        # Проверяем: имя уже не совпадает и данные НЕ являются библиотечными (Read-Only)
        if obj.data.name != obj.name and not obj.data.is_library_indirect:
            try:
                # Пытаемся переименовать данные меша
                obj.data.name = obj.name
            except (AttributeError, RuntimeError):
                # Если Blender все равно блокирует имя (например, из-за специфических связей), просто идем дальше
                continue

# Обновляем Outliner и вьюпорт для отображения изменений
for area in context.screen.areas:
    if area.type in {'OUTLINER', 'VIEW_3D'}:
        area.tag_redraw()


def run():
    # 1. Базовые проверки
    if not bpy.data.is_saved:
        bpy.context.window_manager.popup_menu(lambda s, c: s.label(text="Сохраните проект!"), title="Ошибка", icon='ERROR')
        return

    active_obj = bpy.context.view_layer.objects.active
    if not active_obj:
        return

    # 2. Поиск подходящей коллекции среди всех, где состоит объект
    target_filename = None
    coll_name_found = ""
    
    for coll in active_obj.users_collection:
        match = re.search(r'\[(.+?)\]', coll.name)
        if match:
            target_filename = match.group(1).strip()
            coll_name_found = coll.name
            break # Берем первую найденную с скобками
    
    if not target_filename:
        msg = f"В коллекциях объекта '{active_obj.name}' не найдены [brackets]"
        bpy.context.window_manager.popup_menu(lambda s, c: s.label(text=msg), title="Ошибка имени", icon='ERROR')
        return

    # 3. Формирование пути
    if not target_filename.lower().endswith(".fbx"):
        target_filename += ".fbx"

    blend_dir = os.path.dirname(bpy.data.filepath)
    meshes_dir = os.path.join(blend_dir, "#Meshes")
    
    if not os.path.exists(meshes_dir):
        bpy.context.window_manager.popup_menu(lambda s, c: s.label(text="Папка #Meshes не найдена!"), title="Ошибка", icon='ERROR')
        return

    file_path = os.path.join(meshes_dir, target_filename)

    # 4. Экспорт с вашими настройками (перезапись автоматическая)
    try:
        bpy.ops.export_scene.fbx(
            filepath=file_path,
            use_selection=True,
            object_types={'MESH', 'EMPTY'},
            global_scale=2.0,
            apply_scale_options='FBX_SCALE_ALL',
            axis_forward='-Y',
            axis_up='Z',
            use_space_transform=True,
            apply_unit_scale=True,
            bake_space_transform=True,
            mesh_smooth_type='OFF',
            use_mesh_modifiers=True,
            add_leaf_bones=True,
            primary_bone_axis='Y',
            secondary_bone_axis='X',
            armature_nodetype='NULL',
            bake_anim=False
        )
        # Уведомление в системной строке
        bpy.context.workspace.status_text_set(f"Done: {target_filename} (from {coll_name_found})")
        print(f"Exported to: {file_path}")
        
    except Exception as e:
        print(f"Export Error: {e}")

run()
