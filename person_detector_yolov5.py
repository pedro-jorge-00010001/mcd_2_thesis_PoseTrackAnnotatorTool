import torch
from utilities import utils
from utilities import image_annotator
from tkinter import filedialog
import cv2
import glob

#load models
yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
yolo_model.classes = [0]


def detect_persons(img, conf_treshold = 0.45):
    #threshold
    yolo_model.conf = conf_treshold

    results = yolo_model(img)
    detections_boxes = results.pandas().xyxy[0].iloc[:,0:4]
    detections_boxes = [utils.trasnform_to_wh(detection) for detection in detections_boxes._values]
    return detections_boxes
    
if __name__=="__main__":
    #ask to open a directory
    directory_path = filedialog.askdirectory(title="Select directory")
    directory_path += '/*'

    #iterate thorugh all the images in the directory
    for path in glob.glob(directory_path):
        img = cv2.imread(path)

        detections = detect_persons(img)
        for box in detections:
            box = [int(point) for point in box]
            img = image_annotator.draw_box(img, box)

        cv2.imshow("Data generator", img)
        #cv2.waitKey(0)
        if cv2.waitKey(1) & 0xFF==ord('q'):
            break