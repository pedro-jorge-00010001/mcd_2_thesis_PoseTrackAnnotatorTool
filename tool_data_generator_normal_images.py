# Here because at this moment the conda enviroments in my pc are in conflict :( sad face
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'

from utilities import utils
import tool_skeleton_openpose
import cv2
from utilities import image_annotator
from tkinter import filedialog
import glob
import tool_tracker_deepsort
import numpy as np
import imutils
import json
from scipy.spatial import distance
import pathlib
import tool_person_detector_yolov5
from shapely.geometry import Polygon


def get_skeletons_with_box(img):
    # detect persons
    try:
        detections_boxes = tool_person_detector_yolov5.detect_persons(img)
    except:
        detections_boxes = []
    # detections_boxes = [utils.trasnform_to_xy(detection) for detection in detections_boxes]

    keypoints, output_image = tool_skeleton_openpose.get_keypoints(img)
    skeletons_with_box = []
    if keypoints is not None:
        for keypoint in keypoints:
            bbox =  utils.trasnform_to_wh(utils.get_rectangle_from_keypoints(keypoint))
            bbox_xy = utils.trasnform_to_xy(bbox)
            x1,y1,x2, y2 = bbox_xy
            p1 = Polygon([(x1,y1), (x1,y2), (x2, y1), (x2, y2)])
            for det_bbox in detections_boxes:      
                det_bbox_xy = utils.trasnform_to_xy(det_bbox)
                x1,y1,x2, y2 = det_bbox_xy
                p2 = Polygon([(x1,y1), (x1,y2), (x2, y1), (x2, y2)])
                difference = np.sum(np.abs((np.array(bbox_xy) - np.array(det_bbox_xy))))
                if difference < 60 and p1.intersects(p2):
                    bbox = det_bbox
                    break
            keypoint = utils.transform_openpose_skl_to_posetrack_skl(keypoint)
            skeletons_with_box.append((bbox, keypoint))

    return skeletons_with_box

def track_skeletons_with_box(img, skeletons_with_box):
    bbox_detection = [element[0] for element in skeletons_with_box]
    tracked_data = tool_tracker_deepsort.get_ids_from_image(img, bbox_detection)
    box_skeleton_id_list = []
    for track in tracked_data:
        id_num = track[0]
        bbox_detection = track[1]
        bbox_tracker = track[2]
        keypoint = None

        bbox_detection = bbox_detection if bbox_detection is not None else bbox_tracker
        for detection in skeletons_with_box:
            if np.sum(np.array(bbox_detection) - np.array(detection[0])) == 0:
                if detection[1] is not None:
                    keypoint = detection[1]
                    break
        
        if keypoint is None:
            keypoint = get_skeleton_from_crop(img, bbox_detection)
        
        box_skeleton_id_list.append((id_num,bbox_detection, keypoint))
    return box_skeleton_id_list

def get_skeleton_from_crop(img, bbox_crop, pixes_around_detection=10, resize_multiplier = 2):
    def clamp(n, minn, maxn):
        return max(min(maxn, n), minn)
    bbox_crop = np.int0(bbox_crop)
    x,y,w,h = bbox_crop
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
    keypoints, output_image = tool_skeleton_openpose.get_keypoints(croped_img)
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

    return keypoints

#Save data into json file
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
        person_id, bbox_detection, keypoints = elem
        bbox = bbox_detection
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

def run(img):
    #Get box and skeletons
    skeletons_with_box = get_skeletons_with_box(img)
    #Track
    skeletons_with_box_id = track_skeletons_with_box(img, skeletons_with_box)

    for elem in skeletons_with_box_id:
            person_id, bbox_detection, keypoints = elem
            img = image_annotator.draw_box(img, bbox_detection, color=(255,255,255))
            img = image_annotator.draw_annotation(img, (bbox_detection[0], bbox_detection[1]),"Id:" + str(person_id), color=(255,255,255))
            img = image_annotator.draw_skeleton(img, keypoints, color=(255,255,255))
            
            # if keypoints is not None:
            #     left_ear = keypoints[3]
            #     lef_ankle = keypoints[15]
            #     if left_ear[2] != 0 and lef_ankle[2] != 0:
            #         print("---")
            #         height = distance.euclidean(lef_ankle[0:2], left_ear[0:2])
            #         print(height)
            #         img = image_annotator.draw_annotation(img, (bbox_detection[0], bbox_detection[1]),"Hg:" + str(int(height)), color=(255,0,255))

    #Load info into json
    load_into_json(path , skeletons_with_box_id)
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
            #img = image_annotator.remove_distortion(img)
            run(img)
        with open(directory_path + "/data.json", 'w', encoding='utf-8') as f:
            json.dump(json_object, f, ensure_ascii=False, indent=4)
    elif file_type == "wbc":
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            run(frame)
    elif file_type == "mp4":
        #ask to open a directory
        # file_path = filedialog.askopenfile(title="Select file")

        directory_path = filedialog.askdirectory(title="Select directory")
        #iterate thorugh all the images in the directory
        for file_path in glob.glob(directory_path + '/*'):
            filename =  str(os.path.basename(file_path)).replace(".mp4", "")
            directory = pathlib.Path(file_path).parent.absolute()
            directory = str(directory) + "\\" + filename
            if not os.path.exists(directory):
                os.makedirs(directory)
            cap = cv2.VideoCapture(file_path)
            counter = 0
            while(cap.isOpened()):
                counter += 1
                path = filename + "_" + str(counter) + ".jpg"
                path_to_save = directory +"\\" + filename + "_" + str(counter) + ".jpg"
                ret, frame = cap.read()
                cv2.imwrite(path_to_save, frame)  
                if frame is None:
                    break
                # read image
                run(frame)
            with open(directory + "\\data.json", 'w', encoding='utf-8') as f:
                json.dump(json_object, f, ensure_ascii=False, indent=4)

            #Save data into json file
            image_id = 0
            annotation_id = 0
            json_object = {}

            #Store categories like PoseTrack
            with open(r"resources\json\skeleton_map.json") as json_file:
                data = json.load(json_file)  
                json_object["categories"] = data