from tkinter import filedialog
import glob
import cv2
import torch
import numpy as np
import tracker_deepsort
import skeleton_openpose
from utilities import utils as ut

#load models
yolo_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

#threshold
yolo_model.conf = 0.45
yolo_model.classes = [0]


if __name__=="__main__":
    #ask to open a directory
    directory_path = filedialog.askdirectory(title="Select directory")
    directory_path += '/*'

    #iterate thorugh all the images in the directory
    for path in glob.glob(directory_path):
        
        # read image
        imageToProcess = cv2.imread(path)
        
        # detect persons
        results = yolo_model(imageToProcess)
        detections_boxes = results.pandas().xyxy[0].iloc[:,0:4]
        detections_boxes = [detection for detection in detections_boxes._values]
        for bbox in detections_boxes:
            # print it
            bbox = ut.trasnform_wh_to_x2y2(bbox)
            # cv2.rectangle(imageToProcess, (int(bbox[0]), int(bbox[1])), (int(bbox[2] + bbox[0]), int(bbox[3] + bbox[1])),(255,0,0), 2)
            # cv2.putText(imageToProcess, "Yolov5",(int(bbox[0]), int(bbox[1])),0, 5e-3 * 200, (255,0,0),2)

        # get skeletons from persons
        keypoints, output_image = skeleton_openpose.get_keypoints(imageToProcess)
        detections_from_skeletons = []
        if keypoints is not None:
            for keypoint in keypoints:
                bbox =  ut.get_rectangle_from_keypoints(keypoint)
                detections_from_skeletons.append(bbox)
                
                # print it
                bbox = ut.trasnform_wh_to_x2y2(bbox)
                # cv2.rectangle(imageToProcess, (int(bbox[0]), int(bbox[1])), (int(bbox[2] + bbox[0]), int(bbox[3] + bbox[1])),(0,0,255), 2)
                # cv2.putText(imageToProcess, "OpenPose",(int(bbox[0]), int(bbox[1] - 25)),0, 5e-3 * 200, (0,0,255),2)

        detections = ut.get_boxes_diferents_between(detections_boxes, detections_from_skeletons)
        #detections = detections_boxes
        detections = [ut.trasnform_wh_to_x2y2(bbox) for bbox in detections]

        if len(detections):
            # track persons
            tracked_data = tracker_deepsort.get_ids_from_image(imageToProcess, detections)
            
            #print(detections_boxes)
            for track in tracked_data:
                id_num = track[0]
                bbox_detection = track[1]
                bbox_tracker = track[2]
                if bbox_detection is not None:
                    #Draw bbox from tracker.
                    cv2.rectangle(output_image, (int(bbox_detection[0]), int(bbox_detection[1])), (int(bbox_detection[2]), int(bbox_detection[3])),(255,255,255), 2)
                    #cv2.putText(imageToProcess, "Yolov5 + OpenPose",(int(bbox_detection[0]), int(bbox_detection[1] - 25)),0, 5e-3 * 200, (255,255,255),2)

                    #cv2.rectangle(imageToProcess, (int(bbox_tracker[0]), int(bbox_tracker[1])), (int(bbox_tracker[2]), int(bbox_tracker[3])),(0,255,0), 2)
                    #cv2.putText(imageToProcess, "DeepSort",(int(bbox_tracker[0]), int(bbox_tracker[1] - 25)),0, 5e-3 * 200, (0,255,0),2)
                    cv2.putText(output_image, "Id : " + str(id_num),(int(bbox_tracker[0]), int(bbox_tracker[1])),0, 5e-3 * 200, (0,255,0),2)

        #cv2.imshow("Data generator", np.squeeze(results.render()))
        cv2.imshow("Data generator", output_image)
        cv2.waitKey(0)
        if cv2.waitKey(1) & 0xFF==ord('q'):
            break

    cv2.destroyAllWindows()