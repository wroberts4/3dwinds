# -*- mode: python -*-
import os


block_cipher = None

collect_list = []
for func in (['open_docs', 'area', 'velocity', 'wind_info', 'vu', 'displacements', 'lat_long']):
    a = Analysis([os.path.join('..', 'pywinds', func + '.py')])
    pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
    exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name=func)
    collect_list.extend([exe, a.binaries, a.zipfiles, a.datas])
COLLECT(*collect_list, name='pywinds')
