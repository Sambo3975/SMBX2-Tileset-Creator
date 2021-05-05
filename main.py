"""
SMBX2 Tileset Creator
---------------------------------
This program streamlines the creation of tilesets in SMBX2 by automating the most tedious parts of the process:
- Cutting the image with all your tiles into individual block-*.png images.
- Finding IDs for all the images
- Creating the .tileset.ini file in PGE.**

This program was designed for Windows and may not work right on other platforms. I figured this would be fine since
SMBX doesn't run on anything but Windows (or Wine) anyway.

** Some manual rearrangement will likely be necessary for tilesets with blocks not all the same size.

Created by Sambo
"""

from tkinter import *
from tkinter import ttk, colorchooser, filedialog

current_row = 0


def next_row(x=None):
    global current_row
    if x is not None:
        current_row = x
    else:
        current_row += 1
    return current_row


# ----------------------------
# Button functions
# ----------------------------


def file_open(*args):
    filename = filedialog.askopenfilename(filetypes=(('PNG files', '*.png'), ("All files", "*.*")))
    if len(filename) > 0:
        pass


def file_save(*args):
    print('save')


def file_export(*args):
    print('export')


def file_close(*args):
    print('close')


def change_highlight_color():
    color_code = colorchooser.askcolor(title='Choose Color')
    if color_code is not None:
        color_code = color_code[1]
        window.highlight_color.set(color_code)
        window.color_preview['background'] = color_code


# ----------------------------
# Main Window
# ----------------------------


