
from asyncore import read
import json
from tkinter import filedialog
from turtle import width
from utilities import utils
from utilities import image_annotator
import cv2 as cv
import numpy as np
from math import atan2, cos, sin, sqrt, pi

import importlib
import sys
sys.path.append(r'lib/3rdparty')


#human_silhoutte_extractor = __import__("human_silhoutte_extractor.Proposed Solution")
human_silhoutte_extractor = importlib.import_module("human_silhoutte_extractor.Proposed Solution")
import math
import re
import csv
import math

from utilities.videoreader import VideoReader

def clamp(n, minn, maxn):
  return max(min(maxn, n), minn)
        
def drawAxis(img, p_, q_, color, scale):
    p = list(p_)
    q = list(q_)

    ## [visualization1]
    angle = atan2(p[1] - q[1], p[0] - q[0]) # angle in radians
    hypotenuse = sqrt((p[1] - q[1]) * (p[1] - q[1]) + (p[0] - q[0]) * (p[0] - q[0]))

    # Here we lengthen the arrow by a factor of scale
    q[0] = p[0] - scale * hypotenuse * cos(angle)
    q[1] = p[1] - scale * hypotenuse * sin(angle)
    cv.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), color, 3, cv.LINE_AA)

    # create the arrow hooks
    p[0] = q[0] + 9 * cos(angle + pi / 4)
    p[1] = q[1] + 9 * sin(angle + pi / 4)
    cv.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), color, 3, cv.LINE_AA)

    p[0] = q[0] + 9 * cos(angle - pi / 4)
    p[1] = q[1] + 9 * sin(angle - pi / 4)
    cv.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), color, 3, cv.LINE_AA)

def getOrientation(pts, img):
  ## [pca]
  # Construct a buffer used by the pca analysis
  sz = len(pts)
  data_pts = np.empty((sz, 2), dtype=np.float64)
  for i in range(data_pts.shape[0]):
    if pts[i][2] != 0:
        data_pts[i,0] = int(pts[i][0])
        data_pts[i,1] = int(pts[i][1])
    # data_pts[i,0] = pts[i,0,0]
    # data_pts[i,1] = pts[i,0,1]
 
  # Perform PCA analysis
  mean = np.empty((0))
  mean, eigenvectors, eigenvalues = cv.PCACompute2(data_pts, mean)
 
#   # Store the center of the object
#   cntr = (int(mean[0,0]), int(mean[0,1]))
  ## [pca]
 
  ## [visualization]
  # Draw the principal components
#   cv.circle(img, cntr, 3, (255, 0, 255), 2)
#   p1 = (cntr[0] + 0.02 * eigenvectors[0,0] * eigenvalues[0,0], cntr[1] + 0.02 * eigenvectors[0,1] * eigenvalues[0,0])
#   p2 = (cntr[0] - 0.02 * eigenvectors[1,0] * eigenvalues[1,0], cntr[1] - 0.02 * eigenvectors[1,1] * eigenvalues[1,0])
#   drawAxis(img, cntr, p1, (255, 255, 0), 1)
#   drawAxis(img, cntr, p2, (0, 0, 255), 5)
 
  angle = atan2(eigenvectors[0,1], eigenvectors[0,0]) # orientation in radians
  ## [visualization]
 
  # Label with the rotation angle
#   label = str(-int(np.rad2deg(angle)) - 90) + " degrees"
#   textbox = cv.rectangle(img, (cntr[0], cntr[1]-25), (cntr[0] + 250, cntr[1] + 10), (255,255,255), -1)
#   cv.putText(img, label, (cntr[0], cntr[1]), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv.LINE_AA)
 
  return angle

def rotate_image(mat, angle):
    """
    Rotates an image (angle in degrees) and expands image to avoid cropping
    """

    height, width = mat.shape[:2] # image shape has 3 dimensions
    image_center = (width/2, height/2) # getRotationMatrix2D needs coordinates in reverse order (width, height) compared to shape

    rotation_mat = cv.getRotationMatrix2D(image_center, angle, 1.)

    # rotation calculates the cos and sin, taking absolutes of those.
    abs_cos = abs(rotation_mat[0,0]) 
    abs_sin = abs(rotation_mat[0,1])

    # find the new width and height bounds
    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    # subtract old image center (bringing image back to origo) and adding the new image center coordinates
    rotation_mat[0, 2] += bound_w/2 - image_center[0]
    rotation_mat[1, 2] += bound_h/2 - image_center[1]

    # rotate image with the new bounds and translated rotation matrix
    rotated_mat = cv.warpAffine(mat, rotation_mat, (bound_w, bound_h))
    return rotated_mat


def remove_black_borders(image):
    y_nonzero, x_nonzero, _ = np.nonzero(image)
    if not len(y_nonzero) and not len(x_nonzero):
      return image
    return image[np.min(y_nonzero):np.max(y_nonzero), np.min(x_nonzero):np.max(x_nonzero)]

annotation_path = filedialog.askopenfilename(filetypes = [("Json files", ".json")])
# directory_path = filedialog.askdirectory(title="Select directory")
video_reader = VideoReader()

data = None

with open(annotation_path) as json_file:
    data = json.load(json_file)

annotations = data["annotations"]
images = data["images"]

dict_data = dict()

