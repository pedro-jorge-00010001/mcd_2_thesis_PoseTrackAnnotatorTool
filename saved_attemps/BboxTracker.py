import json
from tkinter import filedialog

import numpy as np
from libraries.deep_sort.tracker import Tracker
from libraries.deep_sort import nn_matching
from libraries.deep_sort.detection import Detection
from libraries.deep_sort import preprocessing
import cv2
import time
import torch
file_path = filedialog.askopenfilename(filetypes = [("Json files", ".json")])

json_data = []
with open(file_path) as json_file:
    json_data = json.load(json_file)    

first_image = json_data['images'][0]
total_frames = len(json_data['images'])
annotations = json_data['annotations']
first_image_annotations = list(filter(lambda f: (f["image_id"] == first_image['id']), annotations))

# Definition of the parameters
max_cosine_distance = 0.4
nn_budget = None
nms_max_overlap = 2

metric = nn_matching.NearestNeighborDistanceMetric(
        "cosine", max_cosine_distance, nn_budget)
tracker = Tracker(metric)

#Stored results
results = []


def frame_callback(frame_idx):
    for frame_id in range(0, frame_idx):
        image = json_data['images'][frame_id]
        print(image['id'])
        annotations = json_data['annotations']
        image_annotations = list(filter(lambda f: (f["image_id"] == image['id']), annotations))

        detections = []
        for annotation in image_annotations:
            annotation_vector = annotation['bbox']
            x = annotation_vector[0]
            y = annotation_vector[1]
            w = x + annotation_vector[2]
            h = y + annotation_vector[3]
            detection = Detection(tlwh = [x, y, w, h],confidence=0.8, feature=['1'])
            detections.append(detection)
    
        print(detections)
        

        # Run non-maxima suppression.
        boxes = np.array([d.tlwh for d in detections])
        scores = np.array([d.confidence for d in detections])
        indices = preprocessing.non_max_suppression(
            boxes, nms_max_overlap, scores)
        detections = [detections[i] for i in indices]

        # Update tracker.
        tracker.predict()
        tracker.update(detections)
        
        for item in tracker.tracks:
            print(item.track_id)
        """
        # Update visualization.
        if display:
            image = cv2.imread(
                seq_info["image_filenames"][frame_idx], cv2.IMREAD_COLOR)
            vis.set_image(image.copy())
            vis.draw_detections(detections)
            vis.draw_trackers(tracker.tracks)
        """
        # Store results.
        for track in tracker.tracks:
            #if not track.is_confirmed() or track.time_since_update > 1:
            #    continue
            bbox = track.to_tlwh()
            results.append([
                frame_id, track.track_id, bbox[0], bbox[1], bbox[2], bbox[3]])


frame_callback(total_frames)

color_palette = [(154,205,50),(138,43,226),(233,150,122),(0,255,255),(100,149,237),(0,0,128),(139,0,139),(255,250,205),(205,133,63),(240,255,255),(205,133,63),(240,255,255),(205,133,63),(240,255,255),(154,205,50),(138,43,226),(233,150,122),(0,255,255),(100,149,237),(0,0,128),(139,0,139),(255,250,205),(205,133,63),(240,255,255),(205,133,63),(240,255,255),(205,133,63),(240,255,255)]

for frame_id in range(0, total_frames):
    path = "C:\\Users\\Pedro\\Desktop\\Application\\data_no_ids\\images\\" + json_data['images'][frame_id]['file_name']
    img = cv2.imread(path)
    new_annotations = [annotations for annotations in results if annotations[0] == frame_id]
    for a in new_annotations:
        frame_id, person_id, x, y, w, h = a
        current_color = color_palette[int(person_id)]
        img = cv2.rectangle(img, (int(x),int(y)), (int(w),int(h)), current_color, 2)
    cv2.imshow('image',img)
    cv2.waitKey(300)

"""    
for a in results:         
    frame_id, person_id, x, y, w, h = a
    current_color = color_palette[int(person_id)]
    path = "C:\\Users\\Pedro\\Desktop\\Application\\data_no_ids\\images\\" + json_data['images'][frame_id]['file_name']
    img = cv2.imread(path)
    img = cv2.rectangle(img, (int(x),int(y)), (int(w),int(h)), current_color, 2)
    #img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    cv2.imshow('image',img)
    cv2.waitKey(3000)
"""