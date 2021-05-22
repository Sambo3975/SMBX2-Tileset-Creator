# SMBX2 Tileset Importer

## About

This program streamlines the creation of tilesets in SMBX2 by automating the most tedious parts of the process:
- Cutting the image with all your tiles into individual block-*.png images.
- Finding IDs for all the images
- Creating the .tileset.ini file in PGE.

This program was designed for Windows and may not work right on other platforms. I figured this would be fine since
SMBX doesn't run on anything but Windows (or Wine) anyway.

## Installation

### Official Release

The current release of this software is available as a Windows executable 
[here](https://github.com/Sambo3975/SMBX2-Tileset-Creator/releases). That page also includes documentation of the 
software's features.

### Build it Yourself

_Note: If you build the software yourself, do not report bugs or errors from your build. They will be ignored._

If you want to test the software on another platform, or you want to test unreleased features, you can build it
yourself. To do this, do the following:

1. Clone this repository to your local machine:

```git clone Sambo3975/SMBX2-Tileset-Creator```

2. Open a console in the root directory of the repo and execute the following command:

```pyinstaller main.spec```

3. The compiled executable will be created in a subdirectory named `dist`.

Alternatively, you can open your local copy of the repo with PyCharm and run it from there.
