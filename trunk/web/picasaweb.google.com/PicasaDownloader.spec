a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), 'getcontent.py', 'picasa.py'],
             pathex=['D:\\Develop\\picasa-album-download\\trunk\\src'])
pyz = PYZ(a.pure)
exe = EXE( pyz,
          a.scripts,
          a.binaries,
          name='PicasaDownloader.exe',
          debug=False,
          strip=False,
          upx=False,
          console=True )
