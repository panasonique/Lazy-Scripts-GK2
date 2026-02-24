import bpy
import os
import ast
import re
import textwrap

bl_info = {
    "name": "Lazy Scripts",
    "author": "treety & Gemini (Google AI)",
    "version": (3, 4, 1),
    "blender": (4, 0, 0),
    "category": "Interface",
}

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
addon_keymaps = []
dynamic_classes = []

# --- ЛОГИКА ПЕРЕМЕННЫХ ---

def update_step_logic(self, context):
    target_info = None
    # Ищем info скрипта, которому принадлежит это свойство
    for root, dirs, files in os.walk(BASE_DIR):
        for f in files:
            if f.endswith('.py') and not f.startswith('__'):
                data = get_script_data(os.path.join(root, f))
                if data.get('prop_id') == self.name:
                    target_info = data
                    break
        if target_info: break

    if target_info:
        stype = target_info.get('type', 'input_float')
        p_min = target_info.get('min', -10000.0)
        p_max = target_info.get('max', 10000.0)
        
        # 1. Сначала Clamp (ограничение диапазона)
        new_val = max(p_min, min(p_max, self.value))
        
        # 2. Логика округления в зависимости от типа
        if stype in {'input_int', 'int'}:
            new_val = float(round(new_val))
        elif stype == 'input_custom':
            if new_val > 1.0 or new_val < -1.0:
                new_val = float(round(new_val))
        # Для input_float оставляем как есть (дроби)

        # 3. Записываем только если значение изменилось
        if self.value != new_val:
            self.value = new_val




class MyAddonVariable(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(
        default=-999.0, 
        precision=3, # Увеличим точность для float
        min=-10000.0, # Расширим границы хранилища
        max=10000.0,
        update=update_step_logic # Старая логика останется для совместимости
    )


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def get_sort_key(name):
    match = re.match(r'^(\d+(\.\d+)?)', name)
    return float(match.group(1)) if match else 999.0

def clean_display_name(name):
    name = re.sub(r'^\d+(\.\d+)?[_-]', '', name)
    return name.replace('.py', '').replace('_', ' ')

def get_script_data(filepath):
    data = {"name": clean_display_name(os.path.basename(filepath)), 
            "icon": "NONE", "type": "button", "prop_id": "", "default": 0.0, "description": "", "shortcut": ""}
    try:
        if not os.path.exists(filepath): return data
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(10000))
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == 'info':
                            data.update(ast.literal_eval(node.value))
                            return data
    except: pass
    return data

# --- ОПЕРАТОРЫ ---

class MY_OT_RunExternalScript(bpy.types.Operator):
    bl_idname = "lazy_scripts.run_script"
    bl_label = "Run Script"
    bl_options = {'REGISTER', 'UNDO'} 
    path: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, properties):
        data = get_script_data(properties.path)
        sc = data.get('shortcut', "")
        desc = data.get('description', "Запустить скрипт")
        return f"{desc} [{sc}]" if sc else desc

    def execute(self, context):
        if os.path.exists(self.path):
            info = get_script_data(self.path)
            # Запрещаем запуск для типов int и text
            if info.get('type') in {'int', 'text'}: return {'FINISHED'}
            
        if os.path.exists(self.path):
            info = get_script_data(self.path)
            if info.get('type') == 'int': return {'FINISHED'}
            
            vars_dict = {item.name: item.value for item in context.scene.my_addon_vars}
            class PropsProxy:
                def __init__(self, d): self.__dict__ = d
            global_dict = {
                'bpy': bpy, 
                'context': context, 
                'props': PropsProxy(vars_dict), 
                '__file__': self.path,
                'report': self.report # <-- Добавьте эту строку
            }
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    exec(f.read(), global_dict)
                bpy.ops.ed.undo_push(message=f"Run: {os.path.basename(self.path)}")
            except Exception as e:
                self.report({'ERROR'}, f"Script Error: {e}")
                return {'CANCELLED'}
        return {'FINISHED'}

class MY_OT_RefreshAddon(bpy.types.Operator):
    bl_idname = "lazy_scripts.refresh_addon"
    bl_label = "Refresh"
    def execute(self, context):
        bpy.app.timers.register(self.safe_reload, first_interval=0.1)
        return {'FINISHED'}
    def safe_reload(self):
        try: unregister(); register()
        except: pass
        return None

# --- ГОРЯЧИЕ КЛАВИШИ ---

