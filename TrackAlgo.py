def track_person(box, frame_center):
    
    x, y, w, h = box
    box_center_x = x + w // 2
    box_center_y = y + h // 2
    
    offset_x = box_center_x - frame_center[0]
    offset_y = box_center_y - frame_center[1]
    
    return movement_commands