for annotation in annotations:

    number_of_valid_keypoints = 0
    keypoints = []
    bbox_crop = np.int0(annotation["bbox"])
    x,y,w,h = bbox_crop
    xmax = x + w
    ymax = y + h
    x_crop_reverse = x
    y_crop_reverse = y
    

    for i in range(1,len(annotation["keypoints"])//3 + 1):
        end_pos = 3*i
        start_pos = end_pos - 1
        is_valid = annotation["keypoints"][start_pos:end_pos][0]
        start_pos = end_pos - 3
        current_points = annotation["keypoints"][start_pos:end_pos]
        keypoints.append([abs(current_points[0] - x), abs(current_points[1] - y), current_points[2]])
        number_of_valid_keypoints += is_valid 

    if  number_of_valid_keypoints > 8:
        image = list(filter(lambda f: (f["id"] == annotation["image_id"]), images))[0]
        frame_id = image["frame_id"]
        img = video_reader.read_frame_by_number(frame_id)
        image_path = image["file_name"]

        # path = utils.build_path(directory_path.replace("/", "\\"), image_path.replace("/", "\\"))
        # img = cv.imdecode(np.fromfile(path, dtype=np.uint8), cv.IMREAD_UNCHANGED)
        xmax_crop_reverse =  xmax 
        ymax_crop_reverse = ymax 
        #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        croped_img = img[y_crop_reverse:ymax_crop_reverse, x_crop_reverse:xmax_crop_reverse]


        
        # Apply background subtraction to extract foreground (silhouette)
        mask = human_silhoutte_extractor.makeSegMask(croped_img)
        
        # Apply thresholding to convert mask to binary map
        ret,thresh = cv.threshold(mask, 127, 255,cv.THRESH_BINARY)
        final = cv.bitwise_and(thresh, croped_img)
        # final = image_annotator.draw_skeleton(final, keypoints)
        
        new_points = []
        new_points.append(keypoints[5])
        new_points.append(keypoints[6])
        new_points.append(keypoints[12])
        new_points.append(keypoints[11])
        # point_line_top = (int((keypoints[5][0] + keypoints[6][0])/2), int((keypoints[5][1] + keypoints[6][1])/2) , 1)
        # point_line_down = (int((keypoints[12][0] + keypoints[11][0])/2), int((keypoints[11][1] + keypoints[11][1])/2), 1)
        final = remove_black_borders(final)
        
        # counting the number of pixels
        number_of_non_black_pix = np.sum(final != 0)
        number_of_black_pix = np.sum(final == 0)
        percentage_of_black_pix = number_of_black_pix/(number_of_non_black_pix + number_of_black_pix)
        print('Percetange of black pixels', percentage_of_black_pix)

        # Filter silhoute bad extractions
        #The percentage of black cannot be greather than 70%
        minimum_pixel_density = 20*64
        width, height, _ = final.shape
        if (not math.isnan(percentage_of_black_pix) and int(percentage_of_black_pix*100) <= 70 and minimum_pixel_density < width*height):
          # angle = getOrientation(new_points, final)
          # angle = -(180 -int(np.rad2deg(angle)) - 90)
          # #print(angle)
          
          # final = rotate_image(final, angle)
          # final = remove_black_borders(final)
          #cv.imshow('Final Image', final)

          # How to save it
          csv_columns = ['video_id','frame_number','person_id','gender','age_group','image_path','keypoints']
          # splited_vector = directory_path.split("/")
          #video_id
          # video_id = splited_vector[len(splited_vector)-1]
          video_id = video_reader.get_file_name()
          #person_id
          person_id = annotation['track_id']
          #gender
          current_person_other_info = list(filter(lambda f: (f["track_id"] == person_id), data["characteristics"]))[0]
          gender = current_person_other_info["gender"]
          #age_group
          age_group = current_person_other_info["age_group"]
          #keypoints
          keypoints = annotation['keypoints']

          skeleton_points_vector = []
          #skeleton points
          for i in range(1,len(keypoints)//3 + 1):
              end_pos = 3*i
              start_pos = end_pos - 3
              sk_point = keypoints[start_pos:end_pos]
              x_sk = max(sk_point[0] - x, 0)
              y_sk = max(sk_point[1] - y, 0)
              p_sk = sk_point[2]
              skeleton_points_vector.append(x_sk)
              skeleton_points_vector.append(y_sk)
              skeleton_points_vector.append(p_sk)

          frame_number = image["frame_id"]

          image_path = "data\\train_models_data\\images\\" + video_id + "_" + str(frame_number) +"_" + str(person_id)+ ".jpg"
          dict_data[video_id + "_" + str(frame_number) +"_" + str(person_id)] = {'video_id' : video_id, 'frame_number' : frame_number, 
          'person_id' : person_id, 'gender' : gender, 'age_group' : age_group, 'image_path' : image_path, 'keypoints': skeleton_points_vector}
          
          # final = image_annotator.draw_skeleton(final, skeleton_points_vector)
          cv.imwrite(image_path, final)
          #Key: video_id + frame_number + person_id
          # cv.waitKey(200)
          # cv.destroyAllWindows()



csv_file = "data\\train_models_data\\data.csv"
with open(csv_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns, delimiter=";")
    writer.writeheader()
    for key, value in dict_data.items():
      writer.writerow(value)
# annotations_track_ids = [x['track_id'] for x in annotations]
# annotations_track_ids = list(sorted(set(annotations_track_ids)))

