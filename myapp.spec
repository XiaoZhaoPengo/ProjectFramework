# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules

# 收集隐藏导入模块
hiddenimports = [
    'case.web_demo.test_zzy_business',
    'case.web_demo.__init__',
    'case.__init__',
    'case.conftest',
    'case.pageobj.adminBusiness',
    'common.common',
    'common.reda_data',
    'common.web_base',
    'common.driver_init',
    'common.app_base',
    'common.__init__',
    'config.__init__',
]

hiddenimports += collect_submodules('case')
hiddenimports += collect_submodules('common')
hiddenimports += collect_submodules('config')

# 定义资源文件路径，仅包含数据文件和必要的资源文件
datas = [
    ('config/setting.yaml', 'config'),
    ('database/caseYAML/test_zzy_business.yaml', 'database/caseYAML'),
    ('database/locatorYAML/adminBusiness.yaml', 'database/locatorYAML'),
    ('driver/windos/chromedriver.exe', 'driver/windos'),
    ('logs', '.'),  # 如果 log 是一个目录，保留
    ('LegalFile', 'LegalFile'),  # 添加 LegalFile 目录
    ('pytest.ini', '.'),  # 配置文件
    ('requirements.txt', '.'),  # 配置文件
    ('zzyLogo.ico', '.'),
]

# 如果需要包含其他数据文件，请按需添加

# 创建 Analysis 对象
a = Analysis(
    ['main.py'],
    pathex=['E:/zzybusiness/pythonProject'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False, # 设置为 True 以避免使用 zip 文件打包
    optimize=0,
)

# 创建 PYZ 对象
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 创建 EXE 对象
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='myapp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI 程序无需控制台
    windowed=True, # 隐藏命令行窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='zzyLogo.ico',
)

# 创建 COLLECT 对象
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='myapp'
)
