# SMBX2 Tileset Importer

_Note: This software is currently in Beta. If you experience any errors or bugs, please report them
[here](https://github.com/Sambo3975/SMBX2-Tileset-Creator/issues/new?assignees=&labels=&template=bug_report.md&title=)._

## About

This program streamlines the creation of tilesets for SMBX2 and TheXTech by automating the most tedious parts of the process:
- Cutting the image with all your tiles into individual block-*.png images.
- Finding IDs for all the images.
- Creating the `.tileset.ini` file for the Moondust Editor (former PGE Editor).

This program was originally designed for Windows, however it also can work on Linux if you will install all necessary
python3 packages. If you want to try to use it on another platform or test unreleased features, feel free to build it yourself.

This program also has limited support for [TheXTech project](https://github.com/Wohlstand/TheXTech/wiki), the enhanced
cross-platform port of the SMBX 1.3. It has support for PNG sprites and has the full native support by the standalone
Moondust Editor, including direct level testing. However, it doesn't support any config files to
customize settings for blocks and BGOs yet and keeps using the same itemset as SMBX 1.3 had with reserved blocks
and BGO entries.

## Installation

### On Windows
Get the current release [here](https://github.com/Sambo3975/SMBX2-Tileset-Creator/releases).

### On Linux
This program can work on Linux-based operating systems. It requires Python 3.8+.

If you have the Debian-based distribution, you need to install these dependencies to get the program to work:
```bash
sudo apt install tix-dev python3-tk python3-regex python3-pil python3-pip
sudo -H pip3 install pathvalidate
```

Then, clone this repository into any convenient directory and try to run the `main.py` script to start the program.


## How to Use

When you launch this software, you should see the following:

![Imgur](https://imgur.com/rX7aQL9.png)

Go ahead and open your tileset image to get started.

### View and Export Settings

Once you've opened your image, you should see the following. The image shown here includes a test tileset that I made.

![Imgur](https://imgur.com/sy6Ch2m.png)

You can now configure the tileset using the options on the left panel. Refer to the tooltips in the software for more
information about each option. Options that have bad values will be marked with a warning icon (⚠).

### Tile Interactions

The software allows you to interact with tiles in the following ways.

#### Creating a New Tile

To create a new tile, left-click and drag over the area of the image you want the tile to occupy. The edges of your
selection will automatically snap to the grid. When you release the mouse button, a new tile will be created. You can
then edit that tile's settings in the right panel. Note that tiles may not overlap. If your selection overlaps with an
existing tile, a new tile will not be created.

#### Selecting a Tile

To select a tile, simply left-click somewhere within it. Its settings will then be loaded and can be edited.

#### Editing a tile.

When editing a tile, any field with a bad value will be marked with a warning icon (⚠). Any tiles with bad field values
will be marked in the same way.

#### Deleting a Tile

If you made a mistake when creating a tile, such as making it the wrong size, you can delete the tile by right-clicking
it and selecting Delete in the context menu.

### Saving the Tileset

To save the tileset, go to File->Save or press Ctrl + S. This will create a file with the same name as your tileset
image, but with the extension `.tileset.json`, that contains all the tileset's data. You can save the tileset even if
some settings or tile fields have bad values, but you will not be able to export a tileset with bad values.

_Note: Do not edit the `.tileset.json` file in a text editor. It is quite easy to break the software this way. Editing
the tileset only in the software ensures that the file is changed in ways that are safe. Do not report errors or bugs
caused by hand-editing this file, as they will be ignored._

### Exporting the Tileset

To export the tileset, go to File->Export or press Ctrl + E. This will create a directory with the same name as your
tileset image and fill it with several .png and .txt files, as well as up to two .tileset.ini files if you have chosen
to create Moondust Editor tilesets. Copy and paste the contents of this folder to the folder of the level you wish to use the tiles
in.

This process will also assign IDs to all unassigned blocks and lock these IDs in place. This ensures that all existing
tiles will keep the same ID in future exports, even if tiles are added or deleted from the tileset. If, for whatever
reason, you want to re-assign the automatically-generated IDs, you can clear the assigned IDs from File->Clear
Auto-Assigned IDs. This will not clear IDs that you manually assigned to individual tiles.

If the export is successful, you will see a message like the one below.

![Imgur](https://imgur.com/2pcext2.png)

#### Export Failures

If the tileset has any bad setting values, a warning describing the problem will be displayed, and the exporting process
will be aborted. The different warning messages and resolutions to them are described below.

![Imgur](https://imgur.com/QDMuLMd.png)

`n invalid tileset settings` -- This indicates that `n` of the settings for the tileset have bad values. Check the left
panel and correct any settings that are marked with warning icons (⚠), then try again.

`n tiles with invalid settings` -- This indicates that `n` tiles are not configured properly. To resolve this, check all
tiles that are marked with warning icons (⚠) and correct any settings that are marked in the same way.

![Imgur](https://imgur.com/kLdf1g3.png)

This indicates that you have not allocated enough IDs for all tiles that are set to have their IDs automatically
assigned. To resolve this, either add more IDs to the indicated ID pool on the left panel, or specify IDs for more
tiles (using the Tile ID field on the right panel), then try again.

#### Note about Editor tilesets

The software will try to arrange the tiles in Moondust Editor tilesets as closely to their arrangement in the image as possible.
However, this is not always possible if tiles are of differing sizes. You may wish to make some minor adjustments to
the tileset in Moondust Editor after you export.

## Known Issues

* Clicking Cancel on a color selector causes a crash.
* Entering a non-integer value in Grid Size or Pixel Scale causes a crash.
* The Lava and P-Switch-able options show the wrong tooltips.

## Features Planned for Future Releases

The following features are planned for future releases. You can request a new feature [here](https://github.com/Sambo3975/SMBX2-Tileset-Creator/issues/new?assignees=&labels=&template=feature_request.md&title=). Approved feature requests will be added to this section.

### General Features

* A scrollbar for large tileset images.

### Tileset Configurations

**Name** -- The name the tileset will have in Moondust Editor. This will also affect the name of the
`.tileset.ini` file itself. If not specified, the tileset will be named 'Imported (Block/BGO) Tileset'

### Grid Configurations

**Padding** -- Adds gaps between grid squares (tileset creators commonly place a 1 or 2 px gap between
tiles)

**Offsets** -- Horizontal and vertical offsets for the grid

### Tile Configurations

**Name** -- The name the tile will have in Moondust Editor. The tile's name will be something like 'Imported Tile' if not defined.

**Description** -- The description the tile will have in Moondust Editor. This will be empty if not defined.

### Placement Modes

**Single Tile** -- The only placement mode available in this release. Places a single tile in the selected area.

**Multi 1x1** -- Places multiple tiles in the selected area that occupy a 1x1 square in the grid. The selected area may
overlap with other tiles when this is used (but no tiles will be placed that overlap others).

### Impute Tile Collision Types

This will be separate from placement modes. The software will attempt to impute the collision type of new tiles
from the image data in the selected area. This will be toggleable. This may not be included if it cannot be done
efficiently.

### Multi-edit

Select multiple tiles with the selector and edit all at once. Fields that differ between the tiles will be blanked.
Writing to a blanked field will still apply the change to all tiles. Don't know if this is really worth the effort.
