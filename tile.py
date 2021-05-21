"""
Tile Class
Contains all the data needed to create a Block or BGO in SMBX2
"""

# -------------------------------
# Tile Type Drawing Functions
# -------------------------------
from tkinter import PhotoImage, NW, NORMAL, HIDDEN

TILE_INSET = 6
T = TILE_INSET


def draw_square_tile(c, x1, y1, x2, y2, passthrough=False):
    poly = c.create_rectangle(x1 + T, y1 + T, x2 - T, y2 - T)
    if passthrough:
        c.itemconfigure(poly, dash=(8, 8))
    return poly


def draw_semisolid(c, x1, y1, x2, y2):
    return c.create_polygon(x1 + T, y1 + T, x2 - T, y1 + T, x2 - T, y2 - T, x1 + T, y2 - T, x1 + T, y1 + T,
                            (x1 + x2) // 2, (y1 + y2) // 2, x2 - T, y1 + T)


def draw_slope_1(c, x1, y1, x2, y2):
    # Slope ◢
    return c.create_polygon(x2 - T, y1 + T, x2 - T, y2 - T, x1 + T, y2 - T)


def draw_slope_2(c, x1, y1, x2, y2):
    # Slope ◣
    return c.create_polygon(x1 + T, y1 + T, x2 - T, y2 - T, x1 + T, y2 - T)


def draw_slope_3(c, x1, y1, x2, y2):
    # Slope ◥
    return c.create_polygon(x1 + T, y1 + T, x2 - T, y1 + T, x2 - T, y2 - T)


def draw_slope_4(c, x1, y1, x2, y2):
    # Slope ◤
    return c.create_polygon(x1 + T, y1 + T, x2 - T, y1 + T, x1 + T, y2 - T)


def draw_passthrough(c, x1, y1, x2, y2):
    return draw_square_tile(c, x1, y1, x2, y2, True)


tile_draw_functions = {
    'Solid': draw_square_tile,
    'Semisolid': draw_semisolid,
    'Passthrough': draw_passthrough,
    'Slope ◢': draw_slope_1,
    'Slope ◣': draw_slope_2,
    'Slope ◥': draw_slope_3,
    'Slope ◤': draw_slope_4,
}

# -------------------------------
# Defaults
# -------------------------------

defaults = {
    # General information
    'tile_type': 'Block',
    'tile_id': '',

    # Animation
    'frames': '1',
    'framespeed': '8',

    # Light
    'no_shadows': False,
    'light_source': False,
    'lightoffsetx': '0',
    'lightoffsety': '0',
    'lightradius': '128',
    'lightbrightness': '1',
    'lightcolor': '#ffffff',
    'lightflicker': False,

    # BGO Exclusive
    'priority': '-85',

    # Behavior (Block Exclusive)
    'collision_type': 'Solid',
    'content_type': 'Empty',
    'content_id': '1',
    'smashable': '0',
    'playerfilter': '0',
    'npcfilter': '0',

    'sizable': False,
    'pswitchable': False,
    'slippery': False,
    'lava': False,
    'bumpable': False,
    'customhurt': False,
    'ediblebyvine': False,
}

# Settings to be checked for all tiles
unconditional_settings = ['tile_type', 'tile_id', 'frames', 'framespeed', 'no_shadows', 'light_source']
# Settings for light sources only
light_settings = ['lightoffsetx', 'lightoffsety', 'lightradius', 'lightbrightness', 'lightcolor', 'lightflicker']
# Settings for BGOs only
bgo_settings = ['priority']
# Settings for Blocks only
block_settings = ['collision_type', 'content_type', 'smashable', 'playerfilter', 'npcfilter', 'sizable', 'pswitchable',
                  'slippery', 'lava', 'bumpable', 'customhurt', 'ediblebyvine']
content_settings = ['content_id']
# All settings (for load) -- currently unused
all_settings = ['tile_type', 'tile_id', 'frames', 'framespeed', 'no_shadows', 'light_source', 'lightoffsetx',
                'lightoffsety', 'lightradius', 'lightbrightness', 'lightcolor', 'lightflicker', 'priority',
                'collision_type', 'content_type', 'smashable', 'playerfilter', 'npcfilter', 'sizable', 'pswitchable',
                'slippery', 'lava', 'bumpable', 'customhurt', 'ediblebyvine', 'content_id']


class Tile:

    def apply_tile_settings(self, tile_data):
        """
        Copies the values of tkinter variables from tile_data to this object's data.
        :param tile_data: The data to copy
        :return: None
        """
        for k in defaults.keys():
            self.data[k] = tile_data[k].get()

    def configure_bounding_box(self, **kwargs):
        """
        Apply configuration changes to the tile's bounding box.
        :param kwargs: Settings to apply to the bounding box. Accepts any named arguments that can be passed to
        tkinter.Canvas.itemconfigure
        :return: None
        """
        self.canvas.itemconfigure(self.bounding_box, **kwargs)

    def _scale_poly(self, poly, scale):
        """Scales any object drawn on the canvas"""
        canvas = self.canvas

        new_pts = []
        for pt in canvas.coords(poly):
            new_pts.append(pt / self.scale * scale)

        canvas.coords(poly, *new_pts)

    def set_scale(self, scale):
        """
        Set the scaling of the tile to <scale>
        :param scale: The desired scale amount
        :return: None
        """
        if scale != self.scale:
            self._scale_poly(self.bounding_box, scale)
            self.canvas.delete(self.type_poly)
            self.type_poly = self.draw_type()
            self.scale = scale

    def increment_bad_field_count(self):
        self.bad_field_count += 1
        if self.bad_field_count == 1:
            self.redraw()

    def decrement_bad_field_count(self):
        self.bad_field_count = max(self.bad_field_count - 1, 0)
        if self.bad_field_count == 0:
            self.redraw()

    def draw_type(self, tile_type=None, collision_type=None, **kwargs):
        """Draw a little picture showing the Tile's type"""
        tile_data = self.data
        tile_type = tile_type or tile_data['tile_type']
        collision_type = 'Passthrough' if tile_type == 'BGO' else collision_type or tile_data['collision_type']
        canvas = self.canvas
        (x1, y1, x2, y2) = self.canvas.coords(self.bounding_box)

        poly = tile_draw_functions[collision_type](canvas, x1, y1, x2, y2)
        kwargs.pop('outline', None)
        kwargs.pop('width', None)

        canvas.itemconfigure(poly, outline=self.color, width=self.border_width, fill='', **kwargs)

        return poly

    def draw_error_indicator(self):
        canvas = self.canvas

        if self.error_indicator is not None:
            canvas.delete(self.error_indicator)

        (x, y, *_) = canvas.coords(self.bounding_box)
        return canvas.create_image(x + 1, y + 1, anchor=NW, image=self.error_image, tags='bad_ind')

    def redraw(self, **tile_data):
        """Redraw the Tile"""
        data = self.data
        canvas = self.canvas
        tile_type = None
        collision_type = None
        scale = None
        color = None

        if 'tile_type' in tile_data:
            tile_type = tile_data['tile_type']
        if 'collision_type' in tile_data:
            collision_type = tile_data['collision_type']
        if 'scale' in tile_data:
            scale = tile_data['scale']
        if 'highlight_color' in tile_data:
            color = tile_data['highlight_color']

        if (tile_type and tile_type != data['tile_type']) \
                or collision_type and (collision_type != data['collision_type']):
            # Tile type or collision type has changed.
            canvas.delete(self.type_poly)
            self.type_poly = self.draw_type(tile_type, collision_type)

            if tile_type:
                data['tile_type'] = tile_type
            if collision_type:
                data['collision_type'] = collision_type

        if scale and scale != self.scale:  # Scale has changed.
            self.set_scale(scale)

            self.scale = scale

        outline = (color or self.color) if self.selected else ''
        canvas.itemconfigure(self.bounding_box, outline=outline)
        if color and color != self.color:  # Highlight Color has changed.
            canvas.itemconfigure(self.type_poly, outline=color)

            self.color = color

        self.error_indicator = self.draw_error_indicator()
        if self.bad_field_count > 0:
            self.canvas.itemconfigure(self.error_indicator, state=NORMAL)
        else:
            self.canvas.itemconfigure(self.error_indicator, state=HIDDEN)

        # Ensure that the tile is always rendered above the grid.
        # highest_above = canvas.find_above(self.bounding_box)
        canvas.tag_raise(self.bounding_box)
        canvas.tag_raise(self.type_poly)
        canvas.tag_raise(self.error_indicator)

    def select(self):
        self.selected = True
        self.redraw()

    def deselect(self):
        self.selected = False
        self.redraw()

    def overlaps(self, bbox):
        """
        Check whether <bbox> overlaps with <self.bounding_box>.
        :param bbox: The bounding box to check. This must be in <self.canvas>, or a TclError exception will be raised.
        :return: True if there is an overlap, False otherwise.
        """
        (sx1, sy1, sx2, sy2) = self.canvas.coords(self.bounding_box)
        (ox1, oy1, ox2, oy2) = self.canvas.coords(bbox)
        return sx2 > ox1 and sx1 < ox2 and sy2 > oy1 and sy1 < oy2

    @staticmethod
    def _collect_non_default_data(keys, data, save_data):
        """
        Collect the non-default data values stored at <data>[<keys>] into <save_data>
        :param keys: The keys to check and possibly copy over
        :param data: All the Tile's data
        :param save_data: The data that will be encoded to .json and written to the save file
        :return:
        """
        for k in keys:
            if data[k] != defaults[k]:
                save_data[k] = data[k]

    def load_to_ui(self, ui_data, ui_inputs):
        """Load the Tile's data to the UI"""
        data = self.data
        for k in data:
            ui_data[k].set(data[k])
            if k in ui_inputs:
                ui_inputs[k].check_variable()

    def get_save_ready_data(self):
        """
        Convert the tile's data into a dict object that is ready to be written to a .json file
        :return: A dict containing all non-default configurations.
        """
        data = self.data
        save_data = {}

        (x1, y1, x2, y2) = self.canvas.coords(self.bounding_box)
        save_data['x1'] = int(x1)
        save_data['y1'] = int(y1)
        save_data['x2'] = int(x2)
        save_data['y2'] = int(y2)

        self._collect_non_default_data(unconditional_settings, data, save_data)
        if data['light_source']:
            self._collect_non_default_data(light_settings, data, save_data)
        if data['tile_type'] == 'Block':
            self._collect_non_default_data(block_settings, data, save_data)
            if data['content_type'] != 'Empty':
                self._collect_non_default_data(content_settings, data, save_data)
        else:
            self._collect_non_default_data(bgo_settings, data, save_data)

        if 'assigned_id' in data:
            save_data['assigned_id'] = data['assigned_id']

        return save_data

    def assign_id(self, generated_id):
        """
        Assigns an ID to the Tile.
        :param generated_id: The ID that will be assigned to the tile if the user did not provide one.
        :return: The ID assigned.
        """
        data = self.data
        if 'assigned_id' not in data:
            data['assigned_id'] = int(data['id']) if data['id'] != '' else generated_id
        return data['assigned_id']

    def export(self):
        """Export the tile to png, txt and ini files for use in SMBX2."""

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __init__(self, canvas, x1, y1, x2, y2, *, outline=None, width=None, scale=1, **kwargs):
        """
        CONSTRUCTOR
        :param canvas: The canvas that the tile will be drawn to
        :type canvas: tkinter.Canvas
        :param x1: The left boundary of the tile
        :param y1: The top boundary of the tile
        :param x2: The right boundary of the tile
        :param y2: The bottom boundary of the tile
        :param kwargs: Settings to apply to the bounding box. Accepts any named arguments that can be passed to
        tkinter.Canvas.itemconfigure
        """
        self.error_image = PhotoImage(file='data/tile_error.png')

        data = {}
        for k in defaults.keys():
            if k in kwargs:
                data[k] = kwargs[k]
                del kwargs[k]  # Remove the key so it won't be passed on to the Canvas items and cause an error
            else:
                data[k] = defaults[k]
        self.data = data

        self.color = outline or 'black'
        self.border_width = width or 3
        self.canvas = canvas

        self.scale = scale
        self.selected = False

        self.bounding_box = canvas.create_rectangle(x1, y1, x2, y2, outline=self.color, width=self.border_width,
                                                    **kwargs)
        self.type_poly = self.draw_type(outline=self.color, width=self.border_width, **kwargs)

        self.bad_field_count = 0
        self.error_indicator = None
        self.error_indicator = self.draw_error_indicator()

    def __del__(self):
        canvas = self.canvas

        canvas.delete(self.bounding_box)
        canvas.delete(self.type_poly)
