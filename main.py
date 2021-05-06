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
from widgets import ColorSelector

data_defaults = {
    'view': {
        'grid_size': '16',
        'show_grid': True,
        'show_block_types': True,
        'highlight_color': '#ff8040',
    },
    'export': {
        'pixel_scale': '2',
        'block_ids': 'Avoid Special',
        'bgo_ids': 'Avoid Special',
        'create_pge_tileset': True,
        'start_high': False,
    },
    'tile:': {
        'animation': {
            'frames': '1',
            'framespeed': '8',
        },
        'light': {
            'lightoffsetx': '0',
            'lightoffsety': '0',
            'lightradius': '128',
            'lightbrightness': '1',
            'lightcolor': '#ffffff',
            'lightflicker': False,
        },
        'priority': -85,
        'behavior': {
            'content_type': 'empty',
            'content_id': '0',

            'collision_type': 'Solid',

            'sizable': False,
            'pswitchable': False,
            'slippery': False,
            'lava': False,
            'bumpable': False,
            'smashable': '0',
        },
    },
}

current_row = 0


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
        return value.isdigit() or value == ''

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
                'frames': StringVar(),
                'framespeed': StringVar(),

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

        ttk.Label(self.view_box, text='Highlight Color:').grid(column=1, row=next_row(1), sticky=W)
        self.highlight_color = self.data['view']['highlight_color']
        ColorSelector(self.view_box, variable=self.highlight_color, color=data_defaults['view']['highlight_color'],
                      tooltip='Change the color that will be used to highlight selected tiles. Use this if the '
                              'current color does not contrast well with the tile colors.') \
            .grid(column=1, row=next_row(), sticky=W)

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
        self.export_box.grid(column=1, row=2, sticky=(N, S, W, E))

        self.pixel_scale = self.data['export']['pixel_scale']
        ttk.Label(self.export_box, text='Pixel Scale:').grid(column=1, row=next_row(1), sticky=W)
        pixel_scale_box = ttk.Combobox(self.export_box, textvariable=self.pixel_scale, values=('1', '2', '4'), width=6)
        pixel_scale_box.grid(column=1, row=next_row(), sticky=W)
        CreateToolTip(pixel_scale_box, 'The scale factor that will be applied to the image before exporting as block'
                                       ' images. Also changes the scale at which the image is displayed in this editor.')

        self.block_ids = self.data['export']['block_ids']
        ttk.Label(self.export_box, text='Block IDs:').grid(column=1, row=next_row(), sticky=W)
        block_ids_box = ttk.Combobox(self.export_box, textvariable=self.block_ids,
                                     values=('Avoid Special', 'User Slots', ''), width=12)
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

        self.bgo_ids = self.data['export']['bgo_ids']
        ttk.Label(self.export_box, text='BGO IDs:').grid(column=1, row=next_row(), sticky=W)
        block_ids_box = ttk.Combobox(self.export_box, textvariable=self.bgo_ids,
                                     values=('Avoid Special', 'User Slots', ''), width=12)
        block_ids_box.grid(column=1, row=next_row(), sticky=W)
        CreateToolTip(block_ids_box, 'The pool of BGO IDs to be assigned or overwritten. IDs can be described in the '
                                     'following ways, separated by semicolons (;):\n\n'
                                     '<single number> - assigns one ID\n\n'
                                     '<lo>-<hi> - a range from low to high. Inclusive.\n\n'
                                     'Example: 1-27;48;99-107\n\n'
                                     'Presets:\n\n'
                                     'Avoid Special: Avoids overwriting arrow BGOs and BGOs with special interactions '
                                     'such as line guides, redirectors, and doors.\n\n'
                                     'User Slots: Overwrites blocks in the user-defined BGO range (751-1000)')

        self.start_high = self.data['export']['start_high']
        start_high_box = ttk.Checkbutton(self.export_box, text='IDs High to Low', variable=self.start_high,
                                         offvalue=False, onvalue=True)
        start_high_box.grid(column=1, row=next_row(), sticky=W)
        CreateToolTip(start_high_box, 'Assign IDs starting at the highest and decreasing, instead of the default '
                                      'lowest and increasing. Useful if you don\'t want to overwrite episode graphics'
                                      ' in a level.')

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

        self.tile_settings_frame = ttk.LabelFrame(self.tile_frame, text='Tile Settings', padding='3 3 12 8')
        self.tile_settings_frame.grid(column=1, row=1, sticky=N)

        ttk.Label(self.tile_settings_frame, text='Tile Type:').grid(column=1, row=next_row(1), sticky=W, pady=4)
        self.tile_type = self.data['current_tile']['type']
        self.tile_type_box = ttk.Combobox(self.tile_settings_frame, width=6, textvariable=self.tile_type,
                                          state='readonly', values=('Block', 'BGO'))
        self.tile_type_box.grid(column=2, row=cur_row(), sticky=W)
        CreateToolTip(self.tile_type_box, 'The type of tile.')

        ttk.Label(self.tile_settings_frame, text='Tile ID:').grid(column=1, row=next_row(), sticky=W, pady=4)
        self.block_id = self.data['current_tile']['id']
        block_id_entry = ttk.Entry(self.tile_settings_frame, textvariable=self.block_id, width=6)
        block_id_entry.grid(column=2, row=cur_row(), sticky=W)
        CreateToolTip(block_id_entry, 'The ID to assign to this tile. Use this to overwrite tiles with special '
                                      'interactions such as item blocks, spikes, filters, or line guides. Leave this '
                                      'field blank to automatically assign an ID from the Block or BGO IDs pool.')

        # Tile Appearance Settings

        self.tile_appearance_frame = ttk.LabelFrame(self.tile_settings_frame, text='Appearance', padding='3 3 12 8')
        self.tile_appearance_frame.grid(column=1, columnspan=2, row=next_row(), sticky=(N, W))

        # Animation Frames
        ttk.Label(self.tile_appearance_frame, text='Animation Frames:  ').grid(column=1, row=next_row(1), sticky=W,
                                                                             pady=4)
        self.animation_frames = self.data['current_tile']['frames']
        self.animation_frames_box = ttk.Spinbox(self.tile_appearance_frame, from_=1, to=100,
                                                textvariable=self.animation_frames, width=6)
        self.animation_frames_box.grid(column=2, row=cur_row(), sticky=W)
        CreateToolTip(self.animation_frames_box, 'Number of frames in the tile\'s animation')

        # Frame Speed
        ttk.Label(self.tile_appearance_frame, text='Frame Speed:').grid(column=1, row=next_row(), sticky=W, pady=4)
        self.frame_speed = self.data['current_tile']['framespeed']
        self.frame_speed_box = ttk.Spinbox(self.tile_appearance_frame, from_=1, to=128, textvariable=self.frame_speed,
                                           width=6)
        self.frame_speed_box.grid(column=2, row=cur_row(), sticky=W)
        CreateToolTip(self.frame_speed_box, 'Length of each frame of the animation, in game ticks.')

        # Render priority
        ttk.Label(self.tile_appearance_frame, text='Render Priority:').grid(column=1, row=next_row(), sticky=W, pady=4)
        self.render_priority = self.data['current_tile']['priority']
        self.render_priority_box = ttk.Entry(self.tile_appearance_frame, textvariable=self.render_priority, width=6)
        self.render_priority_box.grid(column=2, row=cur_row(), sticky=W)
        CreateToolTip(self.render_priority_box, 'LunaLua render priority. This setting is only available for BGOs.')

        # No Shadows
        self.no_shadows = self.data['current_tile']['light_source']
        self.no_shadows_box = ttk.Checkbutton(self.tile_appearance_frame, text='No Shadows',
                                              variable=self.no_shadows, offvalue=False, onvalue=True)
        self.no_shadows_box.grid(column=1, columnspan=2, row=next_row(), sticky=W)
        CreateToolTip(self.no_shadows_box, 'If set to true, the block will not be able to cast shadows in dark '
                                           'sections.')

        # Light Source
        self.is_light_source = self.data['current_tile']['light_source']
        self.light_source_box = ttk.Checkbutton(self.tile_appearance_frame, text='Light Source',
                                                variable=self.is_light_source, offvalue=False, onvalue=True)
        self.light_source_box.grid(column=1, columnspan=2, row=next_row(), sticky=W)
        CreateToolTip(self.light_source_box, 'Whether or not the tile is a light source.')

        # Light Offset X
        ttk.Label(self.tile_appearance_frame, text='Light Offset X:').grid(column=1, row=next_row(), sticky=W, pady=4)
        self.light_offset_x = self.data['current_tile']['lightoffsetx']
        self.light_offset_x_box = ttk.Entry(self.tile_appearance_frame, textvariable=self.light_offset_x, width=6)
        self.light_offset_x_box.grid(column=2, row=cur_row(), sticky=W)
        CreateToolTip(self.light_offset_x_box, 'Horizontal offset of the light source relative to the center of the '
                                               'object.')

        # Light Offset Y
        ttk.Label(self.tile_appearance_frame, text='Light Offset Y:').grid(column=1, row=next_row(), sticky=W, pady=4)
        self.light_offset_y = self.data['current_tile']['lightoffsety']
        self.light_offset_y_box = ttk.Entry(self.tile_appearance_frame, textvariable=self.light_offset_y, width=6)
        self.light_offset_y_box.grid(column=2, row=cur_row(), sticky=W)
        CreateToolTip(self.light_offset_y_box, 'Vertical offset of the light source relative to the center of the '
                                               'object.')

        # Light Radius
        ttk.Label(self.tile_appearance_frame, text='Light Radius:').grid(column=1, row=next_row(), sticky=W, pady=4)
        self.light_radius = self.data['current_tile']['lightradius']
        self.light_radius_box = ttk.Entry(self.tile_appearance_frame, textvariable=self.light_radius, width=6)
        self.light_radius_box.grid(column=2, row=cur_row(), sticky=W)
        CreateToolTip(self.light_radius_box, 'Radius of the light source.')

        # Light Brightness
        ttk.Label(self.tile_appearance_frame, text='Light Brightness:').grid(column=1, row=next_row(), sticky=W, pady=4)
        self.light_brightness = self.data['current_tile']['lightbrightness']
        self.light_brightness_box = ttk.Entry(self.tile_appearance_frame, textvariable=self.light_brightness, width=6)
        self.light_brightness_box.grid(column=2, row=cur_row(), sticky=W)
        CreateToolTip(self.light_brightness_box, 'Brightness of the light source.')

        # Light Color
        ttk.Label(self.tile_appearance_frame, text='Light Color:').grid(column=1, row=next_row(), sticky=W)
        self.light_color = self.data['current_tile']['lightcolor']
        ColorSelector(self.tile_appearance_frame, variable=self.light_color, tooltip='The color of the light source.') \
            .grid(column=1, columnspan=2, row=next_row(), sticky=W)

        # Tile Behavior Settings

        self.tile_behavior_frame = ttk.LabelFrame(self.tile_settings_frame, text='Block Behavior', padding='3 3 12 8')
        self.tile_behavior_frame.grid(column=3, row=3, sticky=(N, S, W), padx=4)

        # Collision Type
        self.collision_type = self.data['current_tile']['collision_type']
        ttk.Label(self.tile_behavior_frame, text='Collision Type:   ').grid(column=1, row=next_row(1), sticky=W, pady=4)
        ttk.Combobox(self.tile_behavior_frame, state='readonly', textvariable=self.collision_type, width=12, values=(
            "Solid", "Semisolid", "Passthrough", "Slope ◢", "Slope ◣", "Slope ◥", "Slope ◤"
        )).grid(column=2, row=cur_row(), sticky=W)

        # Content Type
        ttk.Label(self.tile_behavior_frame, text='Content Type:').grid(column=1, row=next_row(), sticky=W, pady=4)
        self.content_type = self.data['current_tile']['content_type']
        self.content_type_box = ttk.Combobox(self.tile_behavior_frame, state='readonly', textvariable=self.content_type,
                                             width=12, values=('Empty', 'Coins', 'NPC'))
        self.content_type_box.grid(column=2, row=cur_row(), sticky=W)

        # Contents
        ttk.Label(self.tile_behavior_frame, text='Contents:').grid(column=1, row=next_row(), sticky=W, pady=4)
        self.contents = self.data['current_tile']['content_id']
        self.contents_box = ttk.Spinbox(self.tile_behavior_frame, textvariable=self.contents, width=6, from_=1, to=674)
        self.contents_box.grid(column=2, row=cur_row(), sticky=W)

        # Smashable
        ttk.Label(self.tile_behavior_frame, text='Smashable:').grid(column=1, row=next_row(), sticky=W, pady=4)
        self.smashable = self.data['current_tile']['smashable']
        self.smashable_box = ttk.Spinbox(self.tile_behavior_frame, textvariable=self.smashable, width=6, from_=1, to=3)
        self.smashable_box.grid(column=2, row=cur_row(), sticky=W)
        CreateToolTip(self.smashable_box, 'Determines how durable the block should be with regards to certain NPCs '
                                          'that break blocks. Can be a number between 0 and 3. 1 = hit/triggered by '
                                          'the NPC, but not broken; 2 = broken by the NPC; 3 = effortlessly broken by '
                                          'the NPC')

        # Player Filter
        ttk.Label(self.tile_behavior_frame, text='Player Filter:').grid(column=1, row=next_row(), sticky=W, pady=4)
        self.player_filter = self.data['current_tile']['playerfilter']
        self.player_filter_box = ttk.Entry(self.tile_behavior_frame, textvariable=self.player_filter, width=6)
        self.player_filter_box.grid(column=2, row=cur_row(), sticky=W)
        CreateToolTip(self.player_filter_box, 'Character ID that is allowed to pass through this block. -1 means all '
                                              'character IDs.')
        
        # NPC Filter
        ttk.Label(self.tile_behavior_frame, text='NPC Filter:').grid(column=1, row=next_row(), sticky=W, pady=4)
        self.npc_filter = self.data['current_tile']['npcfilter']
        self.npc_filter_box = ttk.Entry(self.tile_behavior_frame, textvariable=self.npc_filter, width=6)
        self.npc_filter_box.grid(column=2, row=cur_row(), sticky=W)
        CreateToolTip(self.npc_filter_box, 'NPC ID that is allowed to pass through this block. -1 means all NPC IDs.')

        # Sizable
        self.sizable = self.data['current_tile']['sizable']
        self.sizable_box = ttk.Checkbutton(self.tile_behavior_frame, text='Sizable', variable=self.sizable,
                                           offvalue=False, onvalue=True)
        self.sizable_box.grid(column=1, row=next_row(), sticky=W)
        CreateToolTip(self.sizable_box, 'Sizable. If checked, the block should occupy a 3x3 space on the grid. '
                                        'Otherwise, weird things will happen in SMBX. Due to some unfortunate '
                                        'limitations, if you want a sizable that is not semisolid, you\'ll have to '
                                        'draw it manually in LunaLua.') 

        # Lava
        self.lava = self.data['current_tile']['lava']
        self.lava_box = ttk.Checkbutton(self.tile_behavior_frame, text='Lava', variable=self.lava, offvalue=False,
                                        onvalue=True)
        self.lava_box.grid(column=1, row=next_row(), sticky=W)
        CreateToolTip(self.lava_box, 'If true, the block acts as lava.')
        
        # P-switch-able
        self.pswitchable = self.data['current_tile']['pswitchable']
        self.pswitchable_box = ttk.Checkbutton(self.tile_behavior_frame, text='P-Switch-able',
                                               variable=self.pswitchable, offvalue=False, onvalue=True)
        self.pswitchable_box.grid(column=1, row=next_row(), sticky=W)
        CreateToolTip(self.lava_box, 'If true, the block turns into a coin when a P-Switch is hit.')
        
        # Edible By Vine
        self.ediblebyvine = self.data['current_tile']['ediblebyvine']
        self.ediblebyvine_box = ttk.Checkbutton(self.tile_behavior_frame, text='Edible By Vine',
                                                variable=self.ediblebyvine, offvalue=False, onvalue=True)
        self.ediblebyvine_box.grid(column=1, row=next_row(), sticky=W)
        CreateToolTip(self.ediblebyvine_box, 'If set to true, the block can be eaten by Mutant Vine NPCs.')
        
        # Slippery
        self.slippery = self.data['current_tile']['slippery']
        self.slippery_box = ttk.Checkbutton(self.tile_behavior_frame, text='Slippery', variable=self.slippery,
                                            offvalue=False, onvalue=True)
        self.slippery_box.grid(column=2, row=next_row(7), sticky=W)
        CreateToolTip(self.slippery_box, 'If true, the block will be slippery by default.')
        
        # Bumpable
        self.bumpable = self.data['current_tile']['bumpable']
        self.bumpable_box = ttk.Checkbutton(self.tile_behavior_frame, text='Bumpable', variable=self.bumpable,
                                            offvalue=False, onvalue=True)
        self.bumpable_box.grid(column=2, row=next_row(), sticky=W)
        CreateToolTip(self.bumpable_box, 'If true, the block can be bumped by players and NPCs.')
        
        # Custom Hurt
        self.customhurt = self.data['current_tile']['customhurt']
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
