import sys
from cx_Freeze import setup, Executable

# Dependencies
build_exe_options = {
    "packages": ["pygame", "os", "random", "math", "numpy"],
    "include_files": ["assets/", "src/"]
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Use this to hide console on Windows

setup(
    name="Snake Game",
    version="1.0",
    description="Realistic Snake Game",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, icon="assets/images/snake_logo.ico" if sys.platform == "win32" else None)]
) 