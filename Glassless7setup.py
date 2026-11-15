# -*- coding: utf-8 -*-
import ctypes, time, os, sys, json
from ctypes import wintypes
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk

if sys.executable.lower().endswith("python.exe"):
    pythonw = sys.executable[:-10] + "pythonw.exe"
    if os.path.exists(pythonw):
        os.spawnv(os.P_NOWAIT, pythonw, [pythonw] + sys.argv)
        sys.exit(0)

console_hwnd = ctypes.windll.kernel32.GetConsoleWindow()
if console_hwnd:
    ctypes.windll.user32.ShowWindow(console_hwnd, 0)

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

DWMWA_USE_IMMERSIVE_DARK_MODE, DWMWA_WINDOW_CORNER_PREFERENCE, DWMWCP_ROUNDSMALL = 20, 33, 3
DWMWA_BORDER_COLOR, DWMWA_CAPTION_COLOR, DWMWA_TEXT_COLOR = 34, 35, 36
DWMWA_CLOAKED, DWMWA_EXTENDED_FRAME_BOUNDS = 14, 9
DWMWA_COLOR_DEFAULT = 0xFFFFFFFF

GWL_STYLE, GWL_EXSTYLE, GWLP_WNDPROC = -16, -20, -4
WS_CAPTION, WS_CHILD = 0x00C00000, 0x40000000
WS_MINIMIZEBOX, WS_MAXIMIZEBOX = 0x00020000, 0x00010000
WS_EX_TRANSPARENT, WS_EX_LAYERED, WS_EX_NOACTIVATE, WS_EX_TOOLWINDOW = 0x20, 0x80000, 0x8000000, 0x80

SWP_NOSIZE, SWP_NOMOVE, SWP_NOACTIVATE = 0x1, 0x2, 0x10
VK_LBUTTON, VK_CONTROL, VK_SHIFT, VK_MENU = 0x1, 0x11, 0x10, 0x12
RGN_DIFF, LWA_ALPHA = 4, 0x2

WM_USER = 0x0400
WM_TRAYICON = WM_USER + 20
WM_LBUTTONUP, WM_LBUTTONDBLCLK, WM_RBUTTONUP = 0x0202, 0x0203, 0x0205
NIM_ADD, NIM_DELETE = 0x0, 0x2
NIF_MESSAGE, NIF_ICON, NIF_TIP = 0x1, 0x2, 0x4

WP_MINBUTTON, WP_MAXBUTTON, WP_RESTOREBUTTON, WP_CLOSEBUTTON = 15, 17, 21, 18
STATE_NORMAL, STATE_HOT, STATE_PUSHED = 1, 2, 3

SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "aero7_config.json")

MODIFIER_MAP = {
    "Ctrl + Shift": (VK_CONTROL, VK_SHIFT),
    "Ctrl + Alt": (VK_CONTROL, VK_MENU),
    "Alt + Shift": (VK_MENU, VK_SHIFT)
}

KEY_OPTIONS = [chr(c) for c in range(ord("A"), ord("Z") + 1)] + [str(d) for d in range(0, 10)]

IGNORED_CLASSES = {
    "Shell_TrayWnd", "Shell_SecondaryTrayWnd", "Progman", "WorkerW",
    "Windows.UI.Core.CoreWindow", "XamlExplorerHostIslandWindow",
    "TopLevelWindowForOverflowXamlIsland", "NotifyIconOverflowWindow",
    "ForegroundStaging", "ApplicationManager_DesktopShellWindow",
    "MsoSplash", "NUIDialog", "Net UI Tool Window", "SearchPane"
}

OFFICE_CLASSES = {"OpusApp", "XLMAIN", "PPTFrameClass", "rctrl_renwnd32"}
TERMINAL_CLASSES = {"CASCADIA_HOSTING_WINDOW_CLASS", "ConsoleWindowClass"}
NO_BLUE_CAPTION_CLASSES = {
    "Notepad", "CabinetWClass", "Chrome_WidgetWin_1",
    "ApplicationFrameWindow", "WinUIDesktopWin32WindowClass"
} | OFFICE_CLASSES | TERMINAL_CLASSES
class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG), ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD), ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD), ("biXPelsPerMeter", wintypes.LONG), ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD), ("biClrImportant", wintypes.DWORD)
    ]

class NOTIFYICONDATAW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD), ("hWnd", wintypes.HWND), ("uID", wintypes.UINT),
        ("uFlags", wintypes.UINT), ("uCallbackMessage", wintypes.UINT), ("hIcon", wintypes.HICON),
        ("szTip", wintypes.WCHAR * 128), ("dwState", wintypes.DWORD), ("dwStateMask", wintypes.DWORD),
        ("szInfo", wintypes.WCHAR * 256), ("uVersion", wintypes.UINT), ("szInfoTitle", wintypes.WCHAR * 64),
        ("dwInfoFlags", wintypes.DWORD)
    ]

