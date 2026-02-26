import bpy

info = {"name": "Textured View", "icon": "TEXTURE", "type": "button", "description": "SEN Overlay Color -> Surface"}

def run():
    mat = bpy.context.active_object.active_material
    nodes = mat.node_tree.nodes
    
    # Ищем ноду SEN Overlay Color
    src = next((n for n in nodes if n.type == 'GROUP' and "SEN Overlay Color" in n.node_tree.name), None)
    out = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL'), None)
    
    if src and out:
        # Соединяем сокет Overlayed с входом Surface
        mat.node_tree.links.new(src.outputs.get("Overlayed"), out.inputs.get("Surface"))

run()
