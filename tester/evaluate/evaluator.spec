# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['evaluator_linuxtool.py'],
    pathex=['/media/yangyh408/YangYH408/onsite-test-server/tester/evaluate'],
    binaries=[],
    datas=[('/media/yangyh408/YangYH408/onsite-test-server/tester/evaluate/server_v3', './server_v3'), ('/media/yangyh408/YangYH408/onsite-test-server/tester/evaluate/ramp', './ramp')],
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
