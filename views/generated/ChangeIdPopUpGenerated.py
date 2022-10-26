#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk


class ChangeIdPopUpGenerated:
    def __init__(self, master=None, translator=None):
        _ = translator
        if translator is None:
            _ = lambda x: x
        # build ui
        self.master = tk.Tk() if master is None else tk.Toplevel(master)
        self.master.configure(height=200, width=200)
        self.master.resizable(False, False)
        self.frame1 = tk.Frame(self.master)
        self.frame1.configure(height=200, width=200)
        self.label1 = tk.Label(self.frame1)
        self.label1.configure(relief="flat", text=_("New id"))
        self.label1.pack(side="top")
        self.entry_object = ttk.Entry(self.frame1)
        self.entry_object.configure(exportselection="true")
        self.entry_object.pack(side="top")
        self.frame1.pack(pady=10, side="top")
        self.frame2 = tk.Frame(self.master)
        self.frame2.configure(height=200, width=200)
        self.button3 = ttk.Button(self.frame2)
        self.button3.configure(text=_("Previous frames (<<)"))
        self.button3.pack(side="left")
        self.button3.configure(command=self.click_button_p)
        self.button4 = ttk.Button(self.frame2)
        self.button4.configure(text=_("Next frames (>>)"))
        self.button4.pack(side="left")
        self.button4.configure(command=self.click_button_n)
        self.frame2.pack(fill="x", padx=10, side="top")
        self.frame3 = tk.Frame(self.master)
        self.frame3.configure(height=200, width=200)
        self.button1 = ttk.Button(self.frame3)
        self.button1.configure(text=_("Current frame ( - )     "))
        self.button1.pack(fill="x", side="left")
        self.button1.configure(command=self.click_button_c)
        self.button5 = ttk.Button(self.frame3)
        self.button5.configure(text=_("All frames (<>)   "))
        self.button5.pack(fill="x", side="right")
        self.button5.configure(command=self.click_button_a)
        self.frame3.pack(fill="x", padx=10, pady=5, side="top")

        # Main widget
        self.mainwindow = self.master

    def run(self):
        self.mainwindow.mainloop()

    def click_button_p(self):
        pass

    def click_button_n(self):
        pass

    def click_button_c(self):
        pass

    def click_button_a(self):
        pass


if __name__ == "__main__":
    app = ChangeIdPopUpGenerated()
    app.run()

