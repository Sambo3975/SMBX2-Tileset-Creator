from tkinter import *
from tkinter import ttk, colorchooser
from tooltip import CreateToolTip


class ColorSelector(ttk.Frame):
    """Color Selector widget"""
    def __change_color(self, *args):
        color_code = colorchooser.askcolor(title='Select Color')
        if color_code is not None:  # user selected a color and did not hit Cancel
            self.__color_preview.configure(background=color_code[1])
            self.value.set(color_code[1])

    def __init__(self, master=None, *, text=None, tooltip=None, variable=None, color='white', **kw):
        super().__init__(master, **kw)

        self.value = variable or StringVar(None, color)
        self.__color_preview = Frame(self, borderwidth=2, relief='sunken', width=23, height=23,
                                     background=color)
        self.__color_preview.grid(column=1, row=1)
        if text is None:
            text = 'Select Color'
        self.__color_button = ttk.Button(self, text=text, command=self.__change_color)
        self.__color_button.grid(column=2, row=1)
        if tooltip is not None:
            self.__tooltip = CreateToolTip(self.__color_button, tooltip)


if __name__ == '__main__':
    current_row = 0


    def next_row(x=None):
        global current_row
        if x is not None:
            current_row = x
        else:
            current_row += 1
        return current_row


    data_default = {
        'color': 'red'
    }

    data = {}
    window = Tk()
    window.title('Test')
    window.resizable(False, False)
    window.columnconfigure(0, weight=1)
    window.rowconfigure(0, weight=1)
    for k in data_default.keys():
        v = data_default[k]
        if isinstance(v, str):
            data[k] = StringVar(None, v)
        else:
            raise ValueError('not a string?')

    window.mainframe = ttk.Frame(window, padding='3 3 12 12')
    window.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

    ttk.Label(text='Color Chooser:').grid(column=1, row=next_row())
    color_selector = ColorSelector(window, color='red', tooltip='Pick a color', variable=data['color'])
    color_selector.grid(column=1, row=next_row())

    window.mainloop()
