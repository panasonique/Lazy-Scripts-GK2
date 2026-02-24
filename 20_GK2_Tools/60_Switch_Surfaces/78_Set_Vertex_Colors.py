import bpy

# Данные для вашего аддона Lazy Scripts
info = {
    "name": "Show All Colors",
    "icon": "GROUP_VCOL",
    "description": "Переключить вывод на Vertex Colors",
    "type": "button"
}

def run():
    # 1. Проверка контекста
    obj = bpy.context.active_object
    if not obj or not obj.active_material:
        # В вашем аддоне можно использовать self.report, но здесь проще так:
        bpy.context.window_manager.popup_menu(lambda s, c: s.label(text="Нет активного материала"), title="Ошибка", icon='ERROR')
        return

    mat = obj.active_material
    if not mat.use_nodes:
        mat.use_nodes = True
        
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # 2. Поиск нод (учитываем, что имена могут содержать .001)
    # Ищем по типу (GROUP) и части имени внутреннего дерева
    source_node = next((n for n in nodes if n.type == 'GROUP' and "SEN Model Debug Set" in n.node_tree.name), None)
    output_node = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL'), None)

    if not source_node:
        print("Нода 'SEN Model Debug Set' не найдена")
        return
    if not output_node:
        print("Нода 'Material Output' не найдена")
        return

    # 3. Поиск сокетов
    # У нод-групп выходы ищутся по имени, заданному внутри группы
    socket_out = source_node.outputs.get("Vertex Colors")
    socket_in = output_node.inputs.get("Surface")

    if socket_out and socket_in:
        # 4. Создание связи
        links.new(socket_out, socket_in)
        # Принудительное обновление интерфейса (иногда нужно в 4.x)
        mat.node_tree.update_tag()
        print(f"Связано: {socket_out.name} -> {socket_in.name}")
    else:
        missing = "Выход" if not socket_out else "Вход"
        print(f"Ошибка: {missing} сокет не найден")

# ВАЖНО: В вашей системе exec() нужно вызвать функцию в конце файла
run()
