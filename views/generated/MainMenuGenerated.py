#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk


class MainMenuGenerated:
    def __init__(self, master=None):
        # build ui
        self.master = tk.Tk() if master is None else tk.Toplevel(master)
        self.master.configure(height=200, width=200)
        self.master.geometry("1550x960")
        self.frame10 = tk.Frame(self.master)
        self.frame10.configure(height=200, width=200)
        self.timeline_view = ttk.Frame(self.frame10)
        self.timeline_view.configure(height=200, width=200)
        self.timeline_view.pack(expand="false", fill="both", side="bottom")
        self.notebook4 = ttk.Notebook(self.frame10)
        self.notebook4.configure(height=200, width=200)
        self.image_view = ttk.Frame(self.notebook4)
        self.image_view.configure(height=200, width=200)
        self.image_view.pack(expand="true", fill="both", side="top")
        self.notebook4.add(self.image_view, text="Video")
        self.frame2 = ttk.Frame(self.notebook4)
        self.frame2.configure(height=200, width=200)
        self.frame2.pack(side="top")
        self.notebook4.add(self.frame2, text="Data")
        self.notebook4.pack(expand="true", fill="both", side="top")
        self.frame10.pack(expand="true", fill="both", side="left")
        self.frame1 = ttk.Frame(self.master)
        self.frame1.configure(height=200, width=200)
        self.play_button = ttk.Button(self.frame1)
        self.play_button.configure(text="Play")
        self.play_button.pack(side="top")
        self.play_button.configure(command=self.play_event)
        self.stop_button = ttk.Button(self.frame1)
        self.stop_button.configure(text="Pause")
        self.stop_button.pack(side="top")
        self.stop_button.configure(command=self.pause_event)
        self.hide_button = ttk.Button(self.frame1)
        self.hide_button.configure(text="Hide/Show")
        self.hide_button.pack(side="top")
        self.hide_button.configure(command=self.hide_event)
        self.slicer_button = ttk.Scale(self.frame1)
        self.slicer_value = tk.IntVar()
        self.slicer_button.configure(
            cursor="hand2",
            from_=550,
            orient="horizontal",
            to=1000,
            variable=self.slicer_value,
        )
        self.slicer_button.pack(side="top")
        self.person_id_label = ttk.Label(self.frame1)
        self.person_selected_id = tk.IntVar()
        self.person_id_label.configure(
            font="{Consolas} 16 {bold}",
            justify="left",
            textvariable=self.person_selected_id,
        )
        self.person_id_label.pack(side="top")
        self.gender_label = ttk.Label(self.frame1)
        self.gender_label.configure(text="Gender")
        self.gender_label.pack(side="top")
        self.gender_combobox = ttk.Combobox(self.frame1)
        self.gender_selected = tk.StringVar()
        self.gender_combobox.configure(
            state="readonly", textvariable=self.gender_selected, values="m f", width=5
        )
        self.gender_combobox.pack(pady=5, side="top")
        self.age_group_label = ttk.Label(self.frame1)
        self.age_group_label.configure(text="Age-group")
        self.age_group_label.pack(side="top")
        self.age_group_combobox = ttk.Combobox(self.frame1)
        self.age_group_selected = tk.StringVar()
        self.age_group_combobox.configure(
            state="readonly",
            textvariable=self.age_group_selected,
            values="00-14(Child) 15-24(Young) 25-64(Adult) 65+(Senior)",
            width=15,
        )
        self.age_group_combobox.pack(pady=5, side="top")
        self.save_button = ttk.Button(self.frame1)
        self.save_button.configure(text="Save")
        self.save_button.pack(padx=5, side="top")
        self.save_button.configure(command=self.save_event)
        self.frame1.pack(side="right")

        # Main widget
        self.mainwindow = self.master
        # Main menu
        _main_menu = self.create_menu(self.mainwindow)
        self.mainwindow.configure(menu=_main_menu)

    def run(self):
        self.mainwindow.mainloop()

    def create_menu(self, master):
        self.menu = tk.Menu(master)
        self.menu.configure(relief="flat", tearoff="false")
        self.file_menu = tk.Menu(
            self.menu, relief="flat", takefocus=False, tearoff="false"
        )
        self.menu.add(
            tk.CASCADE,
            menu=self.file_menu,
            columnbreak="false",
            hidemargin="false",
            label="File",
        )
        self.file_menu.add(
            "command",
            command=self.open_path_configuration,
            label="Configure annotation paths",
        )
        self.file_menu.add("command", command=self.exit_event, label="Exit")
        return self.menu

    def play_event(self):
        pass

    def pause_event(self):
        pass

    def hide_event(self):
        pass

    def save_event(self):
        pass

    def open_path_configuration(self):
        pass

    def exit_event(self):
        pass


if __name__ == "__main__":
    app = MainMenuGenerated()
    app.run()

