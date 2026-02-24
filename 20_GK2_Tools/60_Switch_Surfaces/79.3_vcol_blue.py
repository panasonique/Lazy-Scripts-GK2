import bpy

info = {"name": "B", "icon": "NONE", "type": "button", "description": "Выход Blue -> Surface"}

def run():
    mat = bpy.context.active_object.active_material
    nodes = mat.node_tree.nodes
    
    src = next((n for n in nodes if n.type == 'GROUP' and "SEN Model Debug Set" in n.node_tree.name), None)
    out = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL'), None)
    
    if src and out:
        mat.node_tree.links.new(src.outputs.get("Vertex Colors: Blue"), out.inputs.get("Surface"))

run()
