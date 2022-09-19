#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk
from pygubu.widgets.pathchooserinput import PathChooserInput


class PathConfigurationGenerated(tk.Toplevel):
    def __init__(self, master=None, **kw):
        super(PathConfigurationGenerated, self).__init__(master, **kw)
        self.frame1 = ttk.Frame(self)
        self.frame1.configure(height=200, padding=30, width=400)
        self.frame2 = ttk.Frame(self.frame1)
        self.frame2.configure(height=200, width=400)
        self.label1 = ttk.Label(self.frame2)
        self.label1.configure(text="Annotations (Json)   ")
        self.label1.pack(side="left")
        self.path_choser_json = PathChooserInput(self.frame2)
        self.json_path = tk.StringVar()
        self.path_choser_json.configure(
            textvariable=self.json_path, title="Select json", type="file"
        )
        self.path_choser_json.pack(expand="true", fill="x", side="right")
        self.frame2.pack(expand="true", fill="x", ipady=5, side="top")
        self.frame3 = ttk.Frame(self.frame1)
        self.frame3.configure(height=200, width=200)
        self.label2 = ttk.Label(self.frame3)
        self.label2.configure(text="Video (Ex. MP4)        ")
        self.label2.pack(anchor="s", side="left")
        self.path_choser_mp4 = PathChooserInput(self.frame3)
        self.video_path = tk.StringVar()
        self.path_choser_mp4.configure(textvariable=self.video_path, type="file")
        self.path_choser_mp4.pack(anchor="s", expand="true", fill="x", side="left")
        self.radio_button_mp4 = ttk.Radiobutton(self.frame3)
        self.selected_type_of_import = tk.StringVar(value="mp4")
        self.radio_button_mp4.configure(
            value="mp4", variable=self.selected_type_of_import
        )
        self.radio_button_mp4.pack(anchor="s", side="right")
        self.frame3.pack(expand="true", fill="x", ipadx=10, side="top")
        self.frame4 = ttk.Frame(self.frame1)
        self.frame4.configure(height=200, width=400)
        self.label3 = ttk.Label(self.frame4)
        self.label3.configure(text="Folder with images  ")
        self.label3.pack(anchor="s", side="left")
        self.path_choser_folder = PathChooserInput(self.frame4)
        self.folder_path = tk.StringVar()
        self.path_choser_folder.configure(
            textvariable=self.folder_path, type="directory"
        )
        self.path_choser_folder.pack(anchor="s", expand="true", fill="x", side="left")
        self.radio_button_folder = ttk.Radiobutton(self.frame4)
        self.radio_button_folder.configure(
            value="folder", variable=self.selected_type_of_import
        )
        self.radio_button_folder.pack(anchor="s", side="right")
        self.frame4.pack(expand="true", fill="x", ipadx=10, ipady=5, side="top")
        self.load_button = ttk.Button(self.frame1)
        self.load_button.configure(text="Load")
        self.load_button.pack(pady=10, side="top")
        self.load_button.configure(command=self.load_paths)
        self.frame1.pack(expand="true", fill="x", side="top")
        self.configure(height=200, width=200)
        self.geometry("1000x320")

    def load_paths(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    widget = PathConfigurationGenerated(root)
    widget.pack(expand=True, fill="both")
    root.mainloop()

