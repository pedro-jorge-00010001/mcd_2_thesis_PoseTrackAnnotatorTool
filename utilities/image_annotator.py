#Important link to understand Posetrack dataset https://medium.com/@anuj_shah/posetrack-data-set-summary-9cf61fc6f44e
from unittest import result
import cv2

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

def annotate_image(image, json_data, images_directory_path):    
    color_palette = [(154,205,50),(138,43,226),(233,150,122),(0,255,255),(100,149,237),(0,0,128),(139,0,139),(255,250,205),(205,133,63),(240,255,255),(205,133,63),(240,255,255),(205,133,63),(240,255,255),(154,205,50),(138,43,226),(233,150,122),(0,255,255),(100,149,237),(0,0,128),(139,0,139),(255,250,205),(205,133,63),(240,255,255),(205,133,63),(240,255,255),(205,133,63),(240,255,255)]

    anotations = json_data["annotations"]
    categories = json_data["categories"][0]
    skeleton = categories["skeleton"]

    path = build_path(images_directory_path.replace("/", "\\"), image["file_name"].replace("/", "\\"))
    #path = image["file_name"]
    img = cv2.imread(path)
    
    #img =  np.zeros(img.shape, np.uint8)
    anotations_of_current_image = list(filter(lambda f: (f["image_id"] == image["id"]), anotations))
    other_info = []
    if 'other' in json_data:
        other_info = json_data['other']

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

        try:
            #head box
            box_points = current_annotation["bbox_head"]
            x_head = box_points[0]
            y_head = box_points[1]
            end_x_head = x_head + box_points[2]
            end_y_head = y_head + box_points[3]
            img = cv2.rectangle(img, (x_head, y_head), (end_x_head, end_y_head), current_color, 2)
        except:
            print("Doesn't have head box")

        #body box
        try:
            box_points = current_annotation["bbox"]
            x = int(box_points[0])
            y = int(box_points[1])
            x_head = x
            y_head = y
            end_x = x + int(box_points[2])
            end_y = y + int(box_points[3])
            img = cv2.rectangle(img, (x,y), (end_x,end_y), current_color, 2)
        except:
            print("Doesn't have bbox")
        
        #write skeleton id
        font                   = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (x_head,y_head)
        fontScale              = 0.8
        fontColor              = current_color
        thickness              = 2
        lineType               = 2
        track_id = current_annotation["track_id"]
        cv2.putText(img,"Id:" + str(track_id), 
            bottomLeftCornerOfText, 
            font, 
            fontScale,
            fontColor,
            thickness,
            lineType)
        
        #Write gender
        try:
            track_id_value = list(filter(lambda f: (f["track_id"] == current_annotation["track_id"]), other_info))
            if track_id_value != []:
                bottomLeftCornerOfText = (x_head + 50,y_head)
                gender = track_id_value[0]['gender']
                cv2.putText(img,"Gender:" + gender, 
                    bottomLeftCornerOfText, 
                    font, 
                    fontScale,
                    fontColor,
                    thickness,
                    lineType)
        except:
            print("Doesn't have gender")
        #Write age-group
        try:
            track_id_value = list(filter(lambda f: (f["track_id"] == current_annotation["track_id"]), other_info))
            if track_id_value != []:
                bottomLeftCornerOfText = (x_head, y_head- 30)
                gender = track_id_value[0]['age_group']
                if gender != None:
                    cv2.putText(img,"Age-Group:" + str(gender), 
                        bottomLeftCornerOfText, 
                        font, 
                        fontScale,
                        fontColor,
                        thickness,
                        lineType)
        except:
            print("Doesn't have gender")

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img, anotations_of_current_image