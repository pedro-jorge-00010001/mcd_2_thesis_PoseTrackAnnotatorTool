from tkinter import *
from ttkwidgets import TimeLine
from tkinter import colorchooser
from tkinter import messagebox

class TimelineView(Frame):

    def __init__(self, parent, container):
        super().__init__(container)
        add_action_event = container.register(self.add_action_event)

        #attributes
        self._parent = parent
        self._left_images_number = 0
        #build frame
        self.timeline = TimeLine(
            master = container
        )
        self.timeline.draw_timeline()
        # Right click menu
        self.timeline._canvas_categories.bind_all()
        self.timeline_menu = Menu(self.master, tearoff=False)
        self.timeline_menu.add_command(label="Add action", command=add_action_event)

    def grid(self, column, row ):
        self.timeline.grid(row=row)

    #Events
    def add_action_event(self):
        try:
            frame_number = float(TimeLine.get_time_string(self.timeline.time, self.timeline._unit))
        except:
             frame_number = 0
        self.timeline.tag_configure(self.get_number_to_string(self.action_id_selection), hover_border=2)   
        # r,g,b = (round(random.random()*255), round(random.random()*255), round(random.random()*255)) 
        # hex = rgb2hex(r,g,b)
        self.timeline.create_marker(self.get_number_to_string(self.action_id_selection), frame_number, frame_number+2,
            tags=(self.get_number_to_string(self.action_id_selection),), text="nothing", background= "#5fedce" ,border = 1)

    
    def timeline_rclick_event(self, event):
        def get_number_from_phrase(text):
            vector = text.split("-")
            if len(vector) > 1:
                return int(vector[1])
            return 0
        value_at_index = list(self.timeline._categories.values())[event.y//20]
        self.action_id_selection = get_number_from_phrase(value_at_index["text"])
        self.timeline_menu.tk_popup(event.x_root,event.y_root )
    
    def move_time_pointer_event(self, event):
        # stop video when moving the pointer
        self.pause_image_flag = True
        # get time pointer number
        frame_number = round(float(self.timeline._time_label.cget("text")))
        # update images left
        self.left_images_number = self._left_images_number - frame_number -1
        self._parent.set_image(frame_number)

    
    def double_click_event(self, event):
        def click_cancel():
            self.timeline.update_marker(iid, background=tag_brackground)
            pop.destroy()

        def click_ok():
            start = float(round(float(start_label.get())))
            finish = float(round(float(end_label.get())))
            if start != finish:
                self.timeline.update_marker(iid,text = name_label.get(), 
                    start = start, finish = finish, 
                    background = button_color.cget('bg'))
                pop.destroy()
            else:
                 messagebox.showwarning(title="Action with wrong info", message="The start frame of an action can't be equal or less than to the end frame")

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
        pop.geometry("%dx%d+%d+%d" % (240, 110, event.x_root, event.y_root))
        pop.tkraise(self.timeline)
        pop.wm_resizable(False,False)
        
        # Edit name
        Label(pop, text="Edit name").grid(row=0, column=0)
        name_label = StringVar(pop)
        name_label.set(selected_tag['text'])
        Entry(pop, textvariable = name_label, width=20).grid(row=0, column=1)

        # Edit frames lenght
        Label(pop, text="Start frame").grid(row=1, column=0)
        start_label = StringVar(pop)
        start_label.set(str(int(float(selected_tag['start']))))
        Entry(pop, textvariable = start_label, width=20).grid(row=1, column=1)

        Label(pop, text="End frame").grid(row=2, column=0)
        end_label = StringVar(pop)
        end_label.set(str(int(round(float(selected_tag['finish'])))))
        Entry(pop, textvariable = end_label, width=20).grid(row=2, column=1)
        
        # Edit color
        label_color = Label(pop, text="Color:")
        label_color.grid(row=3, column=0, sticky='nesw')

        #Buttons
        button_color = Button(pop, text = "", command= pick_color,bg=tag_brackground, bd=0)
        button_color.grid(row=3, column=1,sticky='nesw')
        button_ok = Button(pop, text="Ok", command = click_ok, bd=1)
        button_ok.grid(row=4, column=0,sticky='nesw')

        button_remove = Button(pop, text="Remove", command = delete_marker, bd=1)
        button_remove.grid(row=4, column=1,sticky='nesw')
        
        button_cancel = Button(pop, text="Cancel", command= click_cancel, bd=1)
        button_cancel.grid(row=4, column=2,sticky='nesw')


    #Other methods

    def update_timeline(self,left_images_number, annotations_track_ids):
        self.timeline.destroy()
        self._left_images_number = left_images_number
        self.timeline.__init__(master = self._parent.master, 
            height=100, width = 1300, 
            extend=True,  zoom_enabled = False, 
            start = 0.0, 
            resolution= 0.022, tick_resolution = 1.0,
            unit = 's',
            categories={self.get_number_to_string(key):{"text": "Person-{}".format(key)} for key in annotations_track_ids},
            finish = float(left_images_number-1), snap_margin = 2
        )
        
        self.timeline.draw_timeline()   
        self.timeline._canvas_ticks.bind("<ButtonRelease-1>", self.move_time_pointer_event)
        self.timeline._timeline.bind("<ButtonPress-3>", self.timeline_rclick_event)
        self.timeline.grid(row=2)
        self.timeline._timeline.bind("<Double-Button-1>", self.double_click_event)

    def load_data(self, actions):
        if actions is not None and len(actions):
            for action in actions:
                self.timeline.tag_configure(self.get_number_to_string(action["track_id"]), hover_border=2)   
                self.timeline.create_marker(self.get_number_to_string(action["track_id"]), action["start_frame"], action["finish_frame"],
                        tags=(self.get_number_to_string(action["track_id"]),), text = action["action_name"], background= action["color"] ,border = 1)
    
    def set_time(self, time):
        self.timeline.set_time(float(time))
        try:
            self.timeline._time_label['text'] = str(time)
        except: 
            pass
    
    def get_markers(self):
        return self.timeline.markers

    def get_number_to_string(self, number):
        if int(number) < 10:
            return '00' + str(number)
        elif int(number) < 100:
            return '0' + str(number)
        return str(number)

    
    