user32, gdi32, dwmapi, uxtheme, shell32 = ctypes.windll.user32, ctypes.windll.gdi32, ctypes.windll.dwmapi, ctypes.windll.uxtheme, ctypes.windll.shell32

LRESULT = ctypes.c_ssize_t
WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

dwmapi.DwmSetWindowAttribute.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
dwmapi.DwmGetWindowAttribute.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
uxtheme.OpenThemeData.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
uxtheme.OpenThemeData.restype = wintypes.HANDLE
uxtheme.DrawThemeBackground.argtypes = [wintypes.HANDLE, wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.POINTER(RECT), ctypes.POINTER(RECT)]
uxtheme.CloseThemeData.argtypes = [wintypes.HANDLE]
user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
user32.GetWindowLongW.restype = wintypes.LONG
user32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.LONG]
user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint]
user32.SetWindowRgn.argtypes = [wintypes.HWND, wintypes.HRGN, wintypes.BOOL]
user32.SetLayeredWindowAttributes.argtypes = [wintypes.HWND, wintypes.COLORREF, wintypes.BYTE, wintypes.DWORD]
gdi32.CreateRectRgn.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
gdi32.CreateRectRgn.restype = wintypes.HRGN
gdi32.CombineRgn.argtypes = [wintypes.HRGN, wintypes.HRGN, wintypes.HRGN, ctypes.c_int]
gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
user32.GetAsyncKeyState.restype = wintypes.SHORT
shell32.Shell_NotifyIconW.argtypes = [wintypes.DWORD, ctypes.POINTER(NOTIFYICONDATAW)]
user32.CallWindowProcW.argtypes = [ctypes.c_void_p, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.CallWindowProcW.restype = LRESULT

if hasattr(user32, "SetWindowLongPtrW"):
    user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_void_p]
    user32.SetWindowLongPtrW.restype = ctypes.c_void_p
    set_wndproc = user32.SetWindowLongPtrW
else:
    user32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_void_p]
    user32.SetWindowLongW.restype = ctypes.c_void_p
    set_wndproc = user32.SetWindowLongW

def get_dpi_scale():
    try:
        hdc = user32.GetDC(0)
        dpi = gdi32.GetDeviceCaps(hdc, 88)
        user32.ReleaseDC(0, hdc)
        return dpi / 96.0 if dpi > 0 else 1.0
    except Exception:
        return 1.0

