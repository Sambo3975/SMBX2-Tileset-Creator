from tkinter import *
from tkinter import ttk, colorchooser

import regex

from tooltip import CreateToolTip


class ColorSelector(ttk.Frame):
    """Color Selector widget"""
    def configure(self, cnf=None, **kw):
        if 'state' in kw:
            self.__color_button['state'] = kw['state']
            del kw['state']
        super(ColorSelector, self).configure(**kw)
    
    def __change_color(self, *args):
        color_code = colorchooser.askcolor(title='Select Color')
        if color_code[1] is not None:  # user selected a color and did not hit Cancel
            self.__color_preview.configure(background=color_code[1])
            self.value.set(color_code[1])

    def load_color_data(self, *args):
        self.__color_preview.configure(background=self.value.get())

    def __init__(self, master=None, *, text=None, tooltip=None, variable=None, color='white', **kw):
        super().__init__(master, **kw)

        self.value = variable or StringVar(None, color)
        self.value.trace_add('write', self.load_color_data)
        self.__color_preview = Frame(self, borderwidth=2, relief='sunken', width=23, height=23,
                                     background=color)
        self.__color_preview.grid(column=1, row=1)
        if text is None:
            text = 'Select Color'
        self.__color_button = ttk.Button(self, text=text, command=self.__change_color)
        self.__color_button.grid(column=2, row=1)
        if tooltip is not None:
            self.__tooltip = CreateToolTip(self.__color_button, tooltip)


def update_good_input(valid, old_good_input, new_good_input):
    # not valid (so the value will not change) and previous value was good OR the new value is good
    return (not valid and old_good_input) or new_good_input


