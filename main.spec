# -*- mode: python -*-

block_cipher = None

def get_pandas_path():
    import pandas
    pandas_path = pandas.__path__[0]
    return pandas_path
	
a = Analysis(['main.py'],
             pathex=['E:\\huobi\\Huobi'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

 
dict_tree = Tree(get_pandas_path(), prefix='pandas', excludes=["*.pyc"])
a.datas += dict_tree
a.binaries = filter(lambda x: 'pandas' not in x[0], a.binaries)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='DDURobert',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False, icon='favicon.ico' )
		  
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='DDURobert')