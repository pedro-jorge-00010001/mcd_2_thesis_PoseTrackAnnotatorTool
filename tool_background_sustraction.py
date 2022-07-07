#Tutorials
#https://www.youtube.com/watch?v=nRt2LPRz704

import cv2
from tkinter import filedialog
import glob
import numpy as np

substractorMOG2 = cv2.createBackgroundSubtractorMOG2(detectShadows=False)
substractorKNN = cv2.createBackgroundSubtractorKNN(detectShadows=False)


if __name__=="__main__": 
    directory_path = filedialog.askdirectory(title="Select directory")
    directory_path += '/*'  
    for path in glob.glob(directory_path):
        # Process Image
        path = path.replace("/", "\\")
        frame = cv2.imread(path)

        maskMOG2 = substractorMOG2.apply(frame)
        # maskMOG2 = cv2.GaussianBlur(maskMOG2, (5,5), 0)


        maskKNN = substractorKNN.apply(frame)
        # maskKNN = cv2.GaussianBlur(maskKNN, (5,5), 0)

        mask = cv2.bitwise_or(maskMOG2, maskKNN)
        # # mask = cv2.GaussianBlur(mask, (5,5), 0)
        # # #Gaussian blur
        # # mask = cv2.GaussianBlur(mask, (5,5), 0)
        # # mask = cv2.GaussianBlur(mask, (5,5), 0)
        # # #mask = cv2.GaussianBlur(mask, (5,5), 0)
        
        # # #Erode (This will filter matrix of pixels that are minors that 5x5 pixel)
        # kernerl = np.ones((3,3), np.uint8)
        
        # mask = cv2.bilateralFilter(mask,9,75,75)
        # # # Thresholding to convert mask to binary map
        # # ret,thresh = cv2.threshold(mask,200,255,cv2.THRESH_BINARY)
        
        # kernal = np.ones((5,5), np.uint8)
        # dilation = cv2.dilate(mask, kernal, iterations=20)
        
        # mask = cv2.erode(mask, kernerl)
        # #Apply the mask to original image
        final = cv2.bitwise_and(frame, frame, mask = mask)
        
        cv2.imshow("applied mask", final)
        cv2.imshow("mask", mask)
        cv2.imshow("Normal", frame)

        # Display Image
        key = cv2.waitKey(15)
        if key == 27:
            break

    cv2.destroyAllWindows()