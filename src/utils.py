import os
import sys
import datetime

def utc_to_local_str(utc_dt_str: str) -> str:
    """Converts a UTC datetime string from DB to a local formatted string."""
    if not utc_dt_str:
        return "-"
    
    try:
        # DB stores as "YYYY-MM-DD HH:MM:SS" (microseconds optional)
        if "." in utc_dt_str:
            utc_dt = datetime.datetime.strptime(utc_dt_str, "%Y-%m-%d %H:%M:%S.%f")
        else:
            utc_dt = datetime.datetime.strptime(utc_dt_str, "%Y-%m-%d %H:%M:%S")
        
        # Add UTC timezone info
        utc_dt = utc_dt.replace(tzinfo=datetime.timezone.utc)
        
        # Convert to local time
        local_dt = utc_dt.astimezone()
        
        return local_dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return utc_dt_str

def open_file_picker():
    """Opens a file selection dialog and returns the selected file path."""
    if sys.platform == 'win32':
        return _open_file_picker_win32()
    else:
        # Fallback for other platforms or if we implemented them
        return input("Please enter the file path manually: ").strip()

def _open_file_picker_win32():
    import ctypes
    from ctypes import wintypes
    
    # Structure definition for OPENFILENAME
    class OPENFILENAME(ctypes.Structure):
        _fields_ = [
            ("lStructSize", wintypes.DWORD),
            ("hwndOwner", wintypes.HWND),
            ("hInstance", wintypes.HINSTANCE),
            ("lpstrFilter", wintypes.LPCWSTR),
            ("lpstrCustomFilter", wintypes.LPWSTR),
            ("nMaxCustFilter", wintypes.DWORD),
            ("nFilterIndex", wintypes.DWORD),
            ("lpstrFile", wintypes.LPWSTR),
            ("nMaxFile", wintypes.DWORD),
            ("lpstrFileTitle", wintypes.LPWSTR),
            ("nMaxFileTitle", wintypes.DWORD),
            ("lpstrInitialDir", wintypes.LPCWSTR),
            ("lpstrTitle", wintypes.LPCWSTR),
            ("Flags", wintypes.DWORD),
            ("nFileOffset", wintypes.WORD),
            ("nFileExtension", wintypes.WORD),
            ("lpstrDefExt", wintypes.LPCWSTR),
            ("lCustData", wintypes.LPARAM),
            ("lpfnHook", wintypes.LPVOID),
            ("lpTemplateName", wintypes.LPCWSTR),
            ("pvReserved", wintypes.LPVOID),
            ("dwReserved", wintypes.DWORD),
            ("FlagsEx", wintypes.DWORD),
        ]

    file_buffer = ctypes.create_unicode_buffer(32768)
    
    ofn = OPENFILENAME()
    ofn.lStructSize = ctypes.sizeof(OPENFILENAME)
    ofn.lpstrFile = ctypes.cast(file_buffer, wintypes.LPWSTR)
    ofn.nMaxFile = 32768
    ofn.lpstrFilter = "All Files\0*.*\0\0"
    ofn.nFilterIndex = 1
    ofn.lpstrTitle = "Select a file for your workspace"
    ofn.Flags = 0x00000800 | 0x00001000  # OFN_PATHMUSTEXIST | OFN_FILEMUSTEXIST

    if ctypes.windll.comdlg32.GetOpenFileNameW(ctypes.byref(ofn)):
        return file_buffer.value
    return None
