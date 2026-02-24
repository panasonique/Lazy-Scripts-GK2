import bpy

info = {
    "name": "Check Normals",
    "icon": "NORMALS_FACE",
    "type": "button",
    "description": "Переключить вывод на Check Normals"
}

def run():
    # Проверка на наличие активного объекта и материала
    obj = bpy.context.active_object
    if not obj or not obj.active_material:
        return

    mat = obj.active_material
    nodes = mat.node_tree.nodes
    
    # Поиск основной ноды отладки и вывода материала
    src = next((n for n in nodes if n.type == 'GROUP' and "SEN Model Debug Set" in n.node_tree.name), None)
    out = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL'), None)
    
    if src and out:
        # Соединяем сокет Check Normals с входом Surface
        # Убедитесь, что в нод-группе имя сокета точно "Check Normals"
        socket_out = src.outputs.get("Check Normals")
        socket_in = out.inputs.get("Surface")
        
        if socket_out and socket_in:
            mat.node_tree.links.new(socket_out, socket_in)

run()
