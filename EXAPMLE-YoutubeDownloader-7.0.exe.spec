# -*- mode: python -*-

block_cipher = None


a = Analysis(['<Path_To_python_script>'],
             pathex=['C:\\Users\\<UserName>\\AppData\\Local\\Programs\\Python\\Python35'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
 

import os

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
		  Tree('<path_to_avconv*_binaries>', prefix='binaries\\'),
          a.zipfiles,
          a.datas,
          name='YoutubeDownloader-7.0.exe',
          debug=False,
          strip=False,
          upx=True,
          console=False )