def load_config():
    default_cfg = {
        "toggle_mod": "Ctrl + Shift",
        "toggle_key": "A",
        "exit_mod": "Ctrl + Alt",
        "exit_key": "Q",
        "start_active": True
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                default_cfg.update(data)
        except Exception:
            pass
    return default_cfg

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass
def extract_windows_button_texture(hwnd, part_id, state_id, w, h, bg_color=0x00EAD1B9):
    htheme = uxtheme.OpenThemeData(hwnd, "WINDOW")
    hdc_screen = user32.GetDC(0)
    hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
    bmi = BITMAPINFOHEADER()
    bmi.biSize, bmi.biWidth, bmi.biHeight, bmi.biPlanes, bmi.biBitCount = ctypes.sizeof(BITMAPINFOHEADER), w, -h, 1, 32
    bits = ctypes.c_void_p()
    hbmp = gdi32.CreateDIBSection(hdc_mem, ctypes.byref(bmi), 0, ctypes.byref(bits), None, 0)
    old_bmp = gdi32.SelectObject(hdc_mem, hbmp)
    rc = RECT(0, 0, w, h)
    brush = gdi32.CreateSolidBrush(bg_color)
    user32.FillRect(hdc_mem, ctypes.byref(rc), brush)
    gdi32.DeleteObject(brush)
    if htheme:
        uxtheme.DrawThemeBackground(htheme, hdc_mem, part_id, state_id, ctypes.byref(rc), None)
        uxtheme.CloseThemeData(htheme)
    buf_size = w * h * 4
    buf = (ctypes.c_ubyte * buf_size)()
    ctypes.memmove(buf, bits, buf_size)
    img = Image.frombuffer("RGBA", (w, h), bytes(buf), "raw", "BGRA", 0, 1).convert("RGB")
    gdi32.SelectObject(hdc_mem, old_bmp)
    gdi32.DeleteObject(hbmp)
    gdi32.DeleteDC(hdc_mem)
    user32.ReleaseDC(0, hdc_screen)
    return img

def apply_win7_aero_gloss(base_img, btn_type, state):
    w, h = base_img.size
    img = base_img.convert("RGBA")
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    half_h = h // 2
    if state in ("norm", "hot"):
        top_alpha = 95 if state == "hot" else 55
        for y in range(1, half_h):
            alpha = int(top_alpha * (1.0 - (y / half_h)))
            draw.line([(2, y), (w - 3, y)], fill=(255, 255, 255, alpha))
    if state == "hot":
        for y in range(half_h, h - 1):
            progress = (y - half_h) / (h - half_h)
            if btn_type == "close":
                draw.line([(2, y), (w - 3, y)], fill=(255, 195, 65, int(150 * (progress ** 1.4))))
            else:
                draw.line([(2, y), (w - 3, y)], fill=(85, 215, 255, int(150 * (progress ** 1.4))))
    elif state == "pushed":
        if btn_type == "close":
            draw.rectangle([1, 1, w - 2, h - 2], fill=(95, 12, 12, 115))
            for y in range(half_h, h - 1):
                progress = (y - half_h) / (h - half_h)
                draw.line([(2, y), (w - 3, y)], fill=(245, 155, 45, int(160 * (progress ** 1.3))))
        else:
            draw.rectangle([1, 1, w - 2, h - 2], fill=(12, 60, 125, 120))
            for y in range(half_h, h - 1):
                progress = (y - half_h) / (h - half_h)
                draw.line([(2, y), (w - 3, y)], fill=(75, 205, 255, int(155 * (progress ** 1.3))))
        draw.line([(1, 1), (w - 2, 1)], fill=(0, 15, 35, 185))
        draw.line([(1, 2), (w - 2, 2)], fill=(0, 15, 35, 110))
        draw.line([(1, 1), (1, h - 2)], fill=(0, 15, 35, 120))
    if state != "inactive":
        border_alpha = 165 if state == "hot" else (90 if state == "pushed" else 100)
        draw.rectangle([1, 1, w - 2, h - 2], outline=(255, 255, 255, border_alpha))
    draw.rectangle([0, 0, w - 1, h - 1], outline=(55, 78, 105, 130))
    return Image.alpha_composite(img, overlay).convert("RGB")

def apply_aero_cursor_glow(pil_img, btn_type, rel_x_btn):
    try:
        w, h = pil_img.size
        rel_x_btn = max(0, min(w, int(rel_x_btn)))
        glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(glow)
        c0, c1, c2 = (255, 210, 120) if btn_type == "close" else (140, 235, 255)
        radius = max(w // 2, 18)
        for r in range(radius, 2, -2):
            alpha = int(55 * (1.0 - (r / radius)) ** 1.6)
            draw.ellipse([rel_x_btn - r, h - r - 2, rel_x_btn + r, h + r - 2], fill=(c0, c1, c2, alpha))
        return Image.alpha_composite(pil_img.convert("RGBA"), glow).convert("RGB")
    except Exception:
        return pil_img
def create_inactive_close_without_red(close_norm_img, min_norm_img):
    w, h = close_norm_img.size
    neutral_base = min_norm_img.resize((w, h), Image.Resampling.LANCZOS).copy()
    px_close, px_base = close_norm_img.load(), neutral_base.load()
    for y in range(3, h - 3):
        row_color = px_base[4, y]
        for x in range(4, w - 4):
            px_base[x, y] = row_color
    for y in range(4, h - 4):
        for x in range(8, w - 8):
            r, g, b = px_close[x, y]
            if r > 200 and g > 200 and b > 200:
                px_base[x, y] = (245, 248, 252)
            elif r < 110 and g < 110 and b < 110:
                px_base[x, y] = (95, 115, 140)
    return Image.blend(neutral_base, Image.new("RGB", (w, h), (218, 228, 240)), 0.30)

def is_window_eligible(hwnd, overlay_set):
    if not hwnd or hwnd in overlay_set or not user32.IsWindow(hwnd):
        return False
    if not user32.IsWindowVisible(hwnd) or user32.IsIconic(hwnd):
        return False
    cloaked = ctypes.c_int(0)
    dwmapi.DwmGetWindowAttribute(hwnd, DWMWA_CLOAKED, ctypes.byref(cloaked), ctypes.sizeof(cloaked))
    if cloaked.value != 0:
        return False
    class_name = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, class_name, 256)
    cls = class_name.value
    if cls in IGNORED_CLASSES:
        return False
    style = user32.GetWindowLongW(hwnd, GWL_STYLE)
    ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    if cls not in OFFICE_CLASSES and cls != "#32770":
        if not (style & WS_CAPTION) or (style & WS_CHILD) or (ex_style & WS_EX_TOOLWINDOW):
            return False
    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    if (rect.right - rect.left) < 200 or (rect.bottom - rect.top) < 70:
        return False
    return True

def apply_win7_window_style(hwnd, active=True):
    class_name = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, class_name, 256)
    cls = class_name.value

    if not active:
        for attr, val in [
            (DWMWA_WINDOW_CORNER_PREFERENCE, 0),
            (DWMWA_CAPTION_COLOR, DWMWA_COLOR_DEFAULT),
            (DWMWA_BORDER_COLOR, DWMWA_COLOR_DEFAULT),
            (DWMWA_TEXT_COLOR, DWMWA_COLOR_DEFAULT)
        ]:
            v = ctypes.c_int(val)
            dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(v), ctypes.sizeof(v))
        return

    attributes = [(DWMWA_WINDOW_CORNER_PREFERENCE, DWMWCP_ROUNDSMALL)]
    if cls not in NO_BLUE_CAPTION_CLASSES:
        attributes.extend([
            (DWMWA_USE_IMMERSIVE_DARK_MODE, 0),
            (DWMWA_CAPTION_COLOR, 0x00EAD1B9),
            (DWMWA_BORDER_COLOR, 0x00B58D6D),
            (DWMWA_TEXT_COLOR, 0x00000000)
        ])

    for attr, val in attributes:
        v = ctypes.c_int(val)
        dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(v), ctypes.sizeof(v))

