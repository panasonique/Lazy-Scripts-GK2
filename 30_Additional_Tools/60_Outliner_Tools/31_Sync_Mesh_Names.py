info = {
    "name": "Sync Names (Obj=Mesh)",
    "description": "Синхронизировать имя меша с объектом (пропуск Read-Only)",
    "icon": "SORTALPHA",
    "type": "button",
    "shortcut": ""
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
