import json
from operator import index
from tkinter import filedialog
from scipy.spatial import distance
import numpy as np

def json_formating_fixer():
    file_path = filedialog.askopenfilename(filetypes = [("Json files", ".json")])

    data = []
    with open(file_path) as json_file:
        data = json.load(json_file)    

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

#Define center function
def get_rectangle_center(rectangle):
    (x, y, w, h) =  [int(point) for point in rectangle]
    assert w >= x
    assert h >= y
    px = (w-x)/2 + x
    py = (h-y)/2 + y
    return (px, py)

def get_boxes_diferents_between(boxes_a, boxes_b, maximum_dst = 100):
    for box_a in boxes_a:
        a_center = get_rectangle_center(box_a)
        boxes_b_distance = [distance.euclidean(a_center, get_rectangle_center(box)) for box in boxes_b]
        if len(boxes_b_distance):
            min_distance = min(boxes_b_distance)
            if min_distance < maximum_dst:
                boxes_b = [box for box in boxes_b if distance.euclidean(a_center, get_rectangle_center(box)) != min_distance]
    return boxes_a + boxes_b

assert get_boxes_diferents_between([[0,0,20,20]], [[0,0,10,20], [0,0,30,40]]) == [[0,0,20,20], [0,0,30,40]]



def get_closest_rectangle_to(rectangle, vector_of_rectangles_to_compare, maximum_dst = 30):
    
    
    main_rectangle_center = get_rectangle_center(rectangle)

    current_min_dst = 9999999
    current_min_dst_rect = None
    counter = 0
    index = None
    for rectangle_to_compare in vector_of_rectangles_to_compare:
        dst = distance.euclidean(main_rectangle_center, get_rectangle_center(rectangle_to_compare))
        if dst < current_min_dst:
            current_min_dst = dst
            current_min_dst_rect = rectangle_to_compare
            index = counter 
        counter += 1
    if current_min_dst > maximum_dst:
        #current_min_dst_rect = rectangle
        current_min_dst_rect = None
    return current_min_dst_rect, index

def get_number_to_string(number):
    if int(number) < 10:
        return '0' + str(number)
    return str(number)

assert get_number_to_string(1) == '01'
assert get_number_to_string(21) == '21'
 
x = [[120, 120,0],
[30,130, 0]]

def get_rectangle_from_keypoints(keypoints):
    x_min = 99999
    y_min = 99999
    x_max = 0
    y_max = 0
    for keypoint in keypoints:
        x = keypoint[0]
        y = keypoint[1]
        if x < x_min and x != 0:
            x_min = x
        if x > x_max:
            x_max = x
        
        if y < y_min and y != 0:
            y_min = y
        if y > y_max:
            y_max = y
    
    return (x_min, y_min, x_max, y_max)

assert get_rectangle_from_keypoints(x) == (30,120,120,130)


def trasnform_wh_to_x2y2(bbox):
    return (bbox[0], bbox[1], bbox[2]-bbox[0],bbox[3] - bbox[1])


def get_skeletons_and_ids_from_bbox(bboxs_with_ids, vector_of_keypoints):
    if bboxs_with_ids is not None and vector_of_keypoints is not None:
        bbox_skeletons = [get_rectangle_from_keypoints(keypoints) for keypoints in vector_of_keypoints]
        #print(bbox_skeletons)
        keypoints_with_ids = []
        for element in bboxs_with_ids:
            id_num= element[0]
            bbox = element[1]
            bbox = bbox[0]
            print(bbox)
            closest_rectangle, index = get_closest_rectangle_to(bbox, bbox_skeletons)
            keypoints_with_ids.append((id_num,vector_of_keypoints[index]))
        return keypoints_with_ids
    else:
        return []


            

        
