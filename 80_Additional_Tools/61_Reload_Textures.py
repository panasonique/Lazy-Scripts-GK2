info = {
    "name": "Reload Textures",
    "icon": "FILE_REFRESH",
    "description": "Обновить все текстуры в проекте с диска",
    "shortcut": "Alt R"
}

import bpy

def run():
    reloaded_count = 0
    
    # 1. Перезагружаем данные с диска
    for img in bpy.data.images:
        # Обновляем только внешние файлы
        if img.source == 'FILE' and img.filepath:
            try:
                img.reload()
                reloaded_count += 1
            except Exception as e:
                print(f"Ошибка обновления {img.name}: {e}")

    # 2. ФОРСИРУЕМ ОБНОВЛЕНИЕ ВЬЮПОРТОВ
    # В Blender 4.x/5.x для обновления текстур нужно перерисовывать области (Areas)
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()

    # 3. Вывод результата в статус-бар (внизу экрана)
    msg = f"Reloaded {reloaded_count} textures"
    print(msg)
    
    # Проверка на наличие context (безопасно для exec)
    if 'bpy' in globals():
        bpy.context.workspace.status_text_set(msg)

# Запуск для архитектуры Lazy Scripts
run()
