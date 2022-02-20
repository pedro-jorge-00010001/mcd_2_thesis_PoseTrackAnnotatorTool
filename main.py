#Important link to understand Posetrack dataset https://medium.com/@anuj_shah/posetrack-data-set-summary-9cf61fc6f44e
import json
from multiprocessing.connection import wait
import cv2
import time

color_palette = [(154,205,50),(138,43,226),(233,150,122),(0,255,255),(100,149,237)]

# with json load  (file)
with open(r'annotations\000001_bonn_train.json') as json_file:
    data = json.load(json_file)
    anotations = data["annotations"]
    images = data["images"]
    show_annotations = True
    #current_image =  images[23]
    for image in images:
        #get anotations of the current image
        anotations_of_current_image = list(filter(lambda f: (f["image_id"] == image["id"]), anotations))

        img = cv2.imread(image["file_name"])
        if show_annotations:
            color_index = 0
            for current_annotation in anotations_of_current_image:
                current_color = color_palette[color_index]
                color_index += 1
                
                #skeleton points
                for i in range(1,len(current_annotation["keypoints"])//3):
                    end_pos = 3*i
                    start_pos = end_pos - 3
                    xy_pos = current_annotation["keypoints"][start_pos:end_pos]
                    print(xy_pos)
                    if int(xy_pos[0]): 
                        img = cv2.circle(img, (int(xy_pos[0]), int(xy_pos[1])), radius=3, color=current_color, thickness=-1)
                
                #head box
                box_points = current_annotation["bbox_head"]
                x_head = box_points[0]
                y_head = box_points[1]
                end_x_head = x_head + box_points[2]
                end_y_head = y_head + box_points[3]
                img = cv2.rectangle(img, (x_head, y_head), (end_x_head, end_y_head), current_color, 2)
                
                #body box
                box_points = current_annotation["bbox"]
                x = int(box_points[0])
                y = int(box_points[1])
                end_x = x + int(box_points[2])
                end_y = y + int(box_points[3])
                img = cv2.rectangle(img, (x,y), (end_x,end_y), current_color, 2)

                #write skeleton id
                font                   = cv2.FONT_HERSHEY_SIMPLEX
                bottomLeftCornerOfText = (x_head,y_head)
                fontScale              = 0.8
                fontColor              = current_color
                thickness              = 2
                lineType               = 2
                track_id = current_annotation["track_id"]
                cv2.putText(img,str(track_id), 
                    bottomLeftCornerOfText, 
                    font, 
                    fontScale,
                    fontColor,
                    thickness,
                    lineType)

        cv2.imshow('image',img)
        key = cv2.waitKey(200)
        if key == ord('q'):
            break
        
        if key == ord('o'):
            #Disable or able anotations
            show_annotations = not show_annotations
        
        if key == ord('p'):
            key = cv2.waitKey(-1)
            while key != ord('p'): #wait until any key is pressed
                key = cv2.waitKey(-1)

        #img = cv2.rectangle(img, firts_anotation['bbox_head'][2:4], firts_anotation['bbox_head'][0:2] , color=(0, 255, 0), thickness=3)
        


    #cv2.imshow('image',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()