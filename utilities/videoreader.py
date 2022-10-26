import cv2
from tkinter import filedialog
import os

class VideoReader:
    def __init__(self):
        self.video_path = filedialog.askopenfilename(filetypes = [("Mp4 files", ".mp4")])
        self.cap = cv2.VideoCapture(self.video_path)
        self.current_frame_number = 0

    def read_frame(self):
        self.cap.set(1, self.current_frame_number)
        self.current_frame_number += 1
        _, img = self.cap.read()
        return img

    def read_frame_by_number(self, image_number):
        self.current_frame_number = image_number
        return self.read_frame()

    def close(self):
        self.cap.release()

    def get_file_name(self):
        return os.path.basename(self.video_path)