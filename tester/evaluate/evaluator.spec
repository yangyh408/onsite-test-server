# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['evaluator.py'],
    pathex=['/media/yangyh408/YANGYH408/evaluator_exe'],
    binaries=[],
    datas=[('/media/yangyh408/YANGYH408/evaluator_exe/server_v3', './server_v3'), ('/media/yangyh408/YANGYH408/evaluator_exe/ramp', './ramp')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='evaluator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
