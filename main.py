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
import tkinter
from tkinter import *
from tkinter import ttk, colorchooser, filedialog

import regex as regex

from tooltip import CreateToolTip
from widgets import ColorSelector, VerifiedWidget

MAX_BLOCK_ID = 1291
MAX_BGO_ID = 303
MAX_NPC_ID = 674

data_defaults = {

    # View

    'grid_size': '16',
    'show_grid': True,
    'show_block_types': True,
    'highlight_color': '#ff8040',

    # Export

    'pixel_scale': '2',
    'block_ids': 'Avoid Special',
    'bgo_ids': 'Avoid Special',
    'create_pge_tileset': True,
    'start_high': False,

    # Tile

    # Animation
    'frames': '1',
    'framespeed': '8',

    # Light
    'lightoffsetx': '0',
    'lightoffsety': '0',
    'lightradius': '128',
    'lightbrightness': '1',
    'lightcolor': '#ffffff',
    'lightflicker': False,

    # BGO Exclusive
    'priority': -85,

    # Behavior (Block Exclusive)
    'content_type': 'empty',
    'content_id': '0',

    'collision_type': 'Solid',

    'sizable': False,
    'pswitchable': False,
    'slippery': False,
    'lava': False,
    'bumpable': False,
    'smashable': '0',
}

current_row = 0
readonly_widget_map = {}


def cur_row():
    return current_row


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


built_in_id_lists = {
    'Block': {
        'Avoid Special': '1;3;6-29;38-54;56-59;61-87;91-108;113-114;116-168;182-191;194-223;227-266;270-279;284-370'
                         ';372-403;407-419;421-427;432-456;488-525;527-597;599-619;630;635-638;1001-1005;1008-1072'
                         ';1076-1101;1106-1132;1138-1141;1156-1267;1269-1270',
        'User Slots': '751-1000',
    },
    'BGO': {
        'Avoid Special': '1-10;14-34;36-59;62-69;75-86;89-91;93-97;99;101-103;106;108-133;147-159;161-173;187-190;232'
                         '-279;281-303',
        'User Slots': '751-1000',
    }
}


def get_id_list_preset(value, tile_type):
    if value in built_in_id_lists[tile_type]:
        return built_in_id_lists[tile_type][value]
    return value


def parse_id_list(value, tile_type, check_valid_only=False):
    value = get_id_list_preset(value, tile_type)
    if value == '' or regex.match(r'^(\d+(?:-\d+)?;?)+$', value) is None:
        return False, None
    ids = []
    last_id = 0
    for x in value.split(';'):
        x_split = x.split('-')
        lo = x_split[0]
        if not lo.isdigit():
            return False, None
        lo = int(lo)
        if lo <= last_id:
            return False, None
        hi = None
        if len(x_split) == 2:
            hi = int(x_split[1])
        if hi is not None:
            if hi <= lo:
                return False, None
            last_id = hi
            if not check_valid_only:
                for v in range(lo, hi + 1):
                    ids.append(v)
        else:
            last_id = lo
            if not check_valid_only:
                ids.append(lo)
    return True, ids


def verify_id_list(value, tile_type):
    return value == '' or regex.match(r'^[0-9\-;]+$', get_id_list_preset(value, tile_type)) is not None


def verify_block_id_list(value):
    return verify_id_list(value, 'Block')


def verify_bgo_id_list(value):
    return verify_id_list(value, 'BGO')


def good_block_id_list(value):
    return parse_id_list(value, 'Block', True)[0]


def good_bgo_id_list(value):
    return parse_id_list(value, 'BGO', True)[0]


def good_tile_id(value):
    if value == '':
        return True
    if value == '-':
        return False
    tile_type = window.data['type'].get()
    value = int(value)
    return tile_type == 'Block' and 1 <= value <= MAX_BLOCK_ID \
           or tile_type == 'BGO' and (1 <= value <= MAX_BGO_ID or 751 <= value <= 1000)


def good_content_id(value):
    if value == '':
        return False
    content_type = window.data['content_type'].get()
    value = int(value)
    return content_type == 'Coins' and 1 <= value <= 99 \
           or content_type == 'NPC' and (1 <= value <= MAX_NPC_ID or 751 <= value <= 1000)


