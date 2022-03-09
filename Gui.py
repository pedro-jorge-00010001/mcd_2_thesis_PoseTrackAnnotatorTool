from tkinter import *
from tkinter import filedialog
from tkinter import Tk, Label, Button
from tkinter import messagebox as msgb
from tkinter import IntVar

from PIL import Image
from PIL import ImageTk
import  ImageAnnotator
import imutils

import json
import cv2

IMAGE_WIDTH = 1400
IMAGE_HEIGHT = 790
LABEL_EMPTY_PATH = "Empty path"

class Gui:
    
    def __init__(self, master):
        self.master = master
        #Disable resize
        self.master.resizable(False, False)
        master.title("PoseTrackAnnotatorTool")
        
        # INITIALITE OBJECT VARIABLES
        self.json_data = None
        self.left_images_number = 0
        self.stop_current_vid = False
        self.pause_image_flag = False
        self.current_annotations = None
        self.current_image_shape = (0,0,0)
        self.gender_selected = IntVar(master)
        self.person_selected_id = None
        self.show_anotations = True
         
        # REGISTER BUTTONS COMMANDS
        select_file_cmd = master.register(self.select_file)
        play_images_seq_cmd = master.register(self.play_images_seq)
        pause_images_seq_cmd = master.register(self.pause_images_seq)
        save_annotation_cmd = master.register(self.save_annotation)
        hide_anotations_cmd = master.register(self.hide_anotations)

        # BUILD INTERFACE
        self.visualize_button = Button(master, text = "Select an annotations file", command = select_file_cmd)
        self.path_label = Label(root, text = LABEL_EMPTY_PATH)      
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
        self.person_selected_label = Label(root, text = "Person Id: " + str(self.person_selected_id))
        self.tools_panel.add(play_button)
        self.tools_panel.add(stop_button)
        self.tools_panel.add(hide_button)
        self.tools_panel.add(self.person_selected_label)
        #       => GENDER PANEL
        self.gender_panel = PanedWindow(bd = 4,orient= HORIZONTAL,width= 200, height=50)
        label = Label(root, text = "Gender:") 
        r1 = Radiobutton(root, text="Male", value=1, variable=self.gender_selected)
        r2 = Radiobutton(root, text="Female", value=2, variable=self.gender_selected)
        self.gender_panel.add(label)
        self.gender_panel.add(r1)
        self.gender_panel.add(r2)
        self.tools_panel.add(self.gender_panel)
        #       =>AGE PANEL
        self.age_panel = PanedWindow(bd = 4,orient= HORIZONTAL,width= 100, height=30)
        label = Label(root, text = "Age:") 
        self.age = Entry(root)
        self.age_panel.add(label)
        self.age_panel.add(self.age)
        self.tools_panel.add(self.age_panel)


        save_button = Button(self.tools_panel, text = "Save annotations", command = save_annotation_cmd)
        self.tools_panel.add(save_button)

        # LAYOUT
        self.visualize_button.grid(column=0, row=0)
        self.path_label.grid(column=0, row=1)
        self.image.grid(column=0, row=2)
        #
        self.image.grid(column=0, row=2)
        #self.image_panel.grid(column=0, row=2)
        #   => LAYOUT TOOLS PANEL
        self.tools_panel.grid(column=1, row=2)
    
    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes = [
            ("Json files", ".json")])
        self.stop_current_vid = True
        if len(file_path) > 0:
            self.image.image = ""
            self.path_label.configure(text = file_path)
        else:
            self.image.image = ""
            self.path_label.configure(text = LABEL_EMPTY_PATH)

    def play_images_seq(self):     
        self.stop_current_vid = False   
        file_path = self.path_label.cget("text")
        if self.pause_image_flag == True:
            self.pause_image_flag = False
            self.image.after(200, self.visualize)
        else:
            if file_path != LABEL_EMPTY_PATH:
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
            genders={
                None:0,
                'M': 1,
                'F': 2,
            } 
            other_json = self.json_data['other']
            track_id_value = list(filter(lambda f: (f["track_id"] == self.person_selected_id), other_json))
            print(track_id_value)
            if track_id_value != []:
                gender = genders[track_id_value[0]['gender']]
                self.gender_selected.set(gender)
                self.age.delete(0,END)
                self.age.insert(0, str(track_id_value[0]['age_group']))
            else:
                self.gender_selected.set(0)
                self.age.delete(0,END)
                self.age.insert(0, "")
            
    

    def save_annotation(self):
        if self.person_selected_id != None and self.gender_selected.get() != 0:
            genders={
                0:None,
                1:'M',
                2:'F',
            } 
            gender = genders[self.gender_selected.get()]            
            age = int(self.age.get()) if self.age.get().isdigit() else None
            age = age if age != None and age >=1 and age <= 99 else None

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
            msgb.showinfo("Alert", "Please select a person, by clicking over it\nOr select a gender")

    def pause_images_seq(self):
        self.pause_image_flag = True

    def visualize(self):
        #update images left
        self.left_images_number -= 1
        if self.json_data != None and self.stop_current_vid != True:
            if self.left_images_number > 0:
                #print(self.left_images_number)
                index = len(self.json_data["images"]) - self.left_images_number - 1
                img = self.json_data["images"][index]
                if self.show_anotations:
                    img, current_annotations = ImageAnnotator.annotate_image(img, self.json_data)
                    self.current_annotations = current_annotations                
                    self.current_image_shape = img.shape
                else:
                    img = cv2.imread(img["file_name"])
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                #Resize
                img = imutils.resize(img, width=IMAGE_WIDTH, height=IMAGE_HEIGHT)
                im = Image.fromarray(img)            
                img = ImageTk.PhotoImage(image=im)
                self.image.create_image(0, 0, image=img, anchor=NW)
                self.image.image = img
                if self.pause_image_flag != True:                
                    self.image.after(33, self.visualize)

root = Tk()
my_gui = Gui(root)
root.mainloop()