from views.generated.ChangeIdPopUpGenerated import ChangeIdPopUpGenerated

class ChangeIdPopUp(ChangeIdPopUpGenerated):
    def __init__(self, master=None, parent = None, person_selected_id = None):
        self.person_selected_id = person_selected_id
        self._parent = parent
        super().__init__(master)
        

    def set_position(self, x_root, y_root):
        self.master.update()
        self.master.geometry("%dx%d+%d+%d" % (self.master.winfo_width(), self.master.winfo_height(), x_root, y_root))

    # Override ChangeIdPopUpGenerated
    def click_button_p(self):
        self.click_edit_button(self.entry_object.get(), "p")
        self.master.destroy()
    
    # Override ChangeIdPopUpGenerated
    def click_button_n(self):
        self.click_edit_button(self.entry_object.get(), "n")
        self.master.destroy()

    # Override ChangeIdPopUpGenerated
    def click_button_c(self):
        self.click_edit_button(self.entry_object.get(), "c")
        self.master.destroy()

    # Override ChangeIdPopUpGenerated
    def click_button_a(self):
        self.click_edit_button(self.entry_object.get(), "a")
        self.master.destroy()

    def click_edit_button(self, value, option):
        try :
            new_id = int(value)
            self._parent._parent.update_person_id_in_json(self.person_selected_id, new_id, option = option)
        except Exception as e: 
            print(f"Erro {e}")
            pass