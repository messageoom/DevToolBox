# -*- mode: python ; coding: utf-8 -*-

# DevToolBox 后端打包配置
a = Analysis(
    ['backend/app.py'],
    pathex=['backend'],
    binaries=[],
    datas=[
        ('backend/templates', 'templates'),
        ('backend/static', 'static'),
        ('uploads', 'uploads'),
        ('frontend/dist', 'frontend/dist'),
    ],
    hiddenimports=[
        'modules.file_upload',
        'modules.json_tools',
        'modules.yaml_tools',
        'modules.markdown_tools',
        'modules.base64_tools',
        'modules.hash_tools',
        'modules.url_tools',
        'modules.timestamp_tools',
        'flask_cors',
        'yaml',
        'markdown',
        'bcrypt',
        'pytz',
        'tzlocal',
        'bs4',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DevToolBox',
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
