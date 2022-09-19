from enums.AgeGroup import AgeGroup
from enums.Gender import Gender
from views.generated.MainMenuGenerated import MainMenuGenerated
from views.PathConfigurationView import PathConfigurationView
from views.ImageView import ImageView
from views.TimelineView import TimelineView
from configparser import ConfigParser
import json
import  utilities.image_annotator as image_annotator
import cv2
import utilities.utils as utils

from PIL import Image
from PIL import ImageTk
import numpy as np
import os
from tkinter import messagebox
from utilities.lazy_decoder import LazyDecoder

class MainMenuView(MainMenuGenerated):
    def __init__(self, master=None):
        super().__init__(master)
        self._init_custom_views()
        self._init_gui_options()
        self._init_custom_variables()
        self._load_data()
        

    def _init_gui_options(self):
        self.age_group_combobox.bind("<<ComboboxSelected>>",lambda e: self.frame1.focus())
        self.gender_combobox.bind("<<ComboboxSelected>>",lambda e: self.frame1.focus())

    def _init_custom_views(self):
        self.image_view = ImageView(self, self.image_view)
        self.image_view.pack(fill="x", side="top")
        # self.timeline_view = TimelineView(self, self.timeline_view)
        # self.timeline_view.pack(expand="false", fill="x", side="bottom")

    def _init_custom_variables(self):
        #load configs
        self.config = ConfigParser()
        self.config.read('config.ini')

        # initialize object variables
        self.json_data = None
        self.left_images_number = 0
        self.pause_bool = False
        self.pause_image_flag = False
        
        self.show_annotations_bool = True
        self.video_enabled = self.config['paths']['video_path'] != ""
        if self.video_enabled:
            self.cap = cv2.VideoCapture(self.config['paths']['video_path'])

    def _load_data(self):
        last_frame = int(self.config['frames']['frame_id'])
        annotation_path = self.config['paths']['annotation_path']
        if os.path.exists(annotation_path):            
            with open(annotation_path) as json_file:
                data = json.load(json_file, cls=LazyDecoder)       
            
            self.json_data = data
            self.left_images_number = len(self.json_data["images"])
            
            annotations = self.json_data["annotations"]
            annotations_track_ids = [x['track_id'] for x in annotations]
            annotations_track_ids = list(sorted(set(annotations_track_ids)))
            if not self.video_enabled:
                path = utils.build_path(self.config['paths']['folder_path'].replace("/", "\\"), self.json_data["images"][0]["file_name"].replace("/", "\\"))
                if os.path.exists(path):
                    self.set_image(0)
            
                else:
                    messagebox.showerror(title="Image not found", message="The image referenced by the annotation cannot be found\nPlease verify the images path")

            # update timeline
            # self.timeline_view.update_timeline(self.left_images_number, annotations_track_ids)
            
            #Load timeline data
            # self.timeline_view.load_data(self.json_data.get("actions", None))
            self.set_image(last_frame)
        else:
            messagebox.showerror(title="Annotation not found", message="The selected annotation doesn't exist\nPlease verify the path or select other annotation")

    #MENU events
    #Overrides MainMenuGenerated
    def open_path_configuration(self):
        self.pause_bool = True
        self.path_configuration_view = PathConfigurationView()
        self.path_configuration_view.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.path_configuration_view.grab_set()
        if self.video_enabled: self.cap.release()

    #Overrides MainMenuGenerated
    def exit_event(self):
        exit()

    #TOOL events
    #Overrides MainMenuGenerated
    def play_event(self):
        self.pause_bool = False
        json_path = self.config['paths']['annotation_path']
        if self.pause_image_flag == True:
            self.pause_image_flag = False
            self.image_view.after(200, self.visualize)
        else:
            if json_path != "":
                data = None
                with open(json_path) as json_file:
                    data = json.load(json_file)       
                self.json_data = data
                self.visualize()
    
    # #Overrides MainMenuGenerated
    def pause_event(self):
        self.pause_image_flag = True
        self.save_current_frame_id()

    # #Overrides MainMenuGenerated
    def hide_event(self):
        self.left_images_number += 1
        self.show_annotations_bool = not self.show_annotations_bool
        self.visualize()

    # #Overrides MainMenuGenerated
    def save_event(self):
        if self.person_selected_id.get() != 0:
            gender = Gender.get_enum(self.gender_selected.get()).name
            age_group = AgeGroup.get_enum(self.age_group_selected.get()).name
            value_dict = {
                            'track_id': self.person_selected_id.get(),
                            'gender' : gender,
                            'age_group': age_group
                        }
            self._update_json_info('characteristics', value_dict)
            with open(self.config['paths']['annotation_path'], 'w', encoding='utf-8') as f:
                json.dump(self.json_data, f, ensure_ascii=False, indent=4)
            self.left_images_number += 1
            self.visualize()

    
    # #Overrides MainMenuGenerated
    # def open_path_configuration(self):
    #     pass
    
    # #Overrides MainMenuGenerated
    # def exit_event(self):
    #     pass


    #Logic functions
    def visualize(self):
        #update images left
        self.left_images_number -= 1
        if self.json_data != None and self.pause_bool != True:
            if self.left_images_number > 0:
                image_number = len(self.json_data["images"]) - self.left_images_number - 1
                self.set_image(image_number)
                if self.pause_image_flag != True:
                    velocity = 1001 - self.slicer_button.get()
                    self.image_view.after(velocity, self.visualize)

    
    def set_image(self, image_number):
        if image_number < 0:
            image_number = 0
        self.left_images_number = len(self.json_data["images"]) - image_number - 1
        # To do:
        # self.timeline_view.set_time(float(image_number))
        # get image
        img_json = self.json_data["images"][image_number]
        images_directory_path = self.config['paths']['folder_path']
        current_annotations = None

        if self.video_enabled:
            self.cap.set(1,image_number)
            ret, img = self.cap.read()
        else:
            img = cv2.imdecode(np.fromfile(utils.build_path(images_directory_path.replace("/", "\\"), img_json["file_name"].replace("/", "\\")), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        if self.show_annotations_bool:
            img, current_annotations = image_annotator.annotate_image(img_json, img, image_number, self.json_data)             

        current_image_shape = img.shape
        # resize
        img = cv2.resize(img, (self.image_view.image_witdh, self.image_view.image_height))
        im = Image.fromarray(img)            
        img = ImageTk.PhotoImage(image=im)
        self.image_view.show_image(img,current_annotations, current_image_shape)
        self.config.set('frames', 'frame_id', str(image_number))

    def save_current_frame_id(self):
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    def _update_json_info(self, topic, value_dict, update_element_if_in = True):
        if topic in self.json_data:
            element_list = self.json_data[topic]

            if list(filter(lambda f: (f["track_id"] == value_dict["track_id"]), element_list)) and update_element_if_in:   
                annotations_except_this = list(filter(lambda f: (f["track_id"] != value_dict["track_id"]), element_list))
                annotations_except_this.append(value_dict)
                self.json_data[topic] = annotations_except_this
            else:
                if type(element_list) is dict:
                    element_list = [element_list]
                element_list.append(value_dict)
                self.json_data[topic] = element_list
        else:
            self.json_data[topic] = [value_dict]

    def change_person_selected_label(self, person_selected_id):
        self.person_selected_id.set(person_selected_id)
            
        #Update interface
        if 'characteristics' in self.json_data:
            other_json = self.json_data['characteristics']
            track_id_value = list(filter(lambda f: (f["track_id"] == self.person_selected_id), other_json))
            if track_id_value != []:
                gender = Gender[track_id_value[0]['gender']].value
                age = AgeGroup[track_id_value[0]['age_group']].value
                self.gender_selected.set(gender)
                self.age_group_selected.set(age)
            else:
                self.gender_selected.set(0)
                self.age_group_selected.set(0)
        self.save_current_frame_id()

    def on_closing(self):
        self.config.read('config.ini')
        self.path_configuration_view.destroy()
        self.video_enabled = self.config['paths']['video_path'] != ""
        if self.video_enabled:
            self.cap = cv2.VideoCapture(self.config['paths']['video_path'])
        
        