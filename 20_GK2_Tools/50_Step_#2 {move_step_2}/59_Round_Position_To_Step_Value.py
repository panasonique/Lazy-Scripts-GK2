info = {
    "name": "Round Position To Step Value",
    "description": "Округлить положение объекта до значения заданного в поле Step Value 2",
    "icon": "NONE",
    "prop_id": "move_step_2"
}


import bpy

def main():
    # 1. Получаем шаг из прокси-объекта props (твой аддон его уже подготовил)
    step = getattr(props, info["prop_id"], 1.0)
    if step <= 0: return

    # 2. Коэффициенты осей (твои магические числа)
    # Вычисляем один раз перед циклом для производительности
    factors = (
        step * 0.01,         # X
        step * 0.0125,       # Y
        step * 0.0166666     # Z
    )

    # 3. Проверка режима (context уже прокинут аддоном)
    if context.mode != 'OBJECT' or not context.selected_objects:
        return

    # 4. Применяем ко всем выделенным
    for obj in context.selected_objects:
        # Используем списковое включение для быстрой перезаписи координат
        obj.location = [
            round(coord / f) * f 
            for coord, f in zip(obj.location, factors)
        ]

# Запуск внутри окружения exec()
main()







# import bpy

# # Получаем значение из прокси-объекта 'props', который передает твой аддон
# step = props.move_step


# if bpy.context.object.mode == 'OBJECT':
    # if bpy.context.selected_objects:
        # ob = bpy.context.active_object.location
        # ob.x = ((round((ob.x/0.01)/step))*step)*0.01
        # ob.y = ((round((ob.y/0.0125)/step))*step)*0.0125
        # ob.z = ((round((ob.z/0.0166666)/step))*step)*0.0166666



