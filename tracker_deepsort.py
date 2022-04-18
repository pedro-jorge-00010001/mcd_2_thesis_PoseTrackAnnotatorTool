#https://github.com/abhyantrika/nanonets_object_tracking/
from operator import index
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import cv2

from utilities.deepsort import *
from tkinter import filedialog
import json
import utilities.utils as utils
import  utilities.image_annotator as image_annotator

import re


#Initialize deep sort.
deepsort = deepsort_rbc()


def get_gt(images, annotations, frame_id):
    image = images[frame_id]
    annotations = json_data['annotations']
    image_annotations = list(filter(lambda f: (f["image_id"] == image['id']), annotations))  

    detections = []
    out_scores = []
    for annotation in image_annotations:
        try:
            annotation_vector = annotation['bbox']
            x = annotation_vector[0]
            y = annotation_vector[1]       
            w = annotation_vector[2]
            h = annotation_vector[3]

            detections.append([x,y,w,h])      
            out_scores.append(1)
        except:
            print("Doesn't have bbox")

    return detections,out_scores

def get_json(filename):
    json_data = []
    with open(filename) as json_file:
        json_data = json.load(json_file)    
    return json_data

def get_ids_from_image(img, detections):
    frame = img.astype(np.uint8)
    out_scores = np.ones(len(detections))
    detections = np.array(detections)
    tracker,detections_class = deepsort.run_deep_sort(frame,out_scores,detections)
    
    bbox_and_ids = []
    for track in tracker.tracks:
        if not track.is_confirmed() or track.time_since_update > 1:
            continue
        bbox = track.to_tlbr() #Get the corrected/predicted bounding box
        id_num = str(track.track_id) #Get the ID for the particular track.

        bbox_from_tracking = bbox
        detections_rectangle_vector = [det.to_tlbr() for det in detections_class]
        bbox_from_detection, index = utils.get_closest_rectangle_to(bbox_from_tracking,detections_rectangle_vector)
        bbox_and_ids.append((id_num, bbox_from_detection, bbox_from_tracking))
    return bbox_and_ids


if __name__=="__main__": 
    filename = filedialog.askopenfilename(filetypes = [("Json files", ".json")])

    #Load detections for the video
    json_data = get_json(filename)

    #Get just the images that have annotations
    annotations = json_data['annotations']
    annotation_list = [annotation['image_id'] for annotation in annotations]
    annotation_list = list(set(annotation_list))

    images= list(filter(lambda f: (f["id"] in annotation_list), json_data['images']))
    total_frames = len(images)    

    #Initialize json file to save
    json_data_ids = {
        "images" : images
    }

    json_data_ids["annotations"] = []

    for frame_id in range(0, total_frames): 
        path = re.sub('/annotations/.*','/images/', filename)
        path = image_annotator.build_path(path.replace('/', '\\'), images[frame_id]['file_name'].replace('/', '\\'))
        #path = images[frame_id]['file_name']
        print(frame_id)        
        frame = cv2.imread(path)
        

        detections,out_scores = get_gt(images, annotations, frame_id)

        bbox_and_ids = get_ids_from_image(frame, detections)


        for element in bbox_and_ids:
            id_num = element[0]
            bbox = element[1]
            if bbox is not None:
                #Draw bbox from tracker.
                cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])),(255,255,255), 2)
                cv2.putText(frame, str(id_num),(int(bbox[0]), int(bbox[1])),0, 5e-3 * 200, (0,255,0),2)
                if bbox is not None:
                    annotation = {
                        "track_id": int(id_num),
                        "image_id": frame_id + 1,
                        "bbox" : [
                            bbox[0],
                            bbox[1],
                            bbox[2] - bbox[0],
                            bbox[3] - bbox[1]
                        ],
                        "scores" : [],
                        "category_id": 1
                    } 
                    #Store annotation
                    json_data_ids["annotations"].append(annotation)
                
        cv2.imshow('frame',frame)
        #out.write(frame)
        cv2.waitKey(20)
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break

    #Store categories like PoseTrack
    json_data_ids["categories"] = [
            {
                "supercategory": "person",
                "id": 1,
                "name": "person",
                "keypoints": [
                    "nose",
                    "head_bottom",
                    "head_top",
                    "left_ear",
                    "right_ear",
                    "left_shoulder",
                    "right_shoulder",
                    "left_elbow",
                    "right_elbow",
                    "left_wrist",
                    "right_wrist",
                    "left_hip",
                    "right_hip",
                    "left_knee",
                    "right_knee",
                    "left_ankle",
                    "right_ankle"
                ],
                "skeleton": [
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
            }
        ]

    #Build new name
    vector = filename.split('/')
    name = vector[len(vector)-1].replace(".json", "_with_ids.json")
    vector = vector[0:len(vector)-1]
    vector.append(name)

    filename_save = "/".join(vector)  

    with open(filename_save, 'w', encoding='utf-8') as f:
        json.dump(json_data_ids, f, ensure_ascii=False, indent=4)
    print(json_data_ids)