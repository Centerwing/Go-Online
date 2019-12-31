

def build_official_move(move_data):
    # target coordinates
    res_target_coords = '%s_%s' % (move_data['dest_x'], move_data['dest_y'])

    res = '{target_coords}'.format(target_coords=res_target_coords)
    return res
