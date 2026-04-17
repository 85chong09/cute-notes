import sys
from cx_Freeze import setup, Executable

# 依赖包
build_exe_options = {
    "packages": ["PyQt5", "sys", "json", "os", "datetime"],
    "includes": [],
    "excludes": [],
    "include_files": [],
    "optimize": 2
}

# 基础设置
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # 不显示控制台窗口

setup(
    name="可爱便签",
    version="1.0.0",
    description="一个可爱的Windows桌面便签工具",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",
            base=base,
            target_name="可爱便签.exe",
            icon=None  # 可以添加图标文件
        )
    ]
)
