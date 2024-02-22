import sys
from cx_Freeze import setup, Executable
from src.rosinenpicker.start import __version__

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "excludes": ["pdfs/", "configs/", "testconfigs/", ".github/", "helper/", "dumpster/", "*.bat", "test"],
}

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="rosinenpicker",
    version=__version__,
    description="A package for picking the juciest text morsels out of a pile of documents.",
    options={"build_exe": build_exe_options},
    executables=[Executable("src/rosinenpicker/start.py", base=base)],
)

