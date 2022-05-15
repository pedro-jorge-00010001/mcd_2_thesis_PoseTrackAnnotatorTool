from tkinter import *

class ImageView(Frame):

    def __init__(self, parent, container):
        super().__init__(container)
        #regist event in parent
        remove_annotation_event = container.register(self._remove_annotation_event)
        
        #attributes
        self._parent = parent
        self._current_image_shape = (0,0,0)
        self._image_witdh = 1400
        self._image_height = 790
        self._current_annotations = None

        #build frame
        self._image = Canvas(container, width = self.image_witdh, height=self.image_height)
        self._image_rclick_menu = Menu(container, tearoff=False)
        self._image_rclick_menu.add_command(label="Remove annotation", command=remove_annotation_event)
        self._image.bind("<Button 1>", self._image_lclick_event)
        self._image.bind("<ButtonPress-3>", self._image_rclick_event)
        

    
    @property
    def image_witdh(self):
        return self._image_witdh
    @property
    def image_height(self):
        return self._image_height
    
    def grid(self, column, row ):
        self._image.grid(column = column, row = row)

    def show_image(self, img, current_annotations, image_shape = (0,0,0)):
        self._current_image_shape = image_shape
        self._current_annotations = current_annotations
        self._image.create_image(0, 0, image=img, anchor=NW)
        self._image.image = img
    

    #Events
    def _image_rclick_event(self, event):
        self._point_rclick = (event.x, event.y)
        self._image_rclick_menu.tk_popup(event.x_root,event.y_root)
    
    def _remove_annotation_event(self):
        if self._current_annotations is not None and len(self._current_annotations) and self._point_rclick is not None:
            xP,yP = self._point_rclick
            person_selected_id = self._get_selected_person_id(xP,yP)
            self._parent.remove_person_from_json(person_selected_id)
            print("remove " + str(person_selected_id))  
    
    def _image_lclick_event(self, event):
        if self._current_annotations is not None and len(self._current_annotations):
            #Point
            xP = event.x
            yP = event.y
            person_selected_id = self._get_selected_person_id(xP,yP)
            self._parent.change_person_selected_label(person_selected_id)
    
   

    #Other methods
    def _get_selected_person_id(self,xP,yP):
        
        #Multipliers to get the current rectangle for the resized image
        x_multiplier = self.image_witdh/self._current_image_shape[1]
        y_multiplier = self.image_height/self._current_image_shape[0]
        
        def is_point_inside_box(box_points, point):
            #bbox
            x1 = int(box_points[0]*x_multiplier)
            y1 = int(box_points[1]*y_multiplier)
            x2 = x1 + int(box_points[2]*x_multiplier)
            y2 = y1 + int(box_points[3]*y_multiplier)   
            
            #point
            xP, yP = point                          
            if (x1 < xP and xP < x2):
                if (y1 < yP and yP < y2):
                    return True
            return False
        
        person_selected_id = None
        #head box
        for current_annotation in self._current_annotations:
            try:
                box_points = current_annotation["bbox_head"]
                if is_point_inside_box(box_points, [xP,yP]):
                    person_selected_id = current_annotation["track_id"]                   
                    break
            except:
                pass

        if person_selected_id == None:
            #body box
            for current_annotation in self._current_annotations:
                try:
                    box_points = current_annotation["bbox"]
                    if is_point_inside_box(box_points, [xP,yP]):
                        person_selected_id = current_annotation["track_id"]                   
                        break
                except:
                    pass
        return person_selected_id

    