class Window(Tk):
    def __init__(self):
        super().__init__()

        self.title("SMBX2 Tileset Creator")
        self.iconbitmap('data/icon.ico')
        self.resizable(False, False)

        self.mainframe = ttk.Frame(self, padding="3 3 12 12")      # cover the root with a frame that has a modern style
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))  # placed directly in application window
        self.columnconfigure(0, weight=1)                     # fill the whole window vertically, even when resized
        self.rowconfigure(0, weight=1)                        # same horizontally

        self.option_add('*tearOff', FALSE)

        # ------------------------------------------
        # Top-level Menus
        # ------------------------------------------

        self.menu_bar = Menu(self)
        self['menu'] = self.menu_bar

        # File Menu
        self.menu_file = Menu(self.menu_bar)
        self.menu_bar.add_cascade(menu=self.menu_file, label='File')
        self.menu_file.add_command(label='Open...', command=file_open, accelerator='Ctrl+O')
        self.menu_file.add_command(label='Save', command=file_save, accelerator='Ctrl+S')
        self.menu_file.add_command(label='Export...', command=file_export, accelerator='Ctrl+E')
        self.menu_file.add_command(label='Close', command=file_close, accelerator='Ctrl+W')

        # ------------------------------------------
        # Hotkeys
        # ------------------------------------------

        self.bind_all('<Control-o>', file_open)
        self.bind_all('<Control-s>', file_save)
        self.bind_all('<Control-e>', file_export)
        self.bind_all('<Control-w>', file_close)

        # ------------------------------------------
        # Tileset configuration Frame
        # ------------------------------------------

        self.config_frame = ttk.Frame(self.mainframe)
        self.config_frame.grid(column=1, row=1, sticky=N)  # placed directly in application window

        # View Section

        self.view_box = ttk.LabelFrame(self.config_frame, text='View', padding='3 3 12 8')
        self.view_box.grid(column=1, row=1, sticky=(W, E))

        self.highlight_color = StringVar(None, '#ff8040')
        ttk.Label(self.view_box, text='Highlight Color:').grid(column=1, row=next_row(), sticky=W)
        self.color_selector = ttk.Frame(self.view_box)
        self.color_selector.grid(column=1, row=next_row(), sticky=(W, E), padx=2)
        self.color_preview = Frame(self.color_selector, borderwidth=2, relief='sunken', width=23, height=23,
                                   background=self.highlight_color.get())
        self.color_preview.grid(column=1, row=1, sticky=W)
        ttk.Button(self.color_selector, text='Select Color', command=change_highlight_color)\
            .grid(column=2, row=1, sticky=W)

        self.grid_size = StringVar(None, "16")  # default: 16
        ttk.Label(self.view_box, text='Grid Size:').grid(column=1, row=next_row(), sticky=W, padx=0)
        ttk.Combobox(self.view_box, textvariable=self.grid_size, values=('8', '16', '32'), width=6) \
            .grid(column=1, row=next_row(), sticky=W)

        self.grid_show = BooleanVar(None, True)
        ttk.Checkbutton(self.view_box, text='Show Grid', variable=self.grid_show, offvalue=False, onvalue=True) \
            .grid(column=1, row=next_row(), sticky=W)

        self.show_block_types = BooleanVar(None, True)
        ttk.Checkbutton(self.view_box, text='Show Block Types', variable=self.show_block_types, offvalue=False,
                        onvalue=True).grid(column=1, row=next_row(), sticky=W)

        # Export Settings Section

        self.export_box = ttk.LabelFrame(self.config_frame, text='Export Settings', padding='3 3 12 8')
        self.export_box.grid(column=1, row=2, sticky=(W, E))

        self.pixel_scale = StringVar(None, "2")
        ttk.Label(self.export_box, text='Pixel Scale:').grid(column=1, row=next_row(1), sticky=W)
        ttk.Combobox(self.export_box, textvariable=self.pixel_scale, values=('1', '2', '4'), width=6)\
            .grid(column=1, row=next_row(), sticky=W)

        self.block_ids = StringVar(None, "Replace Existing")
        ttk.Label(self.export_box, text='Block IDs:').grid(column=1, row=next_row(), sticky=W)
        ttk.Combobox(self.export_box, textvariable=self.block_ids,
                     values=('Replace Existing', 'User Slots (751-1000)'),
                     width=16).grid(column=1, row=next_row(), sticky=W)

        self.create_pge_tileset = BooleanVar(None, True)
        ttk.Checkbutton(self.export_box, text='Create PGE Tileset', variable=self.create_pge_tileset,
                        offvalue=False, onvalue=True).grid(column=1, row=next_row(), sticky=W)

        # ------------------------------------------
        # Tileset View
        # ------------------------------------------

        self.tileset_frame = ttk.Frame(self.mainframe, width=400, height=300)
        self.tileset_frame.grid(column=2, row=1, sticky=N)

        self.launch_frame = ttk.Frame(self.tileset_frame)
        self.launch_frame.place(in_=self.tileset_frame, anchor='c', relx=.5, rely=.5)
        ttk.Label(self.launch_frame, text='No tileset image currently loaded.', padding='0 0 4 4')\
            .grid(column=1, row=next_row(1))
        ttk.Button(self.launch_frame, text='Open Image', command=file_open).grid(column=1, row=next_row())

        # ------------------------------------------
        # Tile Frame
        # ------------------------------------------

        self.tile_frame = ttk.Frame(self.mainframe)
        self.tile_frame.grid(column=3, row=1, sticky=N)

        # Tile Settings

        self.tile_box = ttk.LabelFrame(self.tile_frame, text='Block Settings', padding='3 3 12 8')
        self.tile_box.grid(column=1, row=1, sticky=N)

        self.collision_type = StringVar(None, "Solid")
        ttk.Label(self.tile_box, text='Collision Type:').grid(column=1, row=next_row(1), sticky=W)
        ttk.Combobox(self.tile_box, state='readonly', textvariable=self.collision_type, width=12, values=(
            "Solid", "Semisolid", "Passthrough", "Slope ◢", "Slope ◣", "Slope ◥", "Slope ◤"
        )).grid(column=1, row=next_row(), sticky=W)

        self.harm_type = StringVar(None, "Harmless")
        ttk.Label(self.tile_box, text='Harm Type:').grid(column=1, row=next_row(), sticky=W)
        ttk.Combobox(self.tile_box, state='readonly', textvariable=self.harm_type, width=12, values=(
            "Harmless", "Hurt Player", "Lava"
        )).grid(column=1, row=next_row(), sticky=W)

        self.animation_frames = StringVar(None, '1')
        ttk.Label(self.tile_box, text='Animation Frames:').grid(column=1, row=next_row(), sticky=W)
        ttk.Spinbox(self.tile_box, from_=1, to=100, textvariable=self.animation_frames, width=6) \
            .grid(column=1, row=next_row(), sticky=W)

        self.contents = StringVar(None, '0')
        ttk.Label(self.tile_box, text='Default Contents:').grid(column=1, row=next_row(), sticky=W)
        ttk.Spinbox(self.tile_box, from_=-99, to=674, textvariable=self.contents, width=6) \
            .grid(column=1, row=next_row(), sticky=W)

        self.sizable = BooleanVar(None, False)
        ttk.Checkbutton(self.tile_box, text='Sizable', variable=self.sizable, offvalue=False, onvalue=True)\
            .grid(column=1, row=next_row(), sticky=W)

        # Tile Preview

        self.preview_box = ttk.LabelFrame(self.tile_frame, text='Preview', padding='3 3 12 8')
        self.preview_box.grid(column=1, row=2, sticky=(W, E))
        self.preview_box.rowconfigure(0, weight=1)
        self.preview_box.columnconfigure(0, weight=1)

        self.preview = Frame(self.preview_box, background='#ff8040', width=32, height=32)
        self.preview.grid(column=0, row=0, sticky="")

        # Add some padding to all children
        for child in self.mainframe.winfo_children():
            try:
                child.grid_configure(padx=5, pady=5)
            except TclError:
                pass


if __name__ == '__main__':
    window = Window()
    window.mainloop()
