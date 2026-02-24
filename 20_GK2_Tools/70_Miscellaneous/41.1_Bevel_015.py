info = {
    "name": "Bevel 0.015",
    "description": "Фаска 0.015м с 2 сегментами",
    "icon": "MOD_BEVEL",
    "type": "button",
    "shortcut": ""
}

# Скрипт выполняется в контексте оператора, bpy и context уже доступны
if context.active_object and context.active_object.mode == 'EDIT':
    bpy.ops.mesh.bevel(
        offset_type='OFFSET', 
        offset=0.015, 
        profile_type='SUPERELLIPSE', 
        offset_pct=0, 
        segments=2, 
        profile=1, 
        affect='EDGES', 
        clamp_overlap=False, 
        loop_slide=True, 
        mark_seam=False, 
        mark_sharp=False, 
        harden_normals=False, 
        face_strength_mode='NONE', 
        miter_outer='SHARP', 
        miter_inner='SHARP', 
        vmesh_method='ADJ'
    )
    # Перерисовка вьюпорта для моментального отображения
    context.area.tag_redraw()
