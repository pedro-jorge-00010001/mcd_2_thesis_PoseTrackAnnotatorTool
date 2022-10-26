from msilib.schema import Icon
import tkinter as tk
from configparser import ConfigParser
from tkinter import messagebox
from views.generated.PathConfigurationGenerated import PathConfigurationGenerated

class PathConfigurationView(PathConfigurationGenerated):
    def __init__(self, master=None):
        super().__init__(master)
        self.init_gui_options()
        self.init_custom_events()

    def init_gui_options(self):
        #Show only json files for json path choser
        self.path_choser_json.config(filetypes = [("Json files", ".json")])
        #Show only mp4 files for mp4 path choser
        self.path_choser_mp4.config(filetypes = [("Mp4 files", ".mp4")])

        # load configurations
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.json_path.set(self.config['paths']['annotation_path'])
        self.video_path.set(self.config['paths']['video_path'])
        self.folder_path.set(self.config['paths']['folder_path'])

        #Set defaults selections
        if self.video_path.get() != "": 
            self.selected_type_of_import.set("mp4")
            self.path_choser_folder.configure(state="disabled")
        else:
            self.selected_type_of_import.set("folder")
            self.path_choser_mp4.configure(state="disabled")


    def init_custom_events(self):
        self.selected_type_of_import.trace_add('write', self.onRadioButtonChange)

    #Override PathConfigurationGenerated
    def load_paths(self):
        #Write configs
        self.config.set('paths', 'annotation_path', self.json_path.get())
        if self.selected_type_of_import.get() == "mp4":
            self.config.set('paths', 'video_path', self.video_path.get())
            self.config.set('paths', 'folder_path', "")
        else:
            self.config.set('paths', 'video_path', "")
            self.config.set('paths', 'folder_path', self.folder_path.get())

        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)
        messagebox.showinfo('Paths', 'The data is loaded', icon = messagebox.INFO)
        
    
    #EVENTS
    def onRadioButtonChange(self, *args):
        if self.selected_type_of_import.get() == "mp4":
            self.path_choser_mp4.configure(state = tk.NORMAL)
            self.path_choser_folder.configure(state = tk.DISABLED)
        else:
            self.path_choser_mp4.configure(state = tk.DISABLED)
            self.path_choser_folder.configure(state = tk.NORMAL)



