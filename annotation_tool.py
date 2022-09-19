#https://ttkwidgets.readthedocs.io/en/sphinx_doc/_modules/ttkwidgets/timeline.html#TimeLine.create_scroll_region
from email import utils
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import Tk, Label, Button
from tkinter import IntVar

from views.ImageView import ImageView
from views.TimelineView import TimelineView

from PIL import Image
from PIL import ImageTk

import os
import numpy as np
import imutils
import json
import cv2

import utilities.utils as utils
import utilities.image_annotator as image_annotator
from enums.AgeGroup import AgeGroup
from enums.Gender import Gender
from configparser import ConfigParser
from utilities.lazy_decoder import LazyDecoder

class Gui:
    
    def __init__(self, master):
        self.master = master
        
        # disable resize
        screen_width = self.master.winfo_screenwidth()
        if screen_width < 1920:
            self.master.resizable(True, True)
            self.master.state('zoomed')

        #self.master.attributes('-fullscreen', True)
        self.master.columnconfigure(0, weight = 1)
        self.master.rowconfigure(0, weight = 1)
        master.title('AnnotationTool')
        
        #Source: <a href="https://www.flaticon.com/free-icons/edit" title="edit icons">Edit icons created by Kiranshastry - Flaticon</a>
        root.iconbitmap(r"resources/images/edit.ico")
    
        # load configurations
        self.config = ConfigParser()
        self.config.read('config.ini')
        annotation_path = self.config['paths']['annotation_path']
        last_frame = self.config['frames']['frame_id']

        # initialize object variables
        self.json_data = None
        self.left_images_number = 0
        self.pause_bool = False
        self.pause_image_flag = False
        
        self.gender_selected = IntVar(master)
        self.age_group_selected = IntVar(master)
        self.person_selected_id = None
        self.show_annotations_bool = True

        # REGISTER BUTTONS COMMANDS
        select_file_cmd = master.register(self.select_file)
        select_default_data_path = master.register(self.select_default_data_path)
        play_images_seq_cmd = master.register(self.play_event)
        pause_images_seq_cmd = master.register(self.pause_event)
        save_annotation_cmd = master.register(self.save_event)
        hide_annotations_cmd = master.register(self.hide_event)
        left_key_cmd = master.register(self.left_key)
        right_key_cmd = master.register(self.right_key)
        
        self.master.bind('<Left>', left_key_cmd)
        self.master.bind('<Right>', right_key_cmd)


        # BUILD INTERFACE
        #   => Menu
        self.menu = Menu(self.master)
        master.config(menu = self.menu)
        #       => File 
        self.file_menu = Menu(self.menu, tearoff=0)
        self.file_menu.add_command(label="Open Annotation", command= select_file_cmd)
        self.file_menu.add_separator()
        self.file_menu.add_command(label = "Exit", command = exit)
        
        #       => Settings 
        self.settings_menu = Menu(self.menu, tearoff=0)
        self.settings_menu.add_command(label="Chose mp4", command= select_default_data_path)

        self.menu.add_cascade(label = "File", menu=self.file_menu)
        self.menu.add_cascade(label = "Settings", menu=self.settings_menu)
        
        self.path_label = Label(root, text = annotation_path)      
        
        self.image_view = ImageView(self, self.master)
        self.timeline_view = TimelineView(self, self.master)

        #   => TOOLS PANEL
        self.tools_panel = PanedWindow(bd = 4,orient= VERTICAL, width= 200, height=450)
        play_button = Button(self.tools_panel, text = "Play", command = play_images_seq_cmd)
        pause_button = Button(self.tools_panel, text = "Pause", command = pause_images_seq_cmd)
        hide_button = Button(self.tools_panel, text = "Hide/Show anotations", command = hide_annotations_cmd)
        self.slicer_button = Scale(master, from_=50, to=1000, resolution=1, orient=HORIZONTAL, showvalue=False)
        self.slicer_button.set(667)
        self.person_selected_label = Label(root, text = "Person Id: " + str(self.person_selected_id))
        self.tools_panel.add(play_button)
        self.tools_panel.add(pause_button)
        self.tools_panel.add(hide_button)
        self.tools_panel.add(self.slicer_button)
        self.tools_panel.add(self.person_selected_label)
        
        #       => GENDER PANEL
        self.gender_panel = PanedWindow(bd = 4,orient= VERTICAL, width= 200, height=80)
        label = Label(root, text = "Gender:") 
        r1 = Radiobutton(root, text="Male", value=1, variable=self.gender_selected)
        r2 = Radiobutton(root, text="Female", value=2, variable=self.gender_selected)
        self.gender_panel.add(label)
        self.gender_panel.add(r1)
        self.gender_panel.add(r2)
        self.tools_panel.add(self.gender_panel)
        #       =>age panel
        self.age_panel = PanedWindow(bd = 5,orient= VERTICAL , width= 100, height=150)
        label = Label(root, text = "Age:")
        a1 = Radiobutton(root, text="Child (00-14 years)", value=1, variable=self.age_group_selected)
        a2 = Radiobutton(root, text="Young (15-24 years)", value=2, variable=self.age_group_selected)
        a3 = Radiobutton(root, text="Adult (25-64 years)", value=3, variable=self.age_group_selected)
        a4 = Radiobutton(root, text="Senior (65 years and over)", value=4, variable=self.age_group_selected)
        
        self.age_panel.add(label)
        self.age_panel.add(a1)
        self.age_panel.add(a2)
        self.age_panel.add(a3)
        self.age_panel.add(a4)
        self.tools_panel.add(self.age_panel)


        save_button = Button(self.tools_panel, text = "Save annotations", command = save_annotation_cmd, height=150)
        self.tools_panel.add(save_button)

        # LAYOUT
        self.path_label.grid(column=0, row=0)
        self.image_view.grid(column=0, row=1)
        self.timeline_view.grid(column=None, row=2)
        self.tools_panel.grid(column=1, row=1)

        self.cap = cv2.VideoCapture(self.config['paths']['video_path'])
        self._load_data(annotation_path, int(last_frame))
    
    def left_key(self):
        self.pause_image_flag = True
        self.left_images_number += 2
        self.visualize()

    def right_key(self):
        # self.left_images_number += 1
        self.pause_image_flag = True
        if self.left_images_number == 1 : 
            self.left_images_number += 1

        self.visualize()

    # Done
    def select_file(self):
        annotation_path = filedialog.askopenfilename(filetypes = [
            ("Json files", ".json")])
        self.pause_bool = True
        if len(annotation_path) > 0:
            self._load_data(annotation_path, 0)
        else:
            self.image.image = ""
            self.path_label.configure(text = self.config['paths']['annotation_path'])

    def select_default_data_path(self):
        annotation_path = filedialog.askopenfilename(filetypes = [
            ("Open mp4 file", ".mp4")])
        self.pause_bool = True
        if len(annotation_path) > 0:
            self.config.set('paths', 'video_path', annotation_path)
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)

    def play_event(self):
        self.pause_bool = False   
        file_path = self.path_label.cget("text")
        if self.pause_image_flag == True:
            self.pause_image_flag = False
            self.image_view.after(200, self.visualize)
        else:
            if file_path != 'Empty':
                data = None
                with open(file_path) as json_file:
                    data = json.load(json_file)       
                self.json_data = data
                # self.left_images_number = len(self.json_data["images"])
                self.visualize()
    
    def hide_event(self):
        self.left_images_number += 1
        self.show_annotations_bool = not self.show_annotations_bool
        self.visualize()

    def update_person_id_in_json(self, person_selected_id, new_person_id, option = "n"):
        # Update annotations
        if 'annotations' in self.json_data:
            annotations_new = []
            image_number = len(self.json_data["images"]) - self.left_images_number - 1
            image_id = self.json_data["images"][image_number]["id"]
            for annotation in self.json_data['annotations']:
                #Conditions
                if annotation["track_id"] == person_selected_id and \
                    ((annotation['image_id'] > image_id and option == "n") or \
                    (annotation['image_id'] < image_id and option == "p") or  \
                    (annotation['image_id'] == image_id and option == "c") or  \
                    (option == "a")):
                    
                    annotation["track_id"] = int(new_person_id)
                    annotations_new.append(annotation)
                else:
                    annotations_new.append(annotation)
            self.json_data['annotations'] = annotations_new
        
        if 'characteristics' in self.json_data:
            characteristics_new = []
            image_id = self.json_data["images"][image_number]["id"]
            for annotation in self.json_data['characteristics']:
                #Conditions
                if annotation["track_id"] == person_selected_id:
                    annotation["track_id"] = int(new_person_id)
                    characteristics_new.append(annotation)
                else:
                    characteristics_new.append(annotation)
            self.json_data['characteristics'] = characteristics_new

        if 'actions' in self.json_data:
            actions_new = []
            image_id = self.json_data["images"][image_number]["id"]
            for annotation in self.json_data['actions']:
                #Conditions
                if annotation["track_id"] == person_selected_id:
                    annotation["track_id"] = int(new_person_id)
                    actions_new.append(annotation)
                else:
                    actions_new.append(annotation)
            self.json_data['actions'] = actions_new

        
        self.left_images_number += 1
        #refresh timeline
        annotations = self.json_data["annotations"]
        annotations_track_ids = [x['track_id'] for x in annotations]
        annotations_track_ids = list(sorted(set(annotations_track_ids)))    
        self.timeline_view.update_timeline(len(self.json_data["images"]), annotations_track_ids)
        self.timeline_view.load_data(self.json_data.get("actions", None))
        self.visualize()
        #characteristics
        #actions
    
    def _update_id_in_json(self, person_selected_id, new_person_id, option, topic):
        if topic in self.json_data:
            annotations_new = []
            image_number = len(self.json_data["images"]) - self.left_images_number - 1
            image_id = self.json_data["images"][image_number]["id"]
            for annotation in self.json_data[topic]:
                #Conditions
                if annotation["track_id"] == person_selected_id and \
                    ((annotation['image_id'] > image_id and option == "n") or \
                    (annotation['image_id'] < image_id and option == "p") or  \
                    (option == "a")):
                    
                    annotation["track_id"] = int(new_person_id)
                    annotations_new.append(annotation)
                else:
                    annotations_new.append(annotation)
            self.json_data[topic] = annotations_new


    def go_to_person_frame(self, person_selected_id):
        element_list = self.json_data['annotations']
        annotations_of_person_selected = list(filter(lambda f: (f["track_id"] == person_selected_id ), element_list))
        image_id = int(annotations_of_person_selected[0]["image_id"])
        self.set_image(image_id)
        pass

    def remove_person_from_json(self, person_selected_id):
        value_dict = {
                            'track_id': person_selected_id,

                        }
        self._remove_json_info('annotations', value_dict)
        self._remove_json_info('characteristics', value_dict)
        self._remove_json_info('actions', value_dict)
        self.pause_image_flag = True
        self.left_images_number += 1
        self.visualize()
        self.save_current_frame_id()
        #with open(self.path_label.cget("text"), 'w', encoding='utf-8') as f:
        #    json.dump(self.json_data, f, ensure_ascii=False, indent=4)
    
    def remove_person_from_json_frame(self, person_selected_id, annotation_id):
        if 'annotations' in self.json_data:
            element_list = self.json_data['annotations']
            image_number = len(self.json_data["images"]) - self.left_images_number
            if list(filter(lambda f: (f["id"] == annotation_id and f["track_id"] == person_selected_id and f["image_id"] == image_number), element_list)):   
                annotations_except_this = list(filter(lambda f: (f["id"] != annotation_id or f["track_id"] != person_selected_id or f["image_id"] != image_number), element_list))
                self.json_data['annotations'] = annotations_except_this
        self.pause_image_flag = True
        self.left_images_number += 1
        self.visualize()
        self.save_current_frame_id()

    def change_person_selected_label(self, person_selected_id):
        self.person_selected_label.config(text ="Person Id: " + str(person_selected_id))
        self.person_selected_id = person_selected_id
            
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
    

    def save_event(self):
        markers = self.timeline_view.get_markers()
        self.json_data['actions'] = []
        
        for key, value in markers.items():
            diff_len = round(float(value['finish']) -float(value['start']))
            start = int(round(float(value['start'])))
            end = int(start + diff_len)

            value_dict = {
                        "track_id": int(value['category']),
                        "action_name": value['text'],
                        "start_frame": start,
                        "finish_frame": end,
                        "start_frame_id": 'None for now',
                        "finish_frame_id": 'None for now',
                        "color" : value['background']
            }
            self._update_json_info('actions', value_dict, update_element_if_in = False)

        if self.person_selected_id != None:     
            if self.gender_selected.get() and self.age_group_selected.get():
                gender = Gender(self.gender_selected.get()).name          
                age = AgeGroup(self.age_group_selected.get()).name
                value_dict = {
                            'track_id': self.person_selected_id,
                            'gender' : gender,
                            'age_group': age
                        }
                self._update_json_info('characteristics', value_dict)

        self.left_images_number += 1
        self.visualize()
        with open(self.path_label.cget("text"), 'w', encoding='utf-8') as f:
            json.dump(self.json_data, f, ensure_ascii=False, indent=4)
        self.save_current_frame_id()
        

    def _remove_json_info(self, topic, value_dict):
        if topic in self.json_data:
            element_list = self.json_data[topic]
            if list(filter(lambda f: (f["track_id"] == value_dict["track_id"]), element_list)):   
                annotations_except_this = list(filter(lambda f: (f["track_id"] != value_dict["track_id"]), element_list))
                self.json_data[topic] = annotations_except_this

            
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

    def pause_event(self):
        self.pause_image_flag = True
        self.save_current_frame_id()

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

    def _load_data(self , annotation_path, last_image):
        if os.path.exists(annotation_path):

            self.path_label.configure(text = annotation_path)
            self.config.set('paths', 'annotation_path', annotation_path)
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)
            
            with open(annotation_path) as json_file:
                data = json.load(json_file, cls=LazyDecoder)       
            self.json_data = data
            self.left_images_number = len(self.json_data["images"])
            
            annotations = self.json_data["annotations"]
            annotations_track_ids = [x['track_id'] for x in annotations]
            annotations_track_ids = list(sorted(set(annotations_track_ids)))
            
            # update timeline
            self.timeline_view.update_timeline(self.left_images_number, annotations_track_ids)
            
            #Load timeline data
            self.timeline_view.load_data(self.json_data.get("actions", None))
            self.set_image(last_image)
        else:
            messagebox.showerror(title="Annotation not found", message="The selected annotation doesn't exist\nPlease verify the path or select other annotation")


    def set_image(self, image_number):
        if image_number < 0:
            image_number = 0
        self.left_images_number = len(self.json_data["images"]) - image_number - 1
        self.timeline_view.set_time(float(image_number))
        # To do:
        # self.timeline_view.set_time(float(image_number))
        # get image
        img_json = self.json_data["images"][image_number]
        current_annotations = None
        self.cap.set(1,image_number)
        ret, img = self.cap.read()
        
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

root = Tk()
my_gui = Gui(root)
root.mainloop()