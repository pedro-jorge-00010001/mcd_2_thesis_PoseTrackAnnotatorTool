#Important link to understand Posetrack dataset https://medium.com/@anuj_shah/posetrack-data-set-summary-9cf61fc6f44e
import cv2
from PIL import ImageColor
from cv2 import exp

import numpy as np
import utilities.utils as utils


#assert build_path("C:\\Users\\Pedro\\Desktop\\Application\\data\\data_no_ids\\images\\", "\\images\\img1.jpg") == "C:\\Users\\Pedro\\Desktop\\Application\\data\\data_no_ids\\images\\img1.jpg"
#assert build_path("C:\\Users\\Pedro\\Desktop\\Application\\data\\data_no_ids\\images\\", "\\img1.jpg") == "C:\\Users\\Pedro\\Desktop\\Application\\data\\data_no_ids\\images\\img1.jpg"

color_palette = [(154,205,50),(138,43,226),(233,150,122),(0,255,255),(100,149,237),(0,0,128),(139,0,139),(255,250,205),(205,133,63),(240,255,255),(205,133,63),(240,255,255),(205,133,63),(240,255,255),(154,205,50),(138,43,226),(233,150,122),(0,255,255),(100,149,237),(0,0,128)]

def draw_box(img, box_points, color = (0,0,0)):
    if box_points is None: return img
    #Convert to intergers
    box_points = [ int(x) for x in box_points ]
    try:
        x, y, w, h = box_points
        img = cv2.rectangle(img, (x, y), ( x + w, y+ h), color, 2)
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


skeleton =  [
                [
                    16,
                    14
                ],
                [
                    14,
                    12
                ],
                [
                    17,
                    15
                ],
                [
                    15,
                    13
                ],
                [
                    12,
                    13
                ],
                [
                    6,
                    12
                ],
                [
                    7,
                    13
                ],
                [
                    6,
                    7
                ],
                [
                    6,
                    8
                ],
                [
                    7,
                    9
                ],
                [
                    8,
                    10
                ],
                [
                    9,
                    11
                ],
                [
                    2,
                    3
                ],
                [
                    1,
                    2
                ],
                [
                    1,
                    3
                ],
                [
                    2,
                    4
                ],
                [
                    3,
                    5
                ],
                [
                    4,
                    6
                ],
                [
                    5,
                    7
                ]
            ]


def draw_skeleton(img, keypoins, color = (255,255,255), draw_circles = False):
    if keypoins is None: return img
    if draw_circles:
        for point in keypoins:
            if point[2]: 
                img = cv2.circle(img, (int(point[0]), int(point[1])), radius=3, color=color, thickness=3)
    #skeleton lines
    index = 0
    for line_betwen_points in skeleton:
        #1-17
        skeleton_point_id_1 = line_betwen_points[0] - 1
        skeleton_point_id_2 = line_betwen_points[1] - 1
        point_1 = keypoins[skeleton_point_id_1]
        point_2 = keypoins[skeleton_point_id_2]
        color = color_palette[index%len(color_palette)]
        if point_1[2] != 0 and point_2[2] != 0:
            cv2.line(img, (int(point_1[0]), int(point_1[1])), (int(point_2[0]), int(point_2[1])), color=color, thickness=2, lineType=8)
        index += 1
    return img


# from kalmanfilter import KalmanFilter
# kf = KalmanFilter()

def annotate_image(image,img, image_number, json_data):    

    anotations = json_data["annotations"]
    anotations_of_current_image = list(filter(lambda f: (f["image_id"] == image["id"]), anotations))
    characteristics = []
    if 'characteristics' in json_data:
        characteristics = json_data['characteristics']
    actions = []
    if 'actions' in json_data:
        actions = json_data['actions']

    for current_annotation in anotations_of_current_image:
        current_color = color_palette[current_annotation["track_id"]%len(color_palette)]

        try:
            skeleton_points_vector = []
            #skeleton points
            for i in range(1,len(current_annotation["keypoints"])//3 + 1):
                end_pos = 3*i
                start_pos = end_pos - 3
                xy_pos = current_annotation["keypoints"][start_pos:end_pos]
                skeleton_points_vector.append(xy_pos)
                #print(xy_pos)
            img = draw_skeleton(img,skeleton_points_vector, color=current_color)
            # # temp
            # left_ear = skeleton_points_vector[0][0:2]
            # predicted = kf.predict(left_ear[0], left_ear[1])
            # print(predicted)
            # img = draw_annotation(img,(predicted[0], predicted[1]), "Pred" , color=(255,255,255))
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

def remove_distortion(img):
    width  = img.shape[1]
    height = img.shape[0]

    distCoeff = np.zeros((4,1),np.float64)

    # TODO: add your coefficients here!
    k1 = -1.0e-5; # negative to remove barrel distortion
    k2 = 0.0;
    p1 = 0.0;
    p2 = 0.0;

    distCoeff[0,0] = k1;
    distCoeff[1,0] = k2;
    distCoeff[2,0] = p1;
    distCoeff[3,0] = p2;

    # assume unit matrix for camera
    cam = np.eye(3,dtype=np.float32)

    cam[0,2] = width/2.0  # define center x
    cam[1,2] = height/2.0 # define center y
    cam[0,0] = 10.        # define focal length x
    cam[1,1] = 10.        # define focal length y

    # here the undistortion will be computed
    dst = cv2.undistort(img,cam,distCoeff)
    return dst