def register_shortcuts():
    unregister_shortcuts()
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if not kc: return
    km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    for root, dirs, files in os.walk(BASE_DIR):
        for f in files:
            if f.endswith('.py') and not f.startswith('__'):
                path = os.path.join(root, f)
                data = get_script_data(path)
                if data.get('shortcut'):
                    p = data['shortcut'].split()
                    kmi = km.keymap_items.new("lazy_scripts.run_script", type=p[-1].upper(), value='PRESS', 
                                              ctrl='Ctrl' in p, alt='Alt' in p, shift='Shift' in p)
                    kmi.properties.path = path
                    addon_keymaps.append((km, kmi))

def unregister_shortcuts():
    for km, kmi in addon_keymaps:
        if kmi:
            try: km.keymap_items.remove(kmi)
            except: pass
    addon_keymaps.clear()

# --- ИНТЕРФЕЙС ---

def draw_dynamic_section(self, context):
    layout = self.layout
    files = getattr(self, "file_paths", [])
    i = 0
    while i < len(files):
        f_path = files[i]
        sort_val = get_sort_key(os.path.basename(f_path))
        row_paths = [f_path]
        current_base = int(sort_val)
        
        for j in range(i + 1, min(i + 3, len(files))):
            if int(get_sort_key(os.path.basename(files[j]))) == current_base:
                row_paths.append(files[j])
            else: break
        
        row = layout.row(align=True)
        for p in row_paths:
            info = get_script_data(p)
            stype = info.get('type')
            p_id = info.get('prop_id')
            
            # --- ТЕКСТОВЫЕ МЕТКИ ---
            if stype == 'text':
                txt = info.get('name', "")
                align_type = info.get('align', 'LEFT').upper()
                wrap_width = info.get('wrap', 0)
                if p_id:
                    var_item = context.scene.my_addon_vars.get(p_id)
                    txt = f"{txt}: {var_item.value:.2f}" if var_item else txt
                main_row = row.row()
                if align_type == 'CENTER': main_row.column()
                content_col = main_row.column(align=True)
                content_col.alignment = align_type
                if wrap_width > 0:
                    for line in textwrap.wrap(txt, width=wrap_width):
                        l_row = content_col.row(); l_row.alignment = align_type; l_row.label(text=line)
                else: content_col.label(text=txt)
                if align_type in {'CENTER', 'LEFT'}: main_row.column()

            # --- ПОЛЯ ВВОДА ---
            elif stype in {'input_custom', 'input_int', 'input_float', 'int'} and p_id:
                var_item = context.scene.my_addon_vars.get(p_id)
                if var_item:
                    sub = row.row(align=True)
                    # Просто отображаем, update_step_logic сама всё поправит при изменении
                    sub.prop(var_item, "value", text=info.get('name', ""), slider=False)
                    
                    if info.get('description'):
                        help_ico = sub.operator("lazy_scripts.run_script", text="", icon='HELP', emboss=False)
                        help_ico.path = p


                else: row.label(text=f"Init: {info['name']}")
            
            # --- КНОПКИ ---
            else:
                op = row.operator("lazy_scripts.run_script", text=info['name'], icon=info.get('icon', 'NONE'))
                op.path = p
                
        i += len(row_paths)




class MY_PT_Settings(bpy.types.Panel):
    bl_label = "Lazy Settings & Debug"
    bl_idname = "MY_PT_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Lazy Scripts"
    bl_options = {'DEFAULT_CLOSED'}
    def draw(self, context):
        self.layout.operator("lazy_scripts.refresh_addon", text="Reload Structure", icon='FILE_REFRESH')

# --- СЛУЖЕБНЫЕ ФУНКЦИИ ---

def sync_addon_properties():
    if not hasattr(bpy.context, "scene") or bpy.context.scene is None: return 0.5
    scene = bpy.context.scene
    # Добавляем новые типы в список для регистрации
    input_types = {'int', 'input_custom', 'input_int', 'input_float'}
    
    for root, dirs, files in os.walk(BASE_DIR):
        for f in files:
            if f.endswith('.py'):
                data = get_script_data(os.path.join(root, f))
                p_id = data.get('prop_id')
                # Теперь проверяем вхождение в расширенный список типов
                if data.get('type') in input_types and p_id:
                    if p_id not in scene.my_addon_vars:
                        item = scene.my_addon_vars.add()
                        item.name = p_id
                        item.value = data.get('default', 0.0)
                    elif scene.my_addon_vars[p_id].value == -999:
                        scene.my_addon_vars[p_id].value = data.get('default', 0.0)
    return None


@bpy.app.handlers.persistent
def on_load_post_handler(dummy1, dummy2=None):
    bpy.app.timers.register(sync_addon_properties, first_interval=0.1)

# --- РЕГИСТРАЦИЯ ---

def register():
    bpy.utils.register_class(MyAddonVariable)
    bpy.utils.register_class(MY_OT_RunExternalScript)
    bpy.utils.register_class(MY_OT_RefreshAddon)
    bpy.types.Scene.my_addon_vars = bpy.props.CollectionProperty(type=MyAddonVariable)
    
    if on_load_post_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(on_load_post_handler)
    
    if not os.path.exists(BASE_DIR): return
    main_folders = sorted([d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d)) and not d.startswith(('.', '__'))], key=get_sort_key)
    for folder in main_folders:
        folder_path = os.path.join(BASE_DIR, folder)
        safe_folder = re.sub(r'\W+', '_', folder)
        main_id = f"MY_PT_{safe_folder}"
        main_cls = type(main_id, (bpy.types.Panel,), {
            "bl_label": clean_display_name(folder), "bl_idname": main_id,
            "bl_space_type": 'VIEW_3D', "bl_region_type": 'UI', "bl_category": "Lazy Scripts", "draw": lambda s, c: None
        })
        bpy.utils.register_class(main_cls); dynamic_classes.append(main_cls)
        
        content = []
        for item in os.listdir(folder_path):
            path = os.path.join(folder_path, item)
            content.append({'name': item, 'path': path, 'is_dir': os.path.isdir(path), 'key': get_sort_key(item)})
        content.sort(key=lambda x: x['key'])
        
        i = 0
        group_idx = 0
        while i < len(content):
            item = content[i]
            if not item['is_dir']:
                file_group = []
                while i < len(content) and not content[i]['is_dir']:
                    file_group.append(content[i]['path']); i += 1
                g_id = f"MY_PT_G_{safe_folder}_{group_idx}"
                g_cls = type(g_id, (bpy.types.Panel,), {
                    "bl_label": "", "bl_idname": g_id, "bl_parent_id": main_id,
                    "bl_space_type": 'VIEW_3D', "bl_region_type": 'UI',
                    "bl_options": {'HIDE_HEADER'}, "file_paths": file_group, "draw": draw_dynamic_section
                })
                bpy.utils.register_class(g_cls); dynamic_classes.append(g_cls); group_idx += 1
            else:
                # 1. Извлекаем prop_id из имени папки {prop_id}
                found_prop = re.search(r'\{(.+?)\}', item['name'])
                target_prop = found_prop.group(1) if found_prop else None
                
                # 2. Очищаем имя для заголовка (убираем {id} и префиксы)
                clean_label = clean_display_name(re.sub(r'\{.+?\}', '', item['name'])).strip()

                # 3. ФОРМИРУЕМ БЕЗОПАСНЫЙ ID КЛАССА (исправление ошибки)
                # Убираем всё лишнее, заменяем на _, и удаляем подчеркивания в конце
                safe_name = re.sub(r'\W+', '_', item['name']).strip('_')
                sub_id = f"MY_PT_{safe_name}"

                def draw_sub_header(self, context):
                    layout = self.layout
                    # Используем getattr для безопасного получения атрибутов
                    label = getattr(self, "base_label", "Panel")
                    prop_id = getattr(self, "linked_prop", None)
                    
                    if prop_id:
                        var_item = context.scene.my_addon_vars.get(prop_id)
                        if var_item:
                            # Формируем строку с числом
                            label = f"{label} ({var_item.value:.2f})"
                            
                    layout.label(text=label)


                sub_cls = type(sub_id, (bpy.types.Panel,), {
                    "bl_label": "", 
                    "base_label": clean_label,
                    "linked_prop": target_prop,
                    "bl_idname": sub_id,
                    "bl_parent_id": main_id,
                    "bl_space_type": 'VIEW_3D',
                    "bl_region_type": 'UI',
                    "bl_options": {'DEFAULT_CLOSED'},
                    "file_paths": [os.path.join(item['path'], f) for f in os.listdir(item['path']) if f.endswith('.py')],
                    "draw_header": draw_sub_header,
                    "draw": draw_dynamic_section
                })
                bpy.utils.register_class(sub_cls)
                dynamic_classes.append(sub_cls)
                i += 1



    
    bpy.utils.register_class(MY_PT_Settings)
    bpy.app.timers.register(sync_addon_properties, first_interval=0.1)
    register_shortcuts()

def unregister():
    unregister_shortcuts()
    if on_load_post_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(on_load_post_handler)
    
    try: bpy.utils.unregister_class(MY_PT_Settings)
    except: pass
    
    for cls in reversed(dynamic_classes):
        try: bpy.utils.unregister_class(cls)
        except: pass
    dynamic_classes.clear()
    
    for cls in [MY_OT_RefreshAddon, MY_OT_RunExternalScript, MyAddonVariable]:
        try: bpy.utils.unregister_class(cls)
        except: pass
        
    if hasattr(bpy.types.Scene, "my_addon_vars"):
        try: del bpy.types.Scene.my_addon_vars
        except: pass

if __name__ == "__main__":
    register()



