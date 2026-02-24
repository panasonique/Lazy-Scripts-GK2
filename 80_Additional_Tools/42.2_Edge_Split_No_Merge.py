info = {
    "name": "Line Split (Separate)",
    "description": "Разрезать ребра в точках пересечения без склейки вершин",
    "icon": "EDGESEL",
    "type": "button",
    "shortcut": ""
}

import bmesh
from mathutils.geometry import intersect_line_line

obj = context.active_object
if obj and obj.type == 'MESH' and obj.mode == 'EDIT':
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    bm.edges.ensure_lookup_table()
    
    edges = [e for e in bm.edges if e.select]
    precision = 0.00001 

    # 1. Собираем все точки пересечения для каждого ребра отдельно
    to_split = [] # Список кортежей (ребро, точка)

    for i in range(len(edges)):
        for j in range(i + 1, len(edges)):
            e1, e2 = edges[i], edges[j]
            v1_a, v1_b = e1.verts[0].co, e1.verts[1].co
            v2_a, v2_b = e2.verts[0].co, e2.verts[1].co
            
            res = intersect_line_line(v1_a, v1_b, v2_a, v2_b)
            if res:
                p1, p2 = res
                if (p1 - p2).length < precision:
                    intersect_pt = (p1 + p2) / 2
                    
                    def is_on_seg(pt, s, e):
                        return (pt - s).length + (pt - e).length < (s - e).length + precision
                    
                    if is_on_seg(intersect_pt, v1_a, v1_b) and is_on_seg(intersect_pt, v2_a, v2_b):
                        # Добавляем задание на разрез для обоих ребер отдельно
                        to_split.append((e1, intersect_pt))
                        to_split.append((e2, intersect_pt))

    # 2. Выполняем разрезы
    # Сортируем по ребрам, чтобы не терять ссылки при итерации
    for edge, pt in to_split:
        # Проверяем, не деградировало ли ребро (длина > 0)
        v1, v2 = edge.verts[0].co, edge.verts[1].co
        total_dist = (v1 - v2).length
        if total_dist > precision:
            # Вычисляем фактор смещения точки на ребре
            fac = (pt - v1).length / total_dist
            # Разрезаем: создается новая вершина, но bmesh.ops.remove_doubles НЕ вызывается
            try:
                bmesh.utils.edge_split(edge, edge.verts[0], fac)
            except: pass

    bmesh.update_edit_mesh(me)
    context.area.tag_redraw()
