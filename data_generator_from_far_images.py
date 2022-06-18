import tracker_deepsort
import cv2
from utilities import utils
import imutils
import numpy as np
import skeleton_openpose
from tkinter import filedialog
import glob
from utilities import image_annotator
import person_detector_yolov5
import json

def get_detections(img):
    # detect persons
    detections_boxes = person_detector_yolov5.detect_persons(img)
    detections_boxes = [utils.trasnform_to_xy(detection) for detection in detections_boxes]

    keypoints, output_image = skeleton_openpose.get_keypoints(img)
    detections_from_skeletons = []
    if keypoints is not None:
        for keypoint in keypoints:
            bbox =  utils.get_rectangle_from_keypoints(keypoint)
            detections_from_skeletons.append(bbox)

    detections = utils.get_boxes_diferents_between(detections_boxes, detections_from_skeletons)
    detections_boxes = [utils.trasnform_to_wh(detection) for detection in detections]
    return detections_boxes

def track_and_get_skeletons(img, detections, pixes_around_detection=0, resize_multiplier = 2):
    def clamp(n, minn, maxn):
        return max(min(maxn, n), minn)
    tracked_data = tracker_deepsort.get_ids_from_image(img, detections)
    data = []
    for track in tracked_data:
        id_num = track[0]
        bbox_detection = track[1]
        bbox_tracker = track[2]

        box_skeleton = bbox_detection
        if utils.get_rectangle_area(utils.trasnform_to_xy(box_skeleton)) < utils.get_rectangle_area(utils.trasnform_to_xy(bbox_tracker)):
            box_skeleton = bbox_tracker
        
        box_skeleton = [int(point) for point in box_skeleton]
        x,y,w,h = box_skeleton
        xmax = x + w
        ymax = y + h

        x_crop_reverse = abs(x-pixes_around_detection)
        y_crop_reverse = abs(y-pixes_around_detection)
        xmax_crop_reverse =  clamp(xmax + pixes_around_detection,0, img.shape[1])
        ymax_crop_reverse = clamp(ymax + pixes_around_detection, 0, img.shape[0])
        croped_img = img[y_crop_reverse:ymax_crop_reverse, x_crop_reverse:xmax_crop_reverse]
        #croped_img = img[y:ymax, x:xmax]
        # resize
        croped_img = imutils.resize(croped_img, width=(xmax_crop_reverse-x_crop_reverse)*resize_multiplier, height=(ymax_crop_reverse-y_crop_reverse)*resize_multiplier)
        keypoints, output_image = skeleton_openpose.get_keypoints(croped_img)
        # cv2.imshow("Data generator", output_image)
        # if cv2.waitKey(10) & 0xFF==ord('q'):
        #     break
        if keypoints is not None:
            #get back points
            keypoints_updated = []
            for points in keypoints[0]:
                xp, yp, cf = points
                xp = xp/resize_multiplier + x_crop_reverse
                yp = yp/resize_multiplier + y_crop_reverse
                keypoints_updated.append([xp, yp, cf])

            keypoints = utils.transform_openpose_skl_to_posetrack_skl(keypoints_updated)
        data.append([id_num, bbox_detection, bbox_tracker, keypoints])

    
    return data

image_id = 0
annotation_id = 0
json_object = {}

#Store categories like PoseTrack
with open(r"resources\json\skeleton_map.json") as json_file:
    data = json.load(json_file)  
    json_object["categories"] = data

def load_into_json(filename, data):
    global image_id
    global json_object
    global annotation_id

    image_id += 1
    def keypoints_to_vect (keypoints):
        vector = []
        if keypoints is not None:
            for points in keypoints:
                for p in points:
                    vector.append(float(p))
        return vector

    #write image in json
    image = {
            "frame_id" : image_id,
            "id" : image_id,
            "file_name" : filename
        }
    if 'images' not in json_object:
        json_object["images"] = []
    json_object["images"].append(image)

    if 'annotations' not in json_object:
        json_object["annotations"] = []
    
    #write annotations
    for elem in data:
        person_id, bbox_detection, bbox_tracker, keypoints = elem
        bbox = bbox_detection
        if bbox is None:
            bbox = bbox_tracker

        if bbox is not None:
            keypoints = keypoints_to_vect(keypoints)
            annotation_id += 1
            annotation = {
                "keypoints": keypoints,
                "track_id": int(person_id),
                "image_id": image_id,
                "bbox": bbox,
                "category_id": 1,
                "id": annotation_id
            }
            json_object["annotations"].append(annotation)

def run(img, path):
    detections_boxes = get_detections(img)
    if len(detections_boxes):
        data = track_and_get_skeletons(img, detections_boxes, pixes_around_detection=100, resize_multiplier=1)
        #black background
        #img =  np.zeros(img.shape, np.uint8)
        for elem in data:
            person_id, bbox_detection, bbox_tracker, keypoints = elem
            
            img = image_annotator.draw_box(img, bbox_detection, color=(255,255,255))
            img = image_annotator.draw_box(img, bbox_tracker, color=(255,255,255))
            img = image_annotator.draw_annotation(img, (bbox_tracker[0], bbox_tracker[1]),"Id:" + str(person_id), color=(255,255,255))
            img = image_annotator.draw_skeleton(img, keypoints, color=(255,255,255))
        load_into_json(path ,data)
    cv2.imshow("Data generator", img)
    #cv2.waitKey(0)
    cv2.waitKey(1)

if __name__=="__main__":
    file_type = "mp4"
    if file_type == "img":
        #ask to open a directory
        directory_path = filedialog.askdirectory(title="Select directory")

        #iterate thorugh all the images in the directory
        for path in glob.glob(directory_path + '/*'):
            # read image
            img = cv2.imread(path)
            run(img, path)
        with open(directory_path + "/data.json", 'w', encoding='utf-8') as f:
            json.dump(json_object, f, ensure_ascii=False, indent=4)

    elif file_type == "wbc":
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            run(frame)
    elif file_type == "mp4":
        #ask to open a directory
        file_path = filedialog.askopenfile(title="Select file")
        cap = cv2.VideoCapture(file_path.name)
        while(cap.isOpened()):
            path = ""
            ret, frame = cap.read()
            # read image
            run(frame, path)
        

    