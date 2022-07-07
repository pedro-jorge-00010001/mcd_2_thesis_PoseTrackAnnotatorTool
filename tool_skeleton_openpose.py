# It requires OpenCV installed for Python (Note: Python 3.8 doesnt work, try out python 3.9)
#How to run this app
# Clone https://github.com/CMU-Perceptual-Computing-Lab/openpose#installation on the libraries folder
# Build it like in this video https://www.youtube.com/watch?v=QC9GTb6Wsb4&list=LL&index=1
# Run the app from 
import sys
import cv2
import os
from sys import platform
import argparse
from tkinter import filedialog
import glob

def get_keypoints(img):
    datum = op.Datum()
    datum.cvInputData = img
    opWrapper.emplaceAndPop(op.VectorDatum([datum]))
    return datum.poseKeypoints, datum.cvOutputData

try:
    # Import Openpose (Windows/Ubuntu/OSX)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    try:
        # Windows Import
        if platform == "win32":
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append(r'libraries\openpose\build\python\openpose\Release');      
            os.environ['PATH']  = os.environ['PATH'] + ';' + r'libraries\openpose\build\x64\Release;' + r'libraries\openpose\build\bin;'
            import pyopenpose as op
        else:
            # Change these variables to point to the correct folder (Release/x64 etc.)
            #sys.path.append('../../python');
            # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
            # sys.path.append('/usr/local/python')
            #from openpose import pyopenpose as op
            pass
    except ImportError as e:
        print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
        raise e

    parser = argparse.ArgumentParser()    
    params = dict()
    params["model_folder"] = r"libraries\openpose\models"
    
    # Starting OpenPose
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()

except Exception as e:
    print(e)
    sys.exit(-1)


if __name__=="__main__": 
    directory_path = filedialog.askdirectory(title="Select directory")
    directory_path += '/*'  
    for path in glob.glob(directory_path):
        # Process Image
        path = path.replace("/", "\\")
        imageToProcess = cv2.imread(path)

        keypoints, output_image = get_keypoints(imageToProcess)

        for keypoint in keypoints:
            print(keypoint)

        # Display Image
        #print("Body keypoints: \n" + str(keypoints))
        cv2.imshow("OpenPose 1.7.0 - Tutorial Python API", output_image)
        cv2.waitKey(0)
        if cv2.waitKey(1) & 0xFF==ord('q'):
            break

    cv2.destroyAllWindows()


