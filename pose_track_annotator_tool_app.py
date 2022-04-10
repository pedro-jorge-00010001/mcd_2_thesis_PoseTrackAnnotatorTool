#https://ttkwidgets.readthedocs.io/en/sphinx_doc/_modules/ttkwidgets/timeline.html#TimeLine.create_scroll_region
from distutils.command.config import config
from tkinter import *
from tkinter import filedialog
from tkinter import Tk, Label, Button
from tkinter import messagebox as msgb
from tkinter import IntVar
from tkinter import colorchooser

from PIL import Image
from PIL import ImageTk

import imutils
import json
import cv2

import  utilities.image_annotator as image_annotator
from enums.AgeGroup import AgeGroup
from enums.Gender import Gender

from configparser import ConfigParser
from ttkwidgets import TimeLine
from utilities.utils import get_number_to_string
import string
import random
from colormap import rgb2hex

IMAGE_WIDTH = 1400
IMAGE_HEIGHT = 790

class Gui:
    
    def __init__(self, master):
        self.master = master
        # disable resize
        self.master.resizable(False, False)
        master.title('PoseTrackAnnotatorTool')
        
        # load configurations
        self.config = ConfigParser()
        self.config.read('config.ini')
        annotation_path = self.config['paths']['annotation_path']

        # initialize object variables
        self.json_data = None
        self.left_images_number = 0
        self.stop_current_vid = False
        self.pause_image_flag = False
        self.current_annotations = None
        self.current_image_shape = (0,0,0)
        self.gender_selected = IntVar(master)
        self.age_group_selected = IntVar(master)
        self.person_selected_id = None
        self.show_anotations = True

        # REGISTER BUTTONS COMMANDS
        select_file_cmd = master.register(self.select_file)
        select_default_data_path = master.register(self.select_default_data_path)
        play_images_seq_cmd = master.register(self.play_images_seq)
        pause_images_seq_cmd = master.register(self.pause_images_seq)
        save_annotation_cmd = master.register(self.save_annotation)
        hide_anotations_cmd = master.register(self.hide_anotations)
        add_action_event = master.register(self.add_action_event)

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
        self.settings_menu.add_command(label="Change Default Images Path", command= select_default_data_path)

        self.menu.add_cascade(label = "File", menu=self.file_menu)
        self.menu.add_cascade(label = "Settings", menu=self.settings_menu)
        
        self.path_label = Label(root, text = annotation_path)      
        #   => IMAGE PANEL
        #self.image_panel = PanedWindow(bd = 0, bg="white", width= 800, height=450)
        self.image = Canvas(master, width = IMAGE_WIDTH, height=IMAGE_HEIGHT)
        self.image.bind("<Button 1>", self.click_event)
        # self.image_panel.add(self.image)

        #   => TOOLS PANEL
        self.tools_panel = PanedWindow(bd = 4,orient= VERTICAL, width= 200, height=450)
        play_button = Button(self.tools_panel, text = "Play", command = play_images_seq_cmd)
        stop_button = Button(self.tools_panel, text = "Pause", command = pause_images_seq_cmd)
        hide_button = Button(self.tools_panel, text = "Hide/Show anotations", command = hide_anotations_cmd)
        self.slicer_button = Scale(master, from_=50, to=300, resolution=1, orient=HORIZONTAL, showvalue=False)
        self.slicer_button.set(167)
        self.person_selected_label = Label(root, text = "Person Id: " + str(self.person_selected_id))
        self.tools_panel.add(play_button)
        self.tools_panel.add(stop_button)
        self.tools_panel.add(hide_button)
        self.tools_panel.add(self.slicer_button)
        self.tools_panel.add(self.person_selected_label)
        #       => GENDER PANEL
        self.gender_panel = PanedWindow(bd = 4,orient= VERTICAL,width= 200, height=80)
        label = Label(root, text = "Gender:") 
        r1 = Radiobutton(root, text="Male", value=1, variable=self.gender_selected)
        r2 = Radiobutton(root, text="Female", value=2, variable=self.gender_selected)
        self.gender_panel.add(label)
        self.gender_panel.add(r1)
        self.gender_panel.add(r2)
        self.tools_panel.add(self.gender_panel)
        #       =>age panel
        self.age_panel = PanedWindow(bd = 5,orient= VERTICAL ,width= 100, height=150)
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

        #   => timeline
        self.timeline = TimeLine(
            master = root
        )
        self.timeline.draw_timeline()
        # =>  timeline menu
        
        self.timeline._canvas_categories.bind_all()
        self.timeline_menu = Menu(self.master, tearoff=False)
        self.timeline_menu.add_command(label="Some Action", command=add_action_event)
        
        # LAYOUT
        self.path_label.grid(column=0, row=0)
        #
        self.image.grid(column=0, row=1)
        #self.image_panel.grid(column=0, row=2)
        #   => LAYOUT TOOLS PANEL
        self.tools_panel.grid(column=1, row=1)
        self.timeline.grid(row=2)
        self._load_data(annotation_path)
    
    def add_action_event(self):
        print("id selected",self.action_id_selection)
        try:
            frame_number = round(float(self.timeline._time_label.cget("text")))
        except:
             frame_number = 0
        self.timeline.tag_configure(get_number_to_string(self.action_id_selection), hover_border=2)   
        # r,g,b = (round(random.random()*255), round(random.random()*255), round(random.random()*255)) 
        # hex = rgb2hex(r,g,b)
        self.timeline.create_marker(get_number_to_string(self.action_id_selection), frame_number, frame_number+2,
            tags=(get_number_to_string(self.action_id_selection),), text="Do nothing", background= "#5fedce" ,border = 1)
        

    def move_time_pointer_event(self, event):
        # stop video when moving the pointer
        self.pause_image_flag = True
        # get time pointer number
        frame_number = round(float(self.timeline._time_label.cget("text")))
        # update images left
        self.left_images_number = len(self.json_data["images"]) - frame_number -1 
        self._set_image(frame_number)
    
    def select_file(self):
        annotation_path = filedialog.askopenfilename(filetypes = [
            ("Json files", ".json")])
        self.stop_current_vid = True
        if len(annotation_path) > 0:
            self._load_data(annotation_path)
        else:
            self.image.image = ""
            self.path_label.configure(text = self.config['paths']['annotation_path'])

    def select_default_data_path(self):
        directory_path = filedialog.askdirectory(title="Select directory")
        self.stop_current_vid = True
        if len(directory_path) > 0:
            self.config.set('paths', 'image_path', directory_path)
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)

    def play_images_seq(self):
        self.stop_current_vid = False   
        file_path = self.path_label.cget("text")
        if self.pause_image_flag == True:
            self.pause_image_flag = False
            self.image.after(200, self.visualize)
        else:
            if file_path != 'Empty':
                data = None
                with open(file_path) as json_file:
                    data = json.load(json_file)       
                self.json_data = data
                self.left_images_number = len(self.json_data["images"])
                self.visualize()
    
    def hide_anotations(self):
        self.left_images_number += 1
        self.show_anotations = not self.show_anotations
        self.visualize()

    def click_event(self, eventorigin):
        #Multipliers to get the current rectangle for the resized image
        x_multiplier = IMAGE_WIDTH/self.current_image_shape[1]
        y_multiplier = IMAGE_HEIGHT/self.current_image_shape[0]

        #Point
        xP = eventorigin.x
        yP = eventorigin.y

        self.person_selected_id = None

        #head box
        for current_annotation in self.current_annotations:
            try:
                box_points = current_annotation["bbox_head"]
                #Rectangle
                x1 = int(box_points[0]*x_multiplier)
                y1 = int(box_points[1]*y_multiplier)
                x2 = x1 + int(box_points[2]*x_multiplier)
                y2 = y1 + int(box_points[3]*y_multiplier)                             
                print(x1,y1,x2,y2)
                if (x1 < xP and xP < x2):
                    if (y1 < yP and yP < y2):
                        self.person_selected_id = current_annotation["track_id"]                   
                        print(current_annotation["track_id"])
                        break
            except:
                print("Doesn't have head box")

        if self.person_selected_id == None:
            #body box
            for current_annotation in self.current_annotations:
                try:
                    box_points = current_annotation["bbox"]
                    #Rectangle
                    x1 = int(box_points[0]*x_multiplier)
                    y1 = int(box_points[1]*y_multiplier)
                    x2 = x1 + int(box_points[2]*x_multiplier)
                    y2 = y1 + int(box_points[3]*y_multiplier)                             
                    print(x1,y1,x2,y2)
                    if (x1 < xP and xP < x2):
                        if (y1 < yP and yP < y2):
                            self.person_selected_id = current_annotation["track_id"]                   
                            print(current_annotation["track_id"])
                            break
                except:
                    print("Doesn't have body box")
        self.person_selected_label.config(text ="Person Id: " + str(self.person_selected_id))
        
        #Update interface
        if 'other' in self.json_data:
            other_json = self.json_data['other']
            track_id_value = list(filter(lambda f: (f["track_id"] == self.person_selected_id), other_json))
            if track_id_value != []:
                gender = Gender[track_id_value[0]['gender']].value
                age = AgeGroup[track_id_value[0]['age_group']].value
                self.gender_selected.set(gender)
                self.age_group_selected.set(age)
            else:
                self.gender_selected.set(0)
                self.age_group_selected.set(0)
            
    

    def save_annotation(self):
        if self.person_selected_id != None and self.gender_selected.get() != 0 and self.age_group_selected.get() != 0:
            gender = Gender(self.gender_selected.get()).name          
            age = AgeGroup(self.age_group_selected.get()).name

            if 'other' in self.json_data:
                other_json = self.json_data['other']
                if list(filter(lambda f: (f["track_id"] == self.person_selected_id), other_json)):                   
                    annotations_except_this = list(filter(lambda f: (f["track_id"] != self.person_selected_id), other_json))
                    annotations_except_this.append({
                        'track_id': self.person_selected_id,
                        'gender' : gender,
                        'age_group': age
                    })
                    self.json_data['other'] = annotations_except_this
                else:
                    element_list = self.json_data['other']
                    if type(element_list) is dict:
                        element_list = [element_list]
                    element_list.append({
                        'track_id': self.person_selected_id,
                        'gender' : gender,
                        'age_group': age
                    })  
                    self.json_data['other'] = element_list
                    #print(self.json_data['other'])
            else:
                self.json_data['other'] = [{
                    'track_id': self.person_selected_id,
                    'gender' : gender,
                    'age_group': age
                }]
            self.left_images_number += 1
            self.visualize()
            with open(self.path_label.cget("text"), 'w', encoding='utf-8') as f:
                json.dump(self.json_data, f, ensure_ascii=False, indent=4)
        else:
            msgb.showinfo("Alert", "Please select a person, by clicking over it\nOr select a gender or age-group")

    def pause_images_seq(self):
        self.pause_image_flag = True

    def visualize(self):
        #update images left
        self.left_images_number -= 1
        if self.json_data != None and self.stop_current_vid != True:
            if self.left_images_number > 0:
                image_number = len(self.json_data["images"]) - self.left_images_number - 1
                self._set_image(image_number)
                if self.pause_image_flag != True:                
                    self.image.after(300 - self.slicer_button.get(), self.visualize)

    def _load_data(self , annotation_path):
        self.path_label.configure(text = annotation_path)
        self.config.set('paths', 'annotation_path', annotation_path)
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)
        
        with open(annotation_path) as json_file:
                data = json.load(json_file)       
        self.json_data = data
        self.left_images_number = len(self.json_data["images"])
        
        annotations = self.json_data["annotations"]
        annotations_track_ids = [x['track_id'] for x in annotations]
        persons_len = max(annotations_track_ids) + 1

        self._set_image(0)

        # update timeline
        vocabulary = ['A',]
        self.timeline.destroy()
        self.timeline.__init__(master = root, 
            height=100, width = 1300, 
            extend=True,  zoom_enabled = False, 
            start = 0.0, 
            resolution= 0.022, tick_resolution = 1.0,
            unit = 's',
            categories={get_number_to_string(key): {"text": "Person-{}".format( key)} for key in range(0, persons_len)},
            finish = float(self.left_images_number-1), snap_margin = 2
        )
        
        self.timeline.draw_timeline()   
        self.timeline._canvas_ticks.bind("<ButtonRelease-1>", self.move_time_pointer_event)
        self.timeline._timeline.bind("<ButtonPress-3>", self.timeline_rclick_event)
        self.timeline.grid(row=2)
        self.timeline._timeline.bind("<Double-Button-1>", self.double_click_event)
        # self.timeline.config(menu = menu)
    
    def double_click_event(self, event):
        def click_cancel():
            self.timeline.update_marker(iid, background=tag_brackground)
            pop.destroy()

        def click_ok():
            start = float(round(float(selected_tag['start'])))
            finish = float(round(float(selected_tag['start']))) + float(frame_lenght_label.get())
            if start == finish:
                finish = start + 1
            
            self.timeline.update_marker(iid,text = name_label.get(), 
                start = start, finish = finish, 
                background = button_color.cget('bg'))
            pop.destroy()

        def pick_color():
            color = colorchooser.askcolor()[1]
            button_color.config(bg=color)
            pop.deiconify()

        def delete_marker():
            self.timeline.delete_marker(iid)
            self.timeline._active = None
            pop.destroy()

        self.timeline.update_active()
        iid = self.timeline.current_iid
        if iid is None:
            return
        
        selected_tag = self.timeline._markers[iid]
        tag_brackground = selected_tag['background']
        self.timeline.update_marker(iid, background="gray")
        
        pop = Toplevel(self.master)
        pop.title("Annotation: " + selected_tag['text'])
        pop.geometry("%dx%d+%d+%d" % (250, 100, event.x_root, event.y_root))
        pop.tkraise(self.timeline)
        pop.wm_resizable(False,False)
        # Edit name
        Label(pop, text="Edit name").grid(row=0, column=0)
        name_label = StringVar(pop)
        name_label.set(selected_tag['text'])
        Entry(pop, textvariable = name_label, width=20).grid(row=0, column=1)

        # Edit frames lenght
        Label(pop, text="Frames lenght").grid(row=1, column=0)
        frame_lenght_label = StringVar(pop)
        frame_lenght_label.set(str(int(round(float(selected_tag['finish']))-float(selected_tag['start']))))
        Entry(pop, textvariable = frame_lenght_label, width=20).grid(row=1, column=1)
        
        # Edit color
        label_color = Label(pop, text="Color:")
        label_color.grid(row=2, column=0, sticky='nesw')

        #Buttons
        button_color = Button(pop, text = "", command= pick_color,bg=tag_brackground, bd=0)
        button_color.grid(row=2, column=1,sticky='nesw')
        button_ok = Button(pop, text="Ok", command = click_ok, bd=1)
        button_ok.grid(row=3, column=0,sticky='nesw')

        button_remove = Button(pop, text="Remove", command = delete_marker, bd=1)
        button_remove.grid(row=3, column=1,sticky='nesw')
        
        button_cancel = Button(pop, text="Cancel", command= click_cancel, bd=1)
        button_cancel.grid(row=3, column=2,sticky='nesw')


    def timeline_rclick_event(self, event):       
        self.action_id_selection = event.y//20
        self.timeline_menu.tk_popup(event.x_root,event.y_root )

    def _set_image(self, image_number):
        self.timeline.set_time(float(image_number))
        try:
            self.timeline._time_label['text'] = str(image_number)
        except: 
            pass
        # get image
        img = self.json_data["images"][image_number]
        if self.show_anotations:
            images_directory_path = self.config['paths']['image_path']
            img, current_annotations = image_annotator.annotate_image(img, self.json_data,images_directory_path)
            self.current_annotations = current_annotations                
            self.current_image_shape = img.shape
        else:
            img = cv2.imread(img["file_name"])
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # resize
        img = imutils.resize(img, width=IMAGE_WIDTH, height=IMAGE_HEIGHT)
        im = Image.fromarray(img)            
        img = ImageTk.PhotoImage(image=im)
        self.image.create_image(0, 0, image=img, anchor=NW)
        self.image.image = img

root = Tk()
my_gui = Gui(root)
root.mainloop()