# -*- mode: python ; coding: utf-8 -*-

import pathlib
import sys

block_cipher = None

path = pathlib.Path().absolute();

a = Analysis(['main.py'],
             pathex=[path],
             binaries=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

if sys.platform == "darwin":
    a.datas += [('data/icon.icns', 'data/icon.icns', 'DATA')]

if sys.platform == "win32":
    a.datas += [('data/icon.ico', 'data/icon.ico', 'DATA')]
else:
    a.datas += [('data/icon_32.png', 'data/icon_32.png', 'DATA')]

a.datas += [('data/tile_error.png', 'data/tile_error.png', 'DATA')]

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='SMBX2 Tileset Importer',
          icon='data/icon.ico',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False)

if sys.platform == "darwin":
    app = BUNDLE(exe,
            name='SMBX2 Tileset Importer.app',
            icon='data/icon.icns',
            bundle_identifier='SMBX2 Tileset Importer',
            version='0.1.2',
            info_plist={
                'NSPrincipalClass': 'NSApplication',
                'NSAppleScriptEnabled': False,
            }
        )
