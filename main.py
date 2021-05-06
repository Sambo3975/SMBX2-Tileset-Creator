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
from tooltip import CreateToolTip

data_defaults = {
    'view': {
        'grid_size':        '16',
        'show_grid':        True,
        'show_block_types': True,
        'highlight_color':  '#ff8040',
    },
    'export': {
        'pixel_scale': '2',
        'block_ids':          'Avoid Special',
        'bgo_ids':            'Avoid Special',
        'create_pge_tileset': True,
        'start_high':         False,
    },
    'tile:': {
        'animation': {
            'frames':     '1',
            'framespeed': '8',
        },
        'light': {
            'lightoffsetx':    '0',
            'lightoffsety':    '0',
            'lightradius':     '128',
            'lightbrightness': '1',
            'lightcolor':      '#ffffff',
            'lightflicker':    False,
        },
        'priority': -85,
        'behavior': {
            'content_type':   'empty',
            'content_id':     '0',

            'collision_type': 'Solid',

            'sizable':        False,
            'pswitchable':    False,
            'slippery':       False,
            'lava':           False,
            'bumpable':       False,
            'smashable':      '0',
        },
    },
}


current_row = 0


def next_row(x=None):
    global current_row
    if x is not None:
        current_row = x
    else:
        current_row += 1
    return current_row


def error_msg(msg):
    print(msg)


def redraw_tileset_selections(canvas):
    pass


def redraw_tileset_grid(canvas):
    pass


def redraw_tileset_image(canvas):
    canvas.configure()


def redraw_canvas():
    canvas = window.tileset_canvas
    canvas.delete('all')  # Clear
    redraw_tileset_image(canvas)
    redraw_tileset_grid(canvas)
    redraw_tileset_selections(canvas)


def save_prompt(action):
    """
    Prompts the user to save before completing an action. Offers Yes, No, or Cancel as options. Saves data if Yes is
    chosen.
    :arg action text describing the action to take
    :type action str
    :return True if the action should proceed; false otherwise
    """
    return True  # Would you like to save before {action}?


def file_verify(filename):
    return len(filename) > 0 and filename.lower().endswith('png')


def load_data(defaults=None, data_from_file=None):
    if defaults is None:
        defaults = data_defaults
    for k in defaults.keys():
        if data_from_file is not None and k in data_from_file:
            v = data_from_file[k]
        else:
            v = defaults[k]
        if isinstance(v, dict):
            load_data(defaults[k], data_from_file[k])
        elif isinstance(v, int):
            data_from_file[k] = IntVar(None, v)
        elif isinstance(v, bool):
            data_from_file[k] = BooleanVar(None, v)
        elif isinstance(v, str):
            data_from_file[k] = StringVar(None, v)
        else:
            raise ValueError(f'Invalid entry: {k}: {v}, ({type(v)})')

# ----------------------------
# Button functions
# ----------------------------


def file_open(*args):
    filename = filedialog.askopenfilename(filetypes=(('PNG files', '*.png'), ("All files", "*.*")))
    if file_verify(filename):

        try:
            if len(window.loaded_file) > 0:  # A file is currently open.
                if not window.data['dirty'] or save_prompt('opening a new tileset'):
                    # No data will be lost or the user has accepted data loss
                    window.tileset_image = PhotoImage(filename)
                    window.tileset_canvas.grid(column=0, row=0)



                    redraw_canvas()
                    window.loaded_file = filename

        except TclError:
            error_msg(f'Error opening file: \'{filename}\'')


