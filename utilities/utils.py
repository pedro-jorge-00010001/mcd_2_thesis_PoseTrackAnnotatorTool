import json
from operator import index
from tkinter import filedialog
from scipy.spatial import distance
import numpy as np
from soupsieve import closest

def get_rectangle_area(rectangle):
    if rectangle is None: return 0
    x, y, w, h =  rectangle
    assert w >= x
    assert h >= y
    length = w - x
    witdh = h - y
    return length * witdh

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


def trasnform_to_wh(bbox):
    if bbox is None: return None
    return (bbox[0], bbox[1], bbox[2]-bbox[0],bbox[3] - bbox[1])

def trasnform_to_xy(bbox):
    if bbox is None: return None
    return (bbox[0], bbox[1], bbox[2]+bbox[0],bbox[3] + bbox[1])

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

map_openpose_posetrack = {
    "nose" : [1, 0],
    "head_bottom" : [2, None],
    "head_top" : [3, None],
    "left_ear" : [4, 18],
    "right_ear" : [5, 17],
    "left_shoulder" : [6, 5],
    "right_shoulder" : [7, 2],
    "left_elbow" : [8, 6],
    "right_elbow" : [9, 3],
    "left_wrist" : [10, 7],
    "right_wrist" : [11, 4],
    "left_hip" : [12, 12],
    "right_hip" : [13, 9],
    "left_knee" : [14, 13],
    "right_knee" : [15, 10],
    "left_ankle" : [16, 14],
    "right_ankle" : [17, 11],
}

def transform_openpose_skl_to_posetrack_skl(keypoints_openpose, skeleton_point_confidence_threshold = 0.15):
    keys = map_openpose_posetrack.keys()
    keypoints = []
    for key in keys:
        openpose_identificator = map_openpose_posetrack[key][1]
        if openpose_identificator is None:
            keypoints.append([0,0,0])
        else:
            openpose_keypoint = keypoints_openpose[openpose_identificator]
            #Verify that the confidence is greather than the threshold
            if openpose_keypoint[2] < skeleton_point_confidence_threshold:
                openpose_keypoint = np.array([0.0, 0.0, 0.0])
            keypoints.append(openpose_keypoint)
    return keypoints

def build_path(images_directory_path, image_path):
    images_directory_path_as_array = images_directory_path.split('\\')
    image_path_as_array = image_path.split('\\')
    for part_of_path in image_path_as_array:
        if part_of_path not in images_directory_path_as_array:
            images_directory_path_as_array.append(part_of_path)
    images_directory_path_as_array = [part_of_path for part_of_path in images_directory_path_as_array if part_of_path.strip() != '']
    return "/".join(images_directory_path_as_array)