class OverlayItem:
    def __init__(self, master, max_w, max_h, chroma_key):
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.configure(bg=chroma_key)
        self.win.wm_attributes("-transparentcolor", chroma_key)
        self.win.withdraw()
        self.win.update_idletasks()

        self.hwnd_ov = user32.GetParent(self.win.winfo_id())
        ex = user32.GetWindowLongW(self.hwnd_ov, GWL_EXSTYLE)
        user32.SetWindowLongW(self.hwnd_ov, GWL_EXSTYLE, ex | WS_EX_TRANSPARENT | WS_EX_LAYERED | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW)

        self.canvas = tk.Canvas(self.win, width=max_w, height=max_h, bg=chroma_key, highlightthickness=0)
        self.canvas.pack()

        self.hover_progress = {"min": 0.0, "max": 0.0, "close": 0.0}
        self.hold_progress = {"min": 0.0, "max": 0.0, "close": 0.0}
        self.captured_btn = None
        self.was_pressed = False
        self.tk_refs = []
        self.visible = False
        self.last_geometry = None
        self.last_visual_state = None
        self.last_clip_regions = None

    def destroy(self):
        try:
            self.win.destroy()
        except Exception:
            pass
class Aero7GlobalManager:
    def __init__(self, config):
        self.config = config
        self.scale = get_dpi_scale()
        self.active = bool(config.get("start_active", True))
        self.running = True
        self.profiles = {
            "classic": {"bw": int(round(45 * self.scale)), "cw": int(round(46 * self.scale)), "h_norm": int(round(30 * self.scale)), "h_max": int(round(23 * self.scale))},
            "dialog": {"bw": int(round(46 * self.scale)), "cw": int(round(47 * self.scale)), "h_norm": int(round(32 * self.scale)), "h_max": int(round(32 * self.scale))},
            "modern": {"bw": int(round(46 * self.scale)), "cw": int(round(47 * self.scale)), "h_norm": int(round(32 * self.scale)), "h_max": int(round(32 * self.scale))},
            "terminal": {"bw": int(round(46 * self.scale)), "cw": int(round(47 * self.scale)), "h_norm": int(round(40 * self.scale)), "h_max": int(round(32 * self.scale))},
            "chrome": {"bw": int(round(50 * self.scale)), "cw": int(round(54 * self.scale)), "h_norm": int(round(40 * self.scale)), "h_max": int(round(41 * self.scale))}
        }

        self.max_w = max(p["bw"] * 2 + p["cw"] for p in self.profiles.values())
        self.max_h = max(max(p["h_norm"], p["h_max"]) for p in self.profiles.values())

        self.root = tk.Tk()
        self.root.withdraw()
        self.chroma_key = "#FF00FF"

        hwnd_desk = user32.GetDesktopWindow()
        self.pil_images = {}
        for prof_name, cfg in self.profiles.items():
            for mode, height in [("max", cfg["h_max"]), ("norm", cfg["h_norm"])]:
                for name, part, width in [
                    ("min", WP_MINBUTTON, cfg["bw"]),
                    ("max", WP_MAXBUTTON, cfg["bw"]),
                    ("rest", WP_RESTOREBUTTON, cfg["bw"]),
                    ("close", WP_CLOSEBUTTON, cfg["cw"])
                ]:
                    raw_norm = extract_windows_button_texture(hwnd_desk, part, STATE_NORMAL, width, height)
                    raw_hot = extract_windows_button_texture(hwnd_desk, part, STATE_HOT, width, height)
                    raw_push = extract_windows_button_texture(hwnd_desk, part, STATE_PUSHED, width, height)
                    self.pil_images[(prof_name, mode, name, "norm")] = apply_win7_aero_gloss(raw_norm, name, "norm")
                    self.pil_images[(prof_name, mode, name, "hot")] = apply_win7_aero_gloss(raw_hot, name, "hot")
                    self.pil_images[(prof_name, mode, name, "pushed")] = apply_win7_aero_gloss(raw_push, name, "pushed")
                    self.pil_images[(prof_name, mode, name, "inactive")] = Image.blend(raw_norm, Image.new("RGB", (width, height), (218, 228, 240)), 0.30)
                self.pil_images[(prof_name, mode, "close", "inactive")] = create_inactive_close_without_red(
                    self.pil_images[(prof_name, mode, "close", "norm")],
                    self.pil_images[(prof_name, mode, "min", "norm")]
                )

        self.overlays = {}
        self.styled_windows = set()
        self.known_windows = set()
        self.fade_animations = {}
        self.tray_hwnd = None
        self.old_wndproc = None
        self.create_tray_icon()

    def get_shortcut_labels(self):
        t_label = f"{self.config['toggle_mod']}+{self.config['toggle_key']}"
        e_label = f"{self.config['exit_mod']}+{self.config['exit_key']}"
        return t_label, e_label

    def create_tray_icon(self):
        self.tray_win = tk.Toplevel(self.root)
        self.tray_win.withdraw()
        self.tray_win.protocol("WM_DELETE_WINDOW", lambda: None)
        self.tray_win.update_idletasks()
        self.tray_hwnd = user32.GetParent(self.tray_win.winfo_id())

        self.menu = tk.Menu(self.tray_win, tearoff=0)
        self.rebuild_tray_menu()

        def tray_wndproc(hwnd, msg, wparam, lparam):
            if msg in (0x0010, 0x0112):
                return 0
            if msg == WM_TRAYICON:
                event = lparam & 0xFFFF
                if event == WM_RBUTTONUP:
                    try:
                        self.menu.unpost()
                        pt = POINT()
                        user32.GetCursorPos(ctypes.byref(pt))
                        user32.SetForegroundWindow(hwnd)
                        self.menu.tk_popup(pt.x, pt.y)
                    except Exception:
                        pass
                elif event in (WM_LBUTTONUP, WM_LBUTTONDBLCLK):
                    self.toggle_theme()
                return 0
            return user32.CallWindowProcW(self.old_wndproc, hwnd, msg, wparam, lparam)

        self.tray_proc_ref = WNDPROC(tray_wndproc)
        self.old_wndproc = set_wndproc(self.tray_hwnd, GWLP_WNDPROC, self.tray_proc_ref)

        t_lbl, _ = self.get_shortcut_labels()
        nid = NOTIFYICONDATAW()
        nid.cbSize = ctypes.sizeof(NOTIFYICONDATAW)
        nid.hWnd = self.tray_hwnd
        nid.uID = 1
        nid.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP
        nid.uCallbackMessage = WM_TRAYICON
        nid.hIcon = user32.LoadIconW(0, 32512)
        nid.szTip = f"Aero7-Zero (Left-click: Toggle [{t_lbl}] | Right-click: Menu)"
        shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(nid))

    def rebuild_tray_menu(self):
        self.menu.delete(0, "end")
        t_lbl, e_lbl = self.get_shortcut_labels()
        self.menu.add_command(label=f"Toggle Aero Theme ({t_lbl})", command=self.toggle_theme)
        self.menu.add_command(label="Configure Shortcuts...", command=self.open_settings_dialog)
        self.menu.add_separator()
        self.menu.add_command(label=f"Exit completely ({e_lbl})", command=self.stop_application)

    def open_settings_dialog(self):
        new_cfg = show_setup_window(self.config, parent=self.root)
        if new_cfg:
            self.config.update(new_cfg)
            save_config(self.config)
            self.rebuild_tray_menu()

    def remove_tray_icon(self):
        if self.tray_hwnd:
            if self.old_wndproc:
                set_wndproc(self.tray_hwnd, GWLP_WNDPROC, self.old_wndproc)
            nid = NOTIFYICONDATAW()
            nid.cbSize = ctypes.sizeof(NOTIFYICONDATAW)
            nid.hWnd = self.tray_hwnd
            nid.uID = 1
            shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(nid))

    def toggle_theme(self):
        self.active = not self.active
        if not self.active:
            for hwnd in list(self.styled_windows):
                apply_win7_window_style(hwnd, active=False)
            for it in self.overlays.values():
                it.destroy()
            self.overlays.clear()
            self.styled_windows.clear()
            self.known_windows.clear()
            self.fade_animations.clear()
        else:
            self.sync_all(force_restyle=True)

    def stop_application(self):
        self.running = False
    def detect_profile_and_geometry(self, hwnd, maximized, has_min, has_max):
        class_name = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, class_name, 256)
        cls = class_name.value
        rect = RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        ext_rect = RECT()
        dwmapi.DwmGetWindowAttribute(hwnd, DWMWA_EXTENDED_FRAME_BOUNDS, ctypes.byref(ext_rect), ctypes.sizeof(ext_rect))

        if "Chrome_WidgetWin" in cls:
            prof = "chrome"
            cfg = self.profiles[prof]
            w = cfg["bw"] * 2 + cfg["cw"]
            h = cfg["h_max"] if maximized else cfg["h_norm"]
            return prof, rect.right - w - int(round(7 * self.scale)), rect.top + int(round((7 if maximized else 1) * self.scale)), w, h, ext_rect
        if cls in TERMINAL_CLASSES:
            prof = "terminal"
            cfg = self.profiles[prof]
            w = cfg["bw"] * 2 + cfg["cw"]
            h = cfg["h_max"] if maximized else cfg["h_norm"]
            return prof, ext_rect.right - w - int(round(1 * self.scale)), ext_rect.top, w, h, ext_rect
        if cls in OFFICE_CLASSES or "WinUI" in cls or cls == "ApplicationFrameWindow":
            prof = "modern"
            cfg = self.profiles[prof]
            w = cfg["bw"] * 2 + cfg["cw"]
            h = cfg["h_max"] if maximized else cfg["h_norm"]
            return prof, ext_rect.right - w - int(round(1 * self.scale)), ext_rect.top + (0 if maximized else int(round(1 * self.scale))), w, h, ext_rect
        if cls == "#32770" or (not has_min and not has_max):
            prof = "dialog"
            cfg = self.profiles[prof]
            w = cfg["bw"] * 2 + cfg["cw"]
            return prof, ext_rect.right - w - int(round(1 * self.scale)), rect.top + int(round(1 * self.scale)), w, cfg["h_norm"], ext_rect
        if "Qt" in cls or cls not in NO_BLUE_CAPTION_CLASSES:
            prof = "classic"
            cfg = self.profiles[prof]
            w = cfg["bw"] * 2 + cfg["cw"]
            h = cfg["h_max"] if maximized else cfg["h_norm"]
            return prof, ext_rect.right - w - int(round(1 * self.scale)), ext_rect.top + int(round(1 * self.scale)), w, h, ext_rect
        prof = "modern"
        cfg = self.profiles[prof]
        w = cfg["bw"] * 2 + cfg["cw"]
        h = cfg["h_max"] if maximized else cfg["h_norm"]
        return prof, ext_rect.right - w - int(round(1 * self.scale)), ext_rect.top + (0 if maximized else int(round(1 * self.scale))), w, h, ext_rect

    def render_item(self, item, prof, hover_btn, rel_x_cursor, is_pressed, maximized, has_min, has_max, is_active):
        if is_pressed and not item.was_pressed:
            item.captured_btn = hover_btn
        elif not is_pressed:
            item.captured_btn = None
        item.was_pressed = is_pressed

        anim_active = False
        for key in ("min", "max", "close"):
            in_hold = (is_pressed and item.captured_btn == key and hover_btn == key and is_active)
            in_hover = (hover_btn == key and is_active and (not is_pressed or item.captured_btn == key))
            target_hover = 1.0 if in_hover else 0.0
            cur_hover = item.hover_progress[key]
            if cur_hover < target_hover:
                item.hover_progress[key] = min(1.0, cur_hover + 0.22)
                anim_active = True
            elif cur_hover > target_hover:
                item.hover_progress[key] = max(0.0, cur_hover - 0.16)
                anim_active = True

            target_hold = 1.0 if in_hold else 0.0
            cur_hold = item.hold_progress[key]
            if cur_hold < target_hold:
                item.hold_progress[key] = min(1.0, cur_hold + 0.30)
                anim_active = True
            elif cur_hold > target_hold:
                item.hold_progress[key] = max(0.0, cur_hold - 0.22)
                anim_active = True

        cur_state = (prof, hover_btn, rel_x_cursor if hover_btn else -1, is_pressed, maximized, has_min, has_max, is_active, tuple(round(v, 3) for v in item.hover_progress.values()), tuple(round(v, 3) for v in item.hold_progress.values()))
        if not anim_active and cur_state == item.last_visual_state:
            return
        item.last_visual_state = cur_state

        item.canvas.delete("all")
        item.tk_refs.clear()
        mode = "max" if maximized else "norm"
        mid_type = "rest" if maximized else "max"
        bw = self.profiles[prof]["bw"]

        buttons = [("close", "close", bw * 2)]
        if has_max:
            buttons.append(("max", mid_type, bw))
        if has_min:
            buttons.append(("min", "min", 0 if has_max else bw))

        for anim_key, img_key, pos_x in buttons:
            if not is_active:
                final_img = self.pil_images[(prof, mode, img_key, "inactive")]
            else:
                a_hover = item.hover_progress[anim_key]
                a_hold = item.hold_progress[anim_key]
                img_norm = self.pil_images[(prof, mode, img_key, "norm")]
                img_hot = self.pil_images[(prof, mode, img_key, "hot")]
                img_push = self.pil_images[(prof, mode, img_key, "pushed")]

                if a_hold > 0.01:
                    base = img_hot if a_hover >= 0.99 else Image.blend(img_norm, img_hot, a_hover)
                    final_img = img_push if a_hold >= 0.99 else Image.blend(base, img_push, a_hold)
                elif a_hover > 0.01:
                    final_img = img_hot if a_hover >= 0.99 else Image.blend(img_norm, img_hot, a_hover)
                else:
                    final_img = img_norm

                if hover_btn == anim_key and a_hover > 0.2:
                    final_img = apply_aero_cursor_glow(final_img, anim_key, rel_x_cursor - pos_x)

            tk_img = ImageTk.PhotoImage(final_img)
            item.tk_refs.append(tk_img)
            item.canvas.create_image(pos_x, 0, anchor="nw", image=tk_img)

    def sync_all(self, force_restyle=False):
        if not self.active:
            self.root.update()
            return

        overlay_set = {it.hwnd_ov for it in self.overlays.values()}
        if self.tray_hwnd:
            overlay_set.add(self.tray_hwnd)
        windows_z = []

        WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def enum_cb(hwnd, lParam):
            if is_window_eligible(hwnd, overlay_set):
                windows_z.append(hwnd)
            return True
        user32.EnumWindows(WNDENUMPROC(enum_cb), 0)

        active_hwnd = user32.GetForegroundWindow()
        pt = POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        is_pressed = bool(user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000)

        upper_rects = []
        currently_active = set(windows_z)

        for hwnd in list(self.overlays.keys()):
            if hwnd not in currently_active:
                self.overlays[hwnd].destroy()
                del self.overlays[hwnd]
                self.styled_windows.discard(hwnd)
                self.fade_animations.pop(hwnd, None)

        for hwnd in windows_z:
            if hwnd not in self.known_windows:
                self.known_windows.add(hwnd)
                ex = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                if not (ex & WS_EX_LAYERED):
                    user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex | WS_EX_LAYERED)
                    user32.SetLayeredWindowAttributes(hwnd, 0, 140, LWA_ALPHA)
                    self.fade_animations[hwnd] = 140

            if hwnd in self.fade_animations:
                new_alpha = min(255, self.fade_animations[hwnd] + 25)
                user32.SetLayeredWindowAttributes(hwnd, 0, new_alpha, LWA_ALPHA)
                if new_alpha >= 255:
                    del self.fade_animations[hwnd]
                else:
                    self.fade_animations[hwnd] = new_alpha

            if hwnd not in self.styled_windows or force_restyle:
                apply_win7_window_style(hwnd, active=True)
                self.styled_windows.add(hwnd)

            if hwnd not in self.overlays:
                self.overlays[hwnd] = OverlayItem(self.root, self.max_w, self.max_h, self.chroma_key)
                overlay_set.add(self.overlays[hwnd].hwnd_ov)

            item = self.overlays[hwnd]
            is_active = (hwnd == active_hwnd)
            style = user32.GetWindowLongW(hwnd, GWL_STYLE)
            has_min = bool(style & WS_MINIMIZEBOX)
            has_max = bool(style & WS_MAXIMIZEBOX)
            maximized = bool(user32.IsZoomed(hwnd))

            prof, x, y, w, h, ext_rect = self.detect_profile_and_geometry(hwnd, maximized, has_min, has_max)
            bw = self.profiles[prof]["bw"]

            clip_rects = []
            fully_covered = False
            for r_sup in upper_rects:
                ix1, iy1 = max(x, r_sup.left), max(y, r_sup.top)
                ix2, iy2 = min(x + w, r_sup.right), min(y + h, r_sup.bottom)
                if ix1 < ix2 and iy1 < iy2:
                    if ix1 == x and iy1 == y and ix2 == x + w and iy2 == y + h:
                        fully_covered = True
                        break
                    clip_rects.append((ix1 - x, iy1 - y, ix2 - x, iy2 - y))

            upper_rects.append(ext_rect)

            if fully_covered:
                if item.visible:
                    item.win.withdraw()
                    item.visible = False
                continue

            new_hover = None
            rel_x = -1
            if is_active and x <= pt.x <= x + w and y <= pt.y <= y + h:
                rel_x = pt.x - x
                if rel_x <= bw and has_min and has_max:
                    new_hover = "min"
                elif rel_x <= bw * 2 and (has_max or has_min):
                    new_hover = "max" if has_max else "min"
                elif rel_x > bw * 2:
                    new_hover = "close"

            self.render_item(item, prof, new_hover, rel_x, is_pressed, maximized, has_min, has_max, is_active)

            if not item.visible:
                item.win.deiconify()
                item.visible = True

            hwnd_above = user32.GetWindow(hwnd, 3)
            if hwnd_above in overlay_set:
                hwnd_above = None

            if (x, y, w, h) != item.last_geometry:
                item.last_geometry = (x, y, w, h)
                user32.SetWindowPos(item.hwnd_ov, hwnd_above, x, y, w, h, SWP_NOACTIVATE)
            elif hwnd_above is not None:
                user32.SetWindowPos(item.hwnd_ov, hwnd_above, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)

            clip_state = (w, h, tuple(clip_rects))
            if clip_state != item.last_clip_regions:
                item.last_clip_regions = clip_state
                if not clip_rects:
                    user32.SetWindowRgn(item.hwnd_ov, None, True)
                else:
                    rgn = gdi32.CreateRectRgn(0, 0, w, h)
                    for dx1, dy1, dx2, dy2 in clip_rects:
                        rgn_sub = gdi32.CreateRectRgn(dx1, dy1, dx2, dy2)
                        gdi32.CombineRgn(rgn, rgn, rgn_sub, RGN_DIFF)
                        gdi32.DeleteObject(rgn_sub)
                    user32.SetWindowRgn(item.hwnd_ov, rgn, True)

        self.root.update()