def file_save(*args):
    window.data['dirty'] = False
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

    @staticmethod
    def verify_int(value):
        if value.isdigit() or value == '':
            return True
        return False

    def __init__(self):
        super().__init__()

        self.data = {
            'dirty': False,  # Set to true whenever there are unsaved changes
            'view': {
                'highlight_color': StringVar(),
                'grid_size': StringVar(),
                'show_grid': BooleanVar(),
                'show_block_types': BooleanVar(),
            },
            'export': {
                'pixel_scale': StringVar(),
                'block_ids': StringVar(),
                'bgo_ids': StringVar(),
                'create_pge_tileset': BooleanVar(),
                'start_high': BooleanVar(),
            },
            'current_tile': {

                # Internally assigned
                'x': IntVar(),
                'y': IntVar(),
                'w': IntVar(),
                'h': IntVar(),

                # Tile Type (Block/BGO)
                'type': StringVar(),

                # Settings for both Blocks and BGOs
                'id': StringVar(),
                'animation': {
                    'frames': StringVar(),
                    'framespeed': StringVar(),
                },
                'light': {
                    'lightoffsetx': StringVar(),
                    'lightoffsety': StringVar(),
                    'lightradius': StringVar(),
                    'lightcolor': StringVar(),
                    'lightflicker': BooleanVar(),
                },

                # Settings exclusive to BGOs
                'priority': StringVar(),

                # Settings exclusive to Blocks
                'content_type': StringVar(),
                'content_id': StringVar(),
                'collision_type': StringVar(),
                'sizable': BooleanVar(),
                'pswitchable': BooleanVar(),
                'slippery': BooleanVar(),
                'bumpable': BooleanVar(),
                'smashable': StringVar(),
            },
            'tiles': [],
        }

        self.title("SMBX2 Tileset Importer")
        self.iconbitmap('data/icon.ico')
        self.resizable(False, False)

        self.mainframe = ttk.Frame(self, padding="3 3 12 12")  # cover the root with a frame that has a modern style
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))  # placed directly in application window
        self.columnconfigure(0, weight=1)  # fill the whole window vertically, even when resized
        self.rowconfigure(0, weight=1)  # same horizontally

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

        self.highlight_color = self.data['view']['highlight_color']
        self.highlight_color.set(data_defaults['view']['highlight_color'])
        ttk.Label(self.view_box, text='Highlight Color:').grid(column=1, row=next_row(), sticky=W)
        self.color_selector = ttk.Frame(self.view_box)
        self.color_selector.grid(column=1, row=next_row(), sticky=(W, E), padx=2)
        self.color_preview = Frame(self.color_selector, borderwidth=2, relief='sunken', width=23, height=23,
                                   background=self.highlight_color.get())
        self.color_preview.grid(column=1, row=1, sticky=W)
        color_button = ttk.Button(self.color_selector, text='Select Color', command=change_highlight_color)
        color_button.grid(column=2, row=1, sticky=W)
        CreateToolTip(color_button, 'Change the color that will be used to highlight selected tiles. Use this if the '
                                    'current color does not contrast well with the tile colors.')

        self.grid_size = self.data['view']['grid_size']
        ttk.Label(self.view_box, text='Grid Size:').grid(column=1, row=next_row(), sticky=W, padx=0)
        grid_size_box = ttk.Combobox(self.view_box, textvariable=self.grid_size, values=('8', '16', '32'), width=6)
        grid_size_box.grid(column=1, row=next_row(), sticky=W)
        CreateToolTip(grid_size_box, 'The size of the grid. This is applied before image scaling.')

        self.grid_show = self.data['view']['show_grid']
        ttk.Checkbutton(self.view_box, text='Show Grid', variable=self.grid_show, offvalue=False, onvalue=True) \
            .grid(column=1, row=next_row(), sticky=W)

        self.show_block_types = self.data['view']['show_block_types']
        ttk.Checkbutton(self.view_box, text='Show Block Types', variable=self.show_block_types, offvalue=False,
                        onvalue=True).grid(column=1, row=next_row(), sticky=W)

        # Export Settings Section

        self.export_box = ttk.LabelFrame(self.config_frame, text='Export Settings', padding='3 3 12 8')
        self.export_box.grid(column=1, row=2, sticky=(W, E))

        self.pixel_scale = self.data['export']['pixel_scale']
        ttk.Label(self.export_box, text='Pixel Scale:').grid(column=1, row=next_row(1), sticky=W)
        pixel_scale_box = ttk.Combobox(self.export_box, textvariable=self.pixel_scale, values=('1', '2', '4'), width=6)
        pixel_scale_box.grid(column=1, row=next_row(), sticky=W)
        CreateToolTip(pixel_scale_box, 'The scale factor that will be applied to the image before exporting as block'
                                       ' images. Also changes the scale at which the image is displayed in this editor.')

        self.block_ids = self.data['export']['block_ids']
        ttk.Label(self.export_box, text='Block IDs:').grid(column=1, row=next_row(), sticky=W)
        block_ids_box = ttk.Combobox(self.export_box, textvariable=self.block_ids,
                                     values=('Avoid Special', 'User Slots', ''), width=16)
        block_ids_box.grid(column=1, row=next_row(), sticky=W)
        CreateToolTip(block_ids_box, 'The pool of Block IDs to be assigned or overwritten. IDs can be described in the '
                                     'following ways, separated by semicolons (;):\n\n'
                                     '<single number> - assigns one ID\n\n'
                                     '<lo>-<hi> - a range from low to high. Inclusive.\n\n'
                                     'Example: 1-27;48;99-107\n\n'
                                     'Presets:\n\n'
                                     'Avoid Special: Avoids overwriting item blocks, blocks with special '
                                     'interactions such as lava, spikes, or filters; and pipes.\n\n'
                                     'User Slots: Overwrites blocks in the user-defined block range (751-1000)')

        self.create_pge_tileset = self.data['export']['create_pge_tileset']
        pge_tileset_box = ttk.Checkbutton(self.export_box, text='Create PGE Tileset', variable=self.create_pge_tileset,
                                          offvalue=False, onvalue=True)
        pge_tileset_box.grid(column=1, row=next_row(), sticky=W)
        CreateToolTip(pge_tileset_box, 'Auto-generate a *.tileset.ini file for PGE containing all blocks in this '
                                       'tileset. This file will have the same name as the tileset image.')

        # ------------------------------------------
        # Tileset View
        # ------------------------------------------

        self.tileset_frame = ttk.Frame(self.mainframe, width=400, height=300)
        self.tileset_frame.grid(column=2, row=1, sticky=N)

        self.launch_frame = ttk.Frame(self.tileset_frame)
        self.launch_frame.place(in_=self.tileset_frame, anchor='c', relx=.5, rely=.5)
        ttk.Label(self.launch_frame, text='No tileset image currently loaded.', padding='0 0 4 4') \
            .grid(column=1, row=next_row(1))
        ttk.Button(self.launch_frame, text='Open Image', command=file_open).grid(column=1, row=next_row())

        self.loaded_file = ''
        self.tileset_image = None
        # No border, no highlight frame (these cause cutoff)
        self.tileset_canvas = Canvas(self.tileset_frame, width=400, height=300, bd=0, highlightthickness=0)

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

        self.block_id = StringVar()
        ttk.Label(self.tile_box, text='Block ID:').grid(column=1, row=next_row(), sticky=W)
        block_id_entry = ttk.Entry(self.tile_box, textvariable=self.block_id, width=6)
        block_id_entry.grid(column=1, row=next_row(), sticky=W)
        CreateToolTip(block_id_entry, 'The ID to assign to this block. Use this to overwrite blocks with special '
                                      'interactions such as item blocks, spikes, and filters. Leave this field blank '
                                      'to automatically assign an ID from the Block IDs pool.')

        self.animation_frames = StringVar(None, '1')
        ttk.Label(self.tile_box, text='Animation Frames:').grid(column=1, row=next_row(), sticky=W)
        ttk.Spinbox(self.tile_box, from_=1, to=100, textvariable=self.animation_frames, width=6) \
            .grid(column=1, row=next_row(), sticky=W)

        self.contents = StringVar(None, '0')
        ttk.Label(self.tile_box, text='Default Contents:').grid(column=1, row=next_row(), sticky=W)
        contents_box = ttk.Spinbox(self.tile_box, from_=-99, to=674, textvariable=self.contents, width=6)
        contents_box.grid(column=1, row=next_row(), sticky=W)
        CreateToolTip(contents_box, 'Default block contents. Set to 0 for no contents, a negative value for coins, '
                                    'or a positive value for an NPC.')

        self.sizable = BooleanVar(None, False)
        sizable_box = ttk.Checkbutton(self.tile_box, text='Sizable', variable=self.sizable, offvalue=False,
                                      onvalue=True)
        sizable_box.grid(column=1, row=next_row(), sticky=W)
        CreateToolTip(sizable_box, 'Sizable. If checked, the block should occupy a 3x3 space on the grid. Otherwise, '
                                   'weird things will happen in SMBX. Due to some unfortunate limitations, '
                                   'if you want a sizable that is not semisolid, you\'ll have to draw it manually in '
                                   'LunaLua. See the Sizables option under the Help tab for the code you\'ll need.')

        self.lava = BooleanVar(None, False)
        ttk.Checkbutton(self.tile_box, text='Lava', variable=self.lava, offvalue=False, onvalue=True) \
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
