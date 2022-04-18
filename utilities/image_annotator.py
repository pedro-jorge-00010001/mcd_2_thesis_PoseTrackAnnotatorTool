#Important link to understand Posetrack dataset https://medium.com/@anuj_shah/posetrack-data-set-summary-9cf61fc6f44e
import cv2
from PIL import ImageColor
from cv2 import exp

import numpy as np

def build_path(images_directory_path, image_path):
    images_directory_path_as_array = images_directory_path.split('\\')
    image_path_as_array = image_path.split('\\')
    for part_of_path in image_path_as_array:
        if part_of_path not in images_directory_path_as_array:
            images_directory_path_as_array.append(part_of_path)
    images_directory_path_as_array = [part_of_path for part_of_path in images_directory_path_as_array if part_of_path.strip() != '']
    return "\\".join(images_directory_path_as_array)

#assert build_path("C:\\Users\\Pedro\\Desktop\\Application\\data\\data_no_ids\\images\\", "\\images\\img1.jpg") == "C:\\Users\\Pedro\\Desktop\\Application\\data\\data_no_ids\\images\\img1.jpg"
#assert build_path("C:\\Users\\Pedro\\Desktop\\Application\\data\\data_no_ids\\images\\", "\\img1.jpg") == "C:\\Users\\Pedro\\Desktop\\Application\\data\\data_no_ids\\images\\img1.jpg"


def draw_box(img, box_points, color = (0,0,0), wh_format = False):
    #Convert to intergers
    box_points = [ int(x) for x in box_points ]
    try:
        x_head = box_points[0]
        y_head = box_points[1]
        if wh_format:
            end_x_head = box_points[2]
            end_y_head = box_points[3]
        else:
            end_x_head = x_head + box_points[2]
            end_y_head = y_head + box_points[3]
        img = cv2.rectangle(img, (x_head, y_head), (end_x_head, end_y_head), color, 2)
    except:
        print("Can't draw the box")
    return img

def draw_annotation(img, head_point, value, color = (0,0,0)):
    head_point = [ int(x) for x in head_point ]
    try:
        x_head, y_head = head_point
        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (x_head,y_head)
        fontScale              = 0.8
        fontColor              = color
        thickness              = 2
        lineType               = 2
        cv2.putText(img, value, 
            bottomLeftCornerOfText, 
            font, 
            fontScale,
            fontColor,
            thickness,
            lineType)
    except:
        print("Can't write annotation (There is something missing)")
    return img

def annotate_image(image, image_number, json_data, images_directory_path):    
    color_palette = [(154,205,50),(138,43,226),(233,150,122),(0,255,255),(100,149,237),(0,0,128),(139,0,139),(255,250,205),(205,133,63),(240,255,255),(205,133,63),(240,255,255),(205,133,63),(240,255,255),(154,205,50),(138,43,226),(233,150,122),(0,255,255),(100,149,237),(0,0,128),(139,0,139),(255,250,205),(205,133,63),(240,255,255),(205,133,63),(240,255,255),(205,133,63),(240,255,255)]

    anotations = json_data["annotations"]
    categories = json_data["categories"][0]
    skeleton = categories["skeleton"]

    path = build_path(images_directory_path.replace("/", "\\"), image["file_name"].replace("/", "\\"))
    #path = image["file_name"]
    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #img =  np.zeros(img.shape, np.uint8)
    anotations_of_current_image = list(filter(lambda f: (f["image_id"] == image["id"]), anotations))
    characteristics = []
    if 'characteristics' in json_data:
        characteristics = json_data['characteristics']
    actions = []
    if 'actions' in json_data:
        actions = json_data['actions']

    for current_annotation in anotations_of_current_image:
        current_color = color_palette[current_annotation["track_id"]]

        try:
            skeleton_points_vector = []
            #skeleton points
            for i in range(1,len(current_annotation["keypoints"])//3 + 1):
                end_pos = 3*i
                start_pos = end_pos - 3
                xy_pos = current_annotation["keypoints"][start_pos:end_pos]
                skeleton_points_vector.append(xy_pos)
                #print(xy_pos)
                if int(xy_pos[0]): 
                    img = cv2.circle(img, (int(xy_pos[0]), int(xy_pos[1])), radius=3, color=current_color, thickness=3)
            #skeleton lines
            for line_betwen_points in skeleton:
                #1-17
                skeleton_point_id_1 = line_betwen_points[0] - 1
                skeleton_point_id_2 = line_betwen_points[1] - 1
                point_1 = skeleton_points_vector[skeleton_point_id_1]
                point_2 = skeleton_points_vector[skeleton_point_id_2]
                if point_1[2] != 0 and point_2[2] != 0:
                    cv2.line(img, (int(point_1[0]), int(point_1[1])), (int(point_2[0]), int(point_2[1])), color=current_color, thickness=1, lineType=8)
        except:
            print("Doesn't have skeleton")

        #head box
        try:
            hbox_points = current_annotation["bbox_head"]
            img = draw_box(img, hbox_points, current_color)
        except:
            print("Doesn't have bbox_head")

        #body box
        bbox_points = None
        try:  
            bbox_points = current_annotation["bbox"]
            img = draw_box(img, bbox_points, current_color)
        except:
            print("Doesn't have bbox")

        if bbox_points is not None or hbox_points is not None:
            if bbox_points is not None:
                x_head = bbox_points[0]
                y_head = bbox_points[1]
            
            elif hbox_points is not None:
                x_head = hbox_points[0]
                y_head = hbox_points[1]
            
            #write skeleton id
            try:  
                track_id = current_annotation["track_id"]
                img = draw_annotation(img, (x_head, y_head),"Id:" + str(track_id), current_color)
            except:
                print("Doesn't have track_id")
            current_person_other_info = list(filter(lambda f: (f["track_id"] == current_annotation["track_id"]), characteristics))
            if len(current_person_other_info):
                #Write gender
                gender = current_person_other_info[0]['gender']
                img = draw_annotation(img, (x_head + 50, y_head), "Gender:" + gender, current_color)

                #Write age-group
                age_group = current_person_other_info[0]['age_group']
                img = draw_annotation(img, (x_head, y_head - 20), "Age-Group:" + age_group, current_color)

            current_person_actions = list(filter(lambda f: (f["track_id"] == current_annotation["track_id"]), actions))
            if len(current_person_actions):
                #Write action
                current_person_actions = list(filter(lambda f: (image_number >= f["start_frame"]  and image_number <= f["finish_frame"]), current_person_actions))
                if len(current_person_actions):
                    action = current_person_actions[0]['action_name']
                    img = draw_annotation(img, (x_head - 50, y_head-40), "Action:" + action, ImageColor.getcolor(current_person_actions[0]['color'], "RGB"))
            #else:
            #    print("There is no aditional info for person: ", track_id)
        #else:
            #print("Can't find a position to write annotations") 
    return img, anotations_of_current_image