def show_setup_window(current_cfg, parent=None):
    result = {}
    win = tk.Toplevel(parent) if parent else tk.Tk()
    win.title("Aero7-Zero Setup Wizard")
    win.resizable(False, False)
    win.attributes("-topmost", True)

    frame = ttk.Frame(win, padding=18)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Windows 7 Aero Theme for Windows 11", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 4))
    ttk.Label(frame, text="Zero DLL injection | Zero Registry edits | Portable", foreground="#555555").grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 12))

    ttk.Label(frame, text="Toggle Theme Shortcut:").grid(row=2, column=0, sticky="w", pady=4)
    toggle_mod_var = tk.StringVar(value=current_cfg.get("toggle_mod", "Ctrl + Shift"))
    toggle_key_var = tk.StringVar(value=current_cfg.get("toggle_key", "A"))
    ttk.Combobox(frame, textvariable=toggle_mod_var, values=list(MODIFIER_MAP.keys()), state="readonly", width=13).grid(row=2, column=1, padx=4, pady=4)
    ttk.Combobox(frame, textvariable=toggle_key_var, values=KEY_OPTIONS, state="readonly", width=5).grid(row=2, column=2, pady=4)
    ttk.Label(frame, text="Exit Completely Shortcut:").grid(row=3, column=0, sticky="w", pady=4)
    exit_mod_var = tk.StringVar(value=current_cfg.get("exit_mod", "Ctrl + Alt"))
    exit_key_var = tk.StringVar(value=current_cfg.get("exit_key", "Q"))
    ttk.Combobox(frame, textvariable=exit_mod_var, values=list(MODIFIER_MAP.keys()), state="readonly", width=13).grid(row=3, column=1, padx=4, pady=4)
    ttk.Combobox(frame, textvariable=exit_key_var, values=KEY_OPTIONS, state="readonly", width=5).grid(row=3, column=2, pady=4)

    start_active_var = tk.BooleanVar(value=current_cfg.get("start_active", True))
    ttk.Checkbutton(frame, text="Enable Aero theme immediately on launch", variable=start_active_var).grid(row=4, column=0, columnspan=3, sticky="w", pady=(10, 12))

    def on_save():
        result["toggle_mod"] = toggle_mod_var.get()
        result["toggle_key"] = toggle_key_var.get()
        result["exit_mod"] = exit_mod_var.get()
        result["exit_key"] = exit_key_var.get()
        result["start_active"] = start_active_var.get()
        win.destroy()

    ttk.Button(frame, text="Save & Launch", command=on_save).grid(row=5, column=0, columnspan=3, sticky="ew")

    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    ww, wh = win.winfo_width(), win.winfo_height()
    win.geometry(f"+{(sw - ww) // 2}+{(sh - wh) // 2}")
    win.lift()
    win.focus_force()

    if parent:
        win.grab_set()
        parent.wait_window(win)
    else:
        win.mainloop()
    return result if result else None

