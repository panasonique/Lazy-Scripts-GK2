info = {
    "name": "Line Split",
    "description": "Разрезать ребра ровно в точках их пересечения",
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
    
    # 1. Список выделенных ребер
    edges = [e for e in bm.edges if e.select]
    precision = 0.00001 # Ваша точность проекта (п. 5)

    # Словарь для хранения точек разреза для каждого ребра
    splits = {e: [] for e in edges}

    # 2. Математический поиск пересечений
    for i in range(len(edges)):
        for j in range(i + 1, len(edges)):
            e1, e2 = edges[i], edges[j]
            
            # Координаты вершин
            v1_a, v1_b = e1.verts[0].co, e1.verts[1].co
            v2_a, v2_b = e2.verts[0].co, e2.verts[1].co
            
            res = intersect_line_line(v1_a, v1_b, v2_a, v2_b)
            if res:
                p1, p2 = res
                # Если прямые пересекаются в 3D (дистанция между ними меньше допуска)
                if (p1 - p2).length < precision:
                    intersect_pt = (p1 + p2) / 2
                    
                    # Проверка: лежит ли точка внутри отрезков (а не на продолжении прямых)
                    def is_on_segment(pt, start, end):
                        return (pt - start).length + (pt - end).length < (start - end).length + precision
                    
                    if is_on_segment(intersect_pt, v1_a, v1_b) and is_on_segment(intersect_pt, v2_a, v2_b):
                        # Сохраняем точку пересечения для обоих ребер
                        splits[e1].append(intersect_pt)
                        splits[e2].append(intersect_pt)

    # 3. Физическое разрезание ребер
    new_verts = []
    for edge, points in splits.items():
        for pt in points:
            # edge_split разрезает ребро 'edge', создавая новую вершину в точке 'pt'
            # Вычисляем коэффициент (factor) положения точки на ребре
            v1, v2 = edge.verts[0].co, edge.verts[1].co
            total_len = (v1 - v2).length
            if total_len > precision:
                fac = (pt - v1).length / total_len
                # Выполняем разрез. Возвращает (новое_ребро, новая_вершина)
                new_edge, new_v = bmesh.utils.edge_split(edge, edge.verts[0], fac)
                new_verts.append(new_v)

    # 4. Склеиваем вершины, которые оказались в одной точке пересечения
    if new_verts:
        bmesh.ops.remove_doubles(bm, verts=new_verts, dist=precision)

    bmesh.update_edit_mesh(me)
    context.area.tag_redraw()
