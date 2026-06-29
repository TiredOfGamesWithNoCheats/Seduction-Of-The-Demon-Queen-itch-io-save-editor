"""
main.py
Entry point for the SOTDQ Save Editor.
"""

import ctypes
import os
import customtkinter as ctk
from ui import SaveEditorGUI


def _disable_efficiency_mode():
    # Windows 11 auto-places Python processes in EcoQoS (efficiency mode).
    # Set NORMAL priority so the UI stays responsive.
    try:
        PROCESS_ALL_ACCESS   = 0x1F0FFF
        NORMAL_PRIORITY      = 0x00000020
        handle = ctypes.windll.kernel32.OpenProcess(
            PROCESS_ALL_ACCESS, False, os.getpid()
        )
        ctypes.windll.kernel32.SetPriorityClass(handle, NORMAL_PRIORITY)
        ctypes.windll.kernel32.CloseHandle(handle)
    except Exception:
        pass


def main():
    _disable_efficiency_mode()
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    app = SaveEditorGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