class VerifiedWidget(ttk.Frame):
    """A widget with built-in verification"""

    @staticmethod
    def _isint(value):
        return regex.search(r'^-?\d*$', value) is not None

    @staticmethod
    def _default_verify_function(value):
        return value == '' or VerifiedWidget._isint(value)

    def _default_good_function(self, value):
        if value in ('', '-'):
            return False
        value = int(value)
        if self.min_val is not None and self.max_val is not None:
            return self.min_val <= value <= self.max_val
        elif self.min_val is not None:
            return value >= self.min_val
        elif self.max_val is not None:
            return value <= self.max_val
        else:
            return True

    def _verify_input(self, value):
        valid = self.verify_function(value)

        # The value was previously good and will not be changed, or it was changed to a good value.
        good_input = (not valid and self.good_input) or (valid and self.good_function(value))
        if good_input and not self.good_input:
            if self.good_value_callback is not None:
                self.good_value_callback()
            self.warning_label.lower()
        elif not good_input and self.good_input:
            if self.bad_value_callback is not None:
                self.bad_value_callback()
            self.warning_label.lift()
        self.good_input = good_input
        if self.last_good_variable is not None and valid and good_input:
            if value != self.last_good_variable.get():
                self.last_good_variable.set(value)

        if not valid:
            self.bell()
        return valid

    def _verify_spinbox_on_scroll(self, *args):
        self._verify_input(self.widget.get())

    def check_variable(self):
        self._verify_input(self.widget.get())

    def configure(self, cnf=None, **kw):
        if 'state' in kw:
            for x in self.winfo_children():
                x['state'] = kw['state']

            if not self.good_input:
                if kw['state'] == DISABLED:
                    # Best not give the user a reason to worry when disabling a widget with a bad value
                    self.warning_label.lower()
                else:
                    self.warning_label.lift()
            del kw['state']
        if 'variable' in kw:
            variable = kw['variable']
            try:
                self.widget.configure(variable=variable)
            except TclError:
                self.widget.configure(textvariable=variable)
            self.variable = variable
            self.check_variable()
            del kw['variable']
        if 'bad_value_callback' in kw:
            self.bad_value_callback = kw['bad_value_callback']
            del kw['bad_value_callback']
        if 'good_value_callback' in kw:
            self.good_value_callback = kw['good_value_callback']
            del kw['good_value_callback']
        super(VerifiedWidget, self).configure(cnf, **kw)

    def __init__(self, widget_type, widget_args, master, *, orientation='horizontal', label_text='',
                 label_width=None, verify_function=None, good_function=None, min_val=None, max_val=None, variable=None,
                 warning_label='⚠', tooltip=None, last_good_variable=None, bad_value_callback=None,
                 good_value_callback=None, **kw):
        """
        CONSTRUCTOR
        :param widget: A ttk widget.
        :type widget: ttk.TCombobox | ttk.TSpinbox | ttk.TEntry
        :param master: This widget's master.
        :type master: ttk.Frame | ttk.LabelFrame
        :param orientation: The orientation of the widget in relation to its label. 'vertical' or 'horizontal'
        :type orientation: str
        :param label_text: The text that will appear on the widget's label.
        :param label_width: The width of the label in pixels. Used to align multiple VerifiedWidget objects.
        :param verify_function: The verify function. Takes one argument, which is the value the field will hold if the
        input is valid.
        :param min_val: The lowest value the widget will accept.
        :param max_val: The highest value the widget will accept.
        :param variable: The variable that this widget will affect
        :type variable: StringVar() | IntVar() | BooleanVar()
        :param warning_label: The string to display to the right of the widget on bad input. Bad input refers to a valid
        input that is not in the acceptable range, such as an integer that is less than the minimum value.
        :param last_good_variable: The variable that will store the last good value that was in the field. This
        variable can be used as a fallback if the widget has a bad value. Should only be used for fields that, when
        changed, have an effect that is immediately apparent to the user.
        :param bad_value_callback: The function to call when the widget's value becomes bad.
        :param good_value_callback: The function to call when the widget's value becomes good.
        :param kw: Additional arguments to pass to the Frame that will be constructed around the widget.
        """
        super().__init__(master, **kw)

        verify_reg = self.register(self._verify_input)

        # Lay out all the widgets

        self.label = ttk.Label(self, text=label_text)
        self.label.grid(column=1, row=1, sticky=(E, W))
        if label_width is not None:
            self.columnconfigure(1, minsize=label_width)

        self.widget = widget_type(self, **widget_args)
        try:
            self.widget.configure(variable=variable)
        except TclError:
            self.widget.configure(textvariable=variable)
        self.widget.configure(validate='all', validatecommand=(verify_reg, '%P'))
        if orientation == 'horizontal':
            self.label.grid(pady=4)
            widget_pos = (2, 1)
        else:
            widget_pos = (1, 2)
        self.widget.grid(column=widget_pos[0], row=widget_pos[1], sticky=W)
        if self.widget.winfo_class() == 'TSpinbox':
            self.widget.configure(command=self._verify_spinbox_on_scroll)
            if min_val is not None:
                self.widget.configure(from_=min_val)
            if max_val is not None:
                self.widget.configure(to=max_val)

        self.warning_label = ttk.Label(self, text=warning_label)
        self.warning_label.grid(column=widget_pos[0] + 1, row=widget_pos[1], sticky=W)

        self.warning_label_cover = ttk.Label(self, text='     ')
        # Cover up the warning label. It can be shown later with the lift() function
        self.warning_label_cover.grid(column=widget_pos[0] + 1, row=widget_pos[1], sticky=W)

        if tooltip is not None:
            CreateToolTip(self.widget, tooltip)

        # Set up other data
        self.min_val = min_val
        self.max_val = max_val
        self.good_input = True
        if good_function is not None:
            self.good_function = good_function
        else:
            self.good_function = self._default_good_function
        if verify_function is not None:
            self.verify_function = verify_function
        else:
            self.verify_function = self._default_verify_function
        if variable is not None:
            self.variable = variable
        else:
            self.variable = StringVar()
        self.last_good_variable = last_good_variable

        self.bad_value_callback = bad_value_callback
        self.good_value_callback = good_value_callback


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

    ttk.Label(window.mainframe, text='Color Chooser:').grid(column=1, row=next_row())
    color_selector = ColorSelector(window.mainframe, color='red', tooltip='Pick a color', variable=data['color'])
    color_selector.grid(column=1, row=next_row(), sticky=W)

    combobox = VerifiedWidget(ttk.Combobox, {'values': ('1', '2', '3'), 'width': 6}, window.mainframe,
                              label_text='Combobox:', label_width=80, min_val=1, max_val=3)
    combobox.grid(column=1, row=next_row(), sticky=W)

    spinbox = VerifiedWidget(ttk.Spinbox, {'width': 6}, window.mainframe, orientation='vertical',
                             label_text='Spinbox:', label_width=80, min_val=-10, max_val=10)
    spinbox.grid(column=1, row=next_row(), sticky=W)

    window.mainloop()