def update_tile_type(*args):
    tile_type = window.data['type'].get()
    if tile_type == 'Block':
        window.render_priority_input.configure(state=DISABLED)
        for x in window.tile_behavior_frame.winfo_children():
            if str(x) in readonly_widget_map:
                x.configure(state='readonly')
            else:
                x.configure(state=NORMAL)
    elif tile_type == 'BGO':
        window.render_priority_input.configure(state=NORMAL)
        for x in window.tile_behavior_frame.winfo_children():
            x.configure(state=DISABLED)
    window.type_selector.check_variable()


def update_light_source(*args):
    state = NORMAL if window.data['light_source'].get() else DISABLED
    for x in window.light_frame.winfo_children():
        x.configure(state=state)


def update_content_type(*args):
    # If I get rid of this call, the conditional below always evaluates to True. Should I be worried?
    repr(window.content_type_box.config('state')[4])

    if window.data['content_type'].get() != 'Empty' and window.content_type_box['state'] != DISABLED:
        window.contents_box.configure(state=NORMAL)
        window.contents_box.check_variable()
    else:
        window.contents_box.configure(state=DISABLED)


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

    def _verify_int(self, name, value):
        widget = self.nametowidget(name)
        name = name.split('.')[-1]  # Ignore the widget's lineage. I only want its name
        good_input = value.isdigit()
        valid = good_input or value == ''
        if good_input:
            try:
                min_val = int(widget.config('from')[4])
                max_val = int(widget.config('to')[4])
                good_input = min_val <= int(value) <= max_val
            except TclError:  # Does not have from and to properties; must check another way
                int_val = int(value)
                if name == 'grid_size':
                    good_input = 8 <= int_val <= 128
                elif name == 'pixel_scale':
                    good_input = 1 <= int_val <= 8
        if good_input:
            self.data['lv_' + name] = value

        self._update_style(name, good_input)

        self._bell_on_invalid(valid)
        return valid

    def __init__(self):
        super().__init__()

        # Styles for indicating bad inputs
        # I will ignore bad inputs that are of the right type but not in the acceptable range. This is to avoid a couple
        # problems I've seen in other programs:
        # 1. You try to clear the box so you can put in something else, but the empty string is not allowed. You have to
        #    add the value you want onto the end and then remove the first number. Annoying.
        # 2. Say the empty string is allowed, but values less than 8 are not. You want to put in 12. You can't type a 1
        #    or a 2 in the empty box because they're both too low. You are forced to type 812 and then remove the 8.
        #    Annoying.
        # How any UX designer notices either of these problems and doesn't immediately fix them is beyond me. /rant
        # style_bad = ttk.Style()
        # print(style_bad.theme_names())
        # style_bad.theme_use('clam')
        # style_bad.configure('bad.TCombobox', fieldbackground='#f4cccc', foreground='maroon')
        # style_bad_spinbox = ttk.Style()
        # style_bad_spinbox.configure('bad.TSpinbox', background='#f4cccc')
        # style_bad_entry = ttk.Style()
        # style_bad_entry.configure('bad.TEntry', background='#f4cccc')

        self.data = {
            # Set to true whenever there are unsaved changes
            'dirty': False,

            # View

            'highlight_color': StringVar(),
            'grid_size': StringVar(),
            'show_grid': BooleanVar(),
            'show_block_types': BooleanVar(),

            # Export

            'pixel_scale': StringVar(),
            'block_ids': StringVar(),
            'bgo_ids': StringVar(),
            'create_pge_tileset': BooleanVar(),
            'start_high': BooleanVar(),

            # Current Tile

            # Internally assigned
            'x': IntVar(),
            'y': IntVar(),
            'w': IntVar(),
            'h': IntVar(),

            # Tile Type (Block/BGO)
            'type': StringVar(),

            # Settings for both Blocks and BGOs
            'id': StringVar(),
            'frames': StringVar(),
            'framespeed': StringVar(),

            'noshadows': StringVar(),
            'light_source': BooleanVar(),
            'lightoffsetx': StringVar(),
            'lightoffsety': StringVar(),
            'lightradius': StringVar(),
            'lightbrightness': StringVar(),
            'lightcolor': StringVar(),
            'lightflicker': BooleanVar(),

            # Settings exclusive to BGOs
            'priority': StringVar(),

            # Settings exclusive to Blocks
            'collision_type': StringVar(),
            'content_type': StringVar(),
            'content_id': StringVar(),

            'playerfilter': StringVar(),
            'npcfilter': StringVar(),

            'sizable': BooleanVar(),
            'lava': BooleanVar(),
            'pswitchable': BooleanVar(),
            'ediblebyvine': BooleanVar(),
            'slippery': BooleanVar(),
            'bumpable': BooleanVar(),
            'smashable': StringVar(),
            'customhurt': BooleanVar(),

            'tiles': [],
        }

        self.label_width_tile_settings = 60
        self.label_width_appearance = 110
        self.label_width_behavior = 100

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

        # Highlight Color
        ttk.Label(self.view_box, text='Highlight Color:').grid(column=1, row=next_row(1), sticky=W)
        self.highlight_color = self.data['highlight_color']
        ColorSelector(self.view_box, variable=self.highlight_color, color=data_defaults['highlight_color'],
                      tooltip='Change the color that will be used to highlight selected tiles. Use this if the '
                              'current color does not contrast well with the tile colors.') \
            .grid(column=1, row=next_row(), sticky=W)

        # Grid Size
        VerifiedWidget(ttk.Combobox, {'values': ('8', '16', '32'), 'width': 6}, self.view_box,
                       variable=self.data['grid_size'], min_val=8, max_val=128, orientation='vertical',
                       label_text='Grid Size:',
                       tooltip='Size of each grid square in pixels. Must be between 8 and 128, inclusive.') \
            .grid(column=1, row=next_row(), sticky=W)

        # Show Grid
        ttk.Checkbutton(self.view_box, text='Show Grid', variable=self.data['show_grid'], offvalue=False, onvalue=True) \
            .grid(column=1, row=next_row(), sticky=W)

        # Show Block Types
        ttk.Checkbutton(self.view_box, text='Show Block Types', variable=self.data['show_block_types'], offvalue=False,
                        onvalue=True).grid(column=1, row=next_row(), sticky=W)

        # Export Settings Section

        self.export_box = ttk.LabelFrame(self.config_frame, text='Export Settings', padding='3 3 12 8')
        self.export_box.grid(column=1, row=2, sticky=(N, S, W, E))

        # Pixel Scale
        VerifiedWidget(ttk.Combobox, {'values': ('1', '2', '4'), 'width': 6}, self.export_box,
                       variable=self.data['pixel_scale'], min_val=1, max_val=8, orientation='vertical',
                       label_text='Pixel Scale:',
                       tooltip='The scale factor that will be applied to the image before exporting as block images. '
                               'Also changes the scale at which the image is displayed in this editor. Must be '
                               'between 1 and 8, inclusive.') \
            .grid(column=1, row=next_row(), sticky=W)

        # Block IDs
        VerifiedWidget(ttk.Combobox, {'values': ('Avoid Special', 'User Slots', ''), 'width': 12}, self.export_box,
                       variable=self.data['block_ids'], verify_function=verify_block_id_list,
                       good_function=good_block_id_list, orientation='vertical', label_text='Block IDs:',
                       tooltip='The pool of Block IDs to be assigned or overwritten. It is a list of IDs and/or ID'
                               'ranges, separated by semicolons (;). These IDs must be in ascending order.\n\n'
                               'Example Input: 1-3;37;48-50\n'
                               'This makes the pool of IDs contain 1,2,3,37,48,49, and 50.\n\n'
                               'Presets:\n\n'
                               'Avoid Special: Avoids overwriting item blocks, blocks with special '
                               'interactions such as lava, spikes, or filters; and pipes.\n\n'
                               'User Slots: Overwrites blocks in the user-defined block range (751-1000)') \
            .grid(column=1, row=next_row(), sticky=W)

        # BGO IDs
        VerifiedWidget(ttk.Combobox, {'values': ('Avoid Special', 'User Slots', ''), 'width': 12}, self.export_box,
                       variable=self.data['bgo_ids'], verify_function=verify_bgo_id_list,
                       good_function=good_bgo_id_list, orientation='vertical', label_text='BGO IDs:',
                       tooltip='The pool of Block IDs to be assigned or overwritten. It is a list of IDs and/or ID'
                               'ranges, separated by semicolons (;). These IDs must be in ascending order.\n\n'
                               'Example Input: 1-3;37;48-50\n'
                               'This makes the pool of IDs contain 1,2,3,37,48,49, and 50.\n\n'
                               'Presets:\n\n'
                               'Avoid Special: Avoids overwriting arrow BGOs and BGOs with special interactions '
                               'such as line guides, redirectors, and doors.\n\n'
                               'User Slots: Overwrites blocks in the user-defined BGO range (751-1000)') \
            .grid(column=1, row=next_row(), sticky=W)

        self.start_high = self.data['start_high']
        start_high_box = ttk.Checkbutton(self.export_box, text='IDs High to Low', variable=self.start_high,
                                         offvalue=False, onvalue=True)
        start_high_box.grid(column=1, row=next_row(), sticky=W)
        CreateToolTip(start_high_box, 'Assign IDs starting at the highest and decreasing, instead of the default '
                                      'lowest and increasing. Useful if you don\'t want to overwrite episode graphics'
                                      ' in a level.')

        self.create_pge_tileset = self.data['create_pge_tileset']
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

        self.tile_settings_frame = ttk.LabelFrame(self.tile_frame, text='Tile Settings', padding='3 3 12 8')
        self.tile_settings_frame.columnconfigure(1, minsize=self.label_width_tile_settings, weight=0)
        self.tile_settings_frame.columnconfigure(2, weight=1)
        self.tile_settings_frame.grid(column=1, row=1, sticky=N)

        # Tile Type
        # Keeps Contents entry from unlocking when it shouldn't
        self.data['type'].trace_add('write', update_content_type)
        # The trace registry seems to be a stack structure. The trace registered last is run first.
        self.data['type'].trace_add('write', update_tile_type)
        ttk.Label(self.tile_settings_frame, text='Tile Type:').grid(column=1, row=next_row(1), sticky=W, pady=4)
        self.tile_type = self.data['type']
        self.tile_type_box = ttk.Combobox(self.tile_settings_frame, width=6, textvariable=self.tile_type,
                                          state='readonly', values=('Block', 'BGO'))
        self.tile_type_box.grid(column=2, row=cur_row(), sticky=W)
        CreateToolTip(self.tile_type_box, 'The type of tile.')
        readonly_widget_map[str(self.tile_type_box)] = True

        # Tile ID
        self.type_selector = VerifiedWidget(ttk.Entry, {'width': 6}, self.tile_settings_frame, variable=self.data['id'],
                                            good_function=good_tile_id, label_text='Tile ID:',
                                            label_width=self.label_width_tile_settings,
                                            tooltip='The ID to assign to this tile. Use this to overwrite tiles with '
                                                    'special interactions such as item blocks, spikes, filters, '
                                                    'or line guides. Leave this field blank to automatically assign '
                                                    'an ID from the Block or BGO IDs pool.\n\n'
                                                    f'For blocks, this ID must be between 1 and {MAX_BLOCK_ID}.\n'
                                                    f'For BGOs, it must be between 1 and {MAX_BGO_ID} or between 751 '
                                                    'and 1000.')
        self.type_selector.grid(column=1, row=next_row(), columnspan=2, sticky=W)

        # Tile Appearance Settings

        self.tile_appearance_frame = ttk.LabelFrame(self.tile_settings_frame, text='Appearance', padding='3 3 12 8')
        self.tile_appearance_frame.grid(column=1, columnspan=2, row=next_row(), sticky=(N, W))
        self.tile_appearance_frame.columnconfigure(1, minsize=self.label_width_appearance, weight=0)
        self.tile_appearance_frame.columnconfigure(2, weight=1)

        # Animation Frames
        VerifiedWidget(ttk.Spinbox, {'width': 6}, self.tile_appearance_frame, variable=self.data['frames'], min_val=1,
                       max_val=1000, label_text='Animation Frames: ', label_width=self.label_width_appearance,
                       tooltip='Number of frames in the tile\'s animation') \
            .grid(column=1, row=next_row(), sticky=W)

        # Frame Speed
        VerifiedWidget(ttk.Spinbox, {'width': 6}, self.tile_appearance_frame, variable=self.data['framespeed'],
                       min_val=1, max_val=100, label_text='Frame Speed: ', label_width=self.label_width_appearance,
                       tooltip='Length of each frame of the animation, in game ticks.') \
            .grid(column=1, row=next_row(), sticky=W)

        # Render Priority
        # Must keep a reference so I can dynamically enable/disable
        self.render_priority_input = VerifiedWidget(ttk.Spinbox, {'width': 6}, self.tile_appearance_frame,
                                                    variable=self.data['priority'], min_val=-100, max_val=10,
                                                    label_text='Render Priority: ',
                                                    label_width=self.label_width_appearance,
                                                    tooltip='The tile\'s render priority. This is only available for '
                                                            'BGOs. Must be between -100 and 10')
        self.render_priority_input.grid(column=1, row=next_row(), sticky=W)

        # No Shadows
        self.no_shadows_box = ttk.Checkbutton(self.tile_appearance_frame, text='No Shadows',
                                              variable=self.data['noshadows'], offvalue=False, onvalue=True)
        self.no_shadows_box.grid(column=1, columnspan=2, row=next_row(), sticky=W)
        CreateToolTip(self.no_shadows_box, 'If set to true, the block will not be able to cast shadows in dark '
                                           'sections.')

        # Light Source
        self.data['light_source'].trace_add('write', update_light_source)
        self.light_source_box = ttk.Checkbutton(self.tile_appearance_frame, text='Light Source',
                                                variable=self.data['light_source'], offvalue=False, onvalue=True)
        self.light_source_box.grid(column=1, columnspan=2, row=next_row(), sticky=W)
        CreateToolTip(self.light_source_box, 'Whether or not the tile is a light source.')

        # Light Subsection
        self.light_frame = ttk.Frame(self.tile_appearance_frame)
        self.light_frame.grid(column=1, columnspan=2, row=next_row(), sticky=W)
        self.light_frame.columnconfigure(1, minsize=self.label_width_appearance, weight=0)
        self.light_frame.columnconfigure(2, weight=1)

        # Light Offset X
        VerifiedWidget(ttk.Entry, {'width': 6}, self.light_frame, variable=self.data['lightoffsetx'],
                       label_text='Light Offset X:', label_width=self.label_width_appearance,
                       tooltip='Horizontal offset of the light source relative to the center of the object.') \
            .grid(column=1, row=next_row(1), sticky=W)

        # Light Offset Y
        VerifiedWidget(ttk.Entry, {'width': 6}, self.light_frame, variable=self.data['lightoffsety'],
                       label_text='Light Offset Y:', label_width=self.label_width_appearance,
                       tooltip='Vertical offset of the light source relative to the center of the object.') \
            .grid(column=1, row=next_row(), sticky=W)

        # Light Radius
        VerifiedWidget(ttk.Entry, {'width': 6}, self.light_frame, variable=self.data['lightradius'],
                       label_text='Light Radius:', label_width=self.label_width_appearance,
                       tooltip='Radius of the light source.') \
            .grid(column=1, row=next_row(), sticky=W)

        # Light Brightness
        VerifiedWidget(ttk.Entry, {'width': 6}, self.light_frame, variable=self.data['lightbrightness'],
                       label_text='Light Brightness:', label_width=self.label_width_appearance,
                       tooltip='Brightness of the light source.') \
            .grid(column=1, row=next_row(), sticky=W)

        # Light Color
        ttk.Label(self.light_frame, text='Light Color:').grid(column=1, row=next_row(), sticky=W)
        ColorSelector(self.light_frame, variable=self.data['lightcolor'],
                      tooltip='The color of the light source.') \
            .grid(column=1, columnspan=2, row=next_row(), sticky=W)

        # Light Flicker
        lf = ttk.Checkbutton(self.light_frame, variable=self.data['lightflicker'],
                             text='Light Flicker', offvalue=False, onvalue=True)
        lf.grid(column=1, row=next_row(), sticky=W)
        CreateToolTip(lf, 'The color of the light source.')

        # Tile Behavior Settings

        self.tile_behavior_frame = ttk.LabelFrame(self.tile_settings_frame, text='Block Behavior', padding='3 3 12 8')
        self.tile_behavior_frame.grid(column=3, row=3, sticky=(N, S, W), padx=4)
        self.tile_behavior_frame.columnconfigure(1, minsize=self.label_width_behavior, weight=0)
        self.tile_behavior_frame.columnconfigure(2, weight=1)

        # Collision Type
        self.collision_type = self.data['collision_type']
        ttk.Label(self.tile_behavior_frame, text='Collision Type:   ').grid(column=1, row=next_row(1), sticky=W, pady=4)
        ct = ttk.Combobox(self.tile_behavior_frame, state='readonly', textvariable=self.collision_type, width=12,
                          values=(
                              "Solid", "Semisolid", "Passthrough", "Slope ◢", "Slope ◣", "Slope ◥", "Slope ◤"
                          ))
        ct.grid(column=2, row=cur_row(), sticky=W)
        readonly_widget_map[str(ct)] = True

        # Content Type
        self.data['content_type'].trace_add('write', update_content_type)
        ttk.Label(self.tile_behavior_frame, text='Content Type:').grid(column=1, row=next_row(), sticky=W, pady=4)
        # Keep a reference so I can check the state later
        self.content_type_box = ttk.Combobox(self.tile_behavior_frame, state='readonly',
                                             textvariable=self.data['content_type'], width=12,
                                             values=('Empty', 'Coins', 'NPC'))
        self.content_type_box.grid(column=2, row=cur_row(), sticky=W)
        readonly_widget_map[str(self.content_type_box)] = True

        # Contents
        self.contents_box = VerifiedWidget(ttk.Entry, {'width': 6}, self.tile_behavior_frame,
                                           variable=self.data['content_id'], good_function=good_content_id,
                                           label_text='Contents:', label_width=self.label_width_behavior,
                                           tooltip='The contents of the block. Must be between 1 and 99 for coins. '
                                                   'Must be between 1 and 99 for coins. Must be between 1 and '
                                                   f'{MAX_NPC_ID} for NPCs.')
        self.contents_box.grid(column=1, columnspan=2, row=next_row(), sticky=W)

        # Smashable
        VerifiedWidget(ttk.Spinbox, {'width': 6}, self.tile_behavior_frame, variable=self.data['smashable'], min_val=0,
                       max_val=3, label_text='Smashable:', label_width=self.label_width_behavior,
                       tooltip='Determines how durable the block should be with regards to certain NPCs '
                               'that break blocks. Can be a number between 0 and 3. 1 = hit/triggered by '
                               'the NPC, but not broken; 2 = broken by the NPC; 3 = effortlessly broken by '
                               'the NPC') \
            .grid(column=1, columnspan=2, row=next_row(), sticky=W)

        # Player Filter
        VerifiedWidget(ttk.Entry, {'width': 6}, self.tile_behavior_frame, variable=self.data['playerfilter'],
                       min_val=-1, max_val=16, label_text='Player Filter:', label_width=self.label_width_behavior,
                       tooltip='Character ID that is allowed to pass through this block. -1 means all character IDs.') \
            .grid(column=1, columnspan=2, row=next_row(), sticky=W)

        # NPC Filter
        VerifiedWidget(ttk.Entry, {'width': 6}, self.tile_behavior_frame, variable=self.data['npcfilter'],
                       min_val=-1, max_val=16, label_text='NPC Filter:', label_width=self.label_width_behavior,
                       tooltip='NPC ID that is allowed to pass through this block. -1 means all NPC IDs.') \
            .grid(column=1, columnspan=2, row=next_row(), sticky=W)

        # Sizable
        self.sizable = self.data['sizable']
        self.sizable_box = ttk.Checkbutton(self.tile_behavior_frame, text='Sizable', variable=self.sizable,
                                           offvalue=False, onvalue=True)
        self.sizable_box.grid(column=1, row=next_row(), sticky=W)
        CreateToolTip(self.sizable_box, 'Sizable. If checked, the block should occupy a 3x3 space on the grid. '
                                        'Otherwise, weird things will happen in SMBX. Due to some unfortunate '
                                        'limitations, if you want a sizable that is not semisolid, you\'ll have to '
                                        'draw it manually in LunaLua.')

        # Lava
        self.lava = self.data['lava']
        self.lava_box = ttk.Checkbutton(self.tile_behavior_frame, text='Lava', variable=self.lava, offvalue=False,
                                        onvalue=True)
        self.lava_box.grid(column=1, row=next_row(), sticky=W)
        CreateToolTip(self.lava_box, 'If true, the block acts as lava.')

        # P-switch-able
        self.pswitchable = self.data['pswitchable']
        self.pswitchable_box = ttk.Checkbutton(self.tile_behavior_frame, text='P-Switch-able',
                                               variable=self.pswitchable, offvalue=False, onvalue=True)
        self.pswitchable_box.grid(column=1, row=next_row(), sticky=W)
        CreateToolTip(self.lava_box, 'If true, the block turns into a coin when a P-Switch is hit.')

        # Edible By Vine
        self.ediblebyvine = self.data['ediblebyvine']
        self.ediblebyvine_box = ttk.Checkbutton(self.tile_behavior_frame, text='Edible By Vine',
                                                variable=self.ediblebyvine, offvalue=False, onvalue=True)
        self.ediblebyvine_box.grid(column=1, row=next_row(), sticky=W)
        CreateToolTip(self.ediblebyvine_box, 'If set to true, the block can be eaten by Mutant Vine NPCs.')

        # Slippery
        self.slippery = self.data['slippery']
        self.slippery_box = ttk.Checkbutton(self.tile_behavior_frame, text='Slippery', variable=self.slippery,
                                            offvalue=False, onvalue=True)
        self.slippery_box.grid(column=2, row=next_row(7), sticky=W)
        CreateToolTip(self.slippery_box, 'If true, the block will be slippery by default.')

        # Bumpable
        self.bumpable = self.data['bumpable']
        self.bumpable_box = ttk.Checkbutton(self.tile_behavior_frame, text='Bumpable', variable=self.bumpable,
                                            offvalue=False, onvalue=True)
        self.bumpable_box.grid(column=2, row=next_row(), sticky=W)
        CreateToolTip(self.bumpable_box, 'If true, the block can be bumped by players and NPCs.')

        # Custom Hurt
        self.customhurt = self.data['customhurt']
        self.customhurt_box = ttk.Checkbutton(self.tile_behavior_frame, text='Custom Hurt', variable=self.customhurt,
                                              offvalue=False, onvalue=True)
        self.customhurt_box.grid(column=2, row=next_row(), sticky=W)
        CreateToolTip(self.customhurt_box, 'Set to true to register your block as part of the list of harmful blocks. '
                                           'Note: This does NOT make the block harmful to players on its own. It only '
                                           'adds it to a list in Lua so other code will identify it as harmful. To '
                                           'make a block harmful, you must make it replace a harmful block or use '
                                           'LunaLua.')

        # Tile Preview

        # self.preview_box = ttk.LabelFrame(self.tile_frame, text='Preview', padding='3 3 12 8')
        # self.preview_box.grid(column=1, row=2, sticky=(W, E))
        # self.preview_box.rowconfigure(0, weight=1)
        # self.preview_box.columnconfigure(0, weight=1)
        #
        # self.preview = Frame(self.preview_box, background='#ff8040', width=32, height=32)
        # self.preview.grid(column=0, row=0, sticky="")

        # Add some padding to all children
        for child in self.mainframe.winfo_children():
            try:
                child.grid_configure(padx=5, pady=5)
            except TclError:
                pass


if __name__ == '__main__':
    window = Window()

    window.mainloop()
