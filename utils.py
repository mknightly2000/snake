def center(obj, parent_obj):
    parent_obj_center_x = parent_obj.width / 2
    parent_obj_center_y = parent_obj.height / 2

    x = parent_obj.x + (parent_obj_center_x - obj.width / 2)
    y = parent_obj.y + (parent_obj_center_y - obj.height / 2)

    return x, y


def center_x(obj, x):
    obj = obj.get_rect()
    return x - obj.width / 2


def center_y(obj, y):
    obj = obj.get_rect()
    return y - obj.height / 2