def is_combo_pressed(mod_name, key_char):
    m1, m2 = MODIFIER_MAP.get(mod_name, (VK_CONTROL, VK_SHIFT))
    vk_key = ord(key_char.upper())
    return bool(user32.GetAsyncKeyState(m1) & 0x8000) and bool(user32.GetAsyncKeyState(m2) & 0x8000) and bool(user32.GetAsyncKeyState(vk_key) & 0x8000)

if __name__ == "__main__":
    cfg = load_config()
    if not os.path.exists(CONFIG_FILE):
        chosen = show_setup_window(cfg)
        if not chosen:
            sys.exit(0)
        cfg.update(chosen)
        save_config(cfg)

    manager = Aero7GlobalManager(cfg)
    step = 0
    prev_toggle = False
    try:
        while manager.running:
            try:
                if is_combo_pressed(manager.config["exit_mod"], manager.config["exit_key"]):
                    break

                cur_toggle = is_combo_pressed(manager.config["toggle_mod"], manager.config["toggle_key"])
                if cur_toggle and not prev_toggle:
                    manager.toggle_theme()
                prev_toggle = cur_toggle

                manager.sync_all(force_restyle=(step % 400 == 0))
                step += 1
            except Exception:
                pass
            time.sleep(0.008)
    finally:
        for hwnd in list(manager.styled_windows):
            apply_win7_window_style(hwnd, active=False)
        for it in manager.overlays.values():
            it.destroy()
        manager.remove_tray_icon()
        try:
            manager.root.destroy()
        except Exception:
            pass
