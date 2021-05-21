""" tk_ToolTip_class101.py
gives a Tkinter widget a tooltip as the mouse is above the widget
tested with Python27 and Python34  by  vegaseat  09sep2014
www.daniweb.com/programming/software-development/code/484591/a-tooltip-class-for-tkinter

Modified to include a delay time by Victor Zaccardo, 25mar16
"""

try:
    # for Python2
    import Tkinter as tk
except ImportError:
    # for Python3
    import tkinter as tk


class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()


"""
Top-Level menu with tooltips
Created by StackOverflow user stovfl
Available online at https://stackoverflow.com/questions/55316791/how-can-i-add-a-tooltip-to-menu-item

It doesn't seem to work...
"""


class MenuTooltip(tk.Menu):
    def __init__(self, parent):
        """
        :param parent: The parent of this Menu, either 'root' or 'Menubar'
         .tooltip == List of tuple (yposition, text)
         .tooltip_active == Index (0-based) of the active shown Tooltip
         Bind events <Leave>, <Motion>
        """
        super().__init__(parent, tearoff=0)
        self.tooltip = []
        self.tooltip_active = None

        self.bind('<Leave>', self.leave)
        self.bind('<Motion>', self.on_motion)

    def add_command(self, *cnf, **kwargs):
        tooltip = kwargs.get('tooltip')
        if tooltip:
            del kwargs['tooltip']
        super().add_command(*cnf, **kwargs)
        self.add_tooltip(len(self.tooltip), tooltip)

    def add_tooltip(self, index, tooltip):
        """
        :param index: Index (0-based) of the Menu Item
        :param tooltip: Text to show as Tooltip
        :return: None
        """
        self.tooltip.append((self.yposition(index) + 2, tooltip))

    def on_motion(self, event):
        """
        Loop .tooltip to find matching Menu Item
        """
        for idx in range(len(self.tooltip) - 1, -1, -1):
            if event.y >= self.tooltip[idx][0]:
                self.show_tooltip(idx)
                break

    def leave(self, event):
        """
        On leave, destroy the Tooltip and reset .tooltip_active to None
        """
        if not self.tooltip_active is None:
            print('leave()'.format())
            # destroy(<tooltip_active>)
            self.tooltip_active = None

    def show_tooltip(self, idx):
        """
        Show the Tooltip if not already shown, destroy the active Tooltip
        :param idx: Index of the Tooltip to show
        :return: None
        """
        if self.tooltip_active != idx:
            # destroy(<tooltip_active>)
            self.tooltip_active = idx
            print('{}'.format(self.tooltip[idx][1]))
