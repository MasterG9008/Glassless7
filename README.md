 Glassless7
 
Bring Windows 7 Aero window styling and glossy caption buttons to Windows 11—with zero DLL injection, zero registry edits, and zero system file modifications.

Glassless7 is a lightweight, portable Python utility that dynamically styles Windows 11 title bars using native Desktop Window Manager (DWM) attributes and renders real-time, DPI-aware Windows 7 Aero-style glossy overlays over window control buttons (Minimize, Maximize/Restore, Close).

---

  Features

Zero System Modification: Works entirely in user space without patching `uxtheme.dll`, injecting DLLs into other processes, or altering the Windows Registry.
Authentic Aero Aesthetics:
Applies Windows 7-inspired sky-blue title bar tints, subtle borders, and compact rounded corners via native `DWMWA_*` APIs.
Renders custom glossy button overlays with hover glows, cursor-tracking radial highlights, and smooth fade transitions.
Automatically desaturates inactive window buttons and strips the red tint from inactive close buttons, just like Windows 7.
  Smart Window Detection: Automatically adapts button geometry and styling across Classic Win32 apps, File Explorer, Chrome/Electron browsers, Windows Terminal, Microsoft Office, WinUI/UWP apps, and standard dialogs.
Z-Order & Occlusion Aware: Properly tracks overlapping windows and clips overlays so background buttons never bleed through foreground windows.*System Tray & Global Hotkeys:
  * Runs silently in the background with a system tray icon.
  * Toggle the theme on/off instantly or exit cleanly (restoring all windows to their default Windows 11 appearance) using customizable global hotkeys.
High-DPI Ready: Automatically scales button dimensions and offsets to match your display scaling.
---
 Requirements

OS: Windows 11 (Windows 10 is partially supported, though DWM caption coloring requires Windows 11 Build 22000+)
Python:** Python 3.8 or higher
Dependencies:
   `Pillow` (PIL)
   `tkinter` (included with standard Windows Python installations)

---

 Installation & Usage

Clone the repository:
   ```bash
   git clone https://github.com/MasterG9008/Glassless7
  
   ```

Install dependencies:
   ```bash
   pip install pillow
   ```
   

First-Time Setup:
   On the first launch, a setup wizard will appear allowing you to configure your preferred keyboard shortcuts and choose whether the theme starts active immediately. Your settings are saved locally in `aero7_config.json`.

---

 Default Controls & Shortcuts

 Action  Default Shortcut  Tray Action 
 :--- | :--- | :--- |
 Toggle Theme On / Off** | `Ctrl + Shift + A` | Left-click tray icon |
 Open Settings / Menu** | — | Right-click tray icon |
 Exit & Restore Windows** | `Ctrl + Alt + Q` | Select **Exit completely** in tray menu |

 How It Works

1.DWM Window Styling: Uses `DwmSetWindowAttribute` to apply custom caption colors (`DWMWA_CAPTION_COLOR`), border colors (`DWMWA_BORDER_COLOR`), text colors (`DWMWA_TEXT_COLOR`), and small rounded corners (`DWMWCP_ROUNDSMALL`) to eligible top-level windows.
2. UxTheme Texture Extraction:** Extracts base button glyphs from the active Windows visual style via `uxtheme.dll` and composites procedural Aero glass gradients, specular highlights, and cursor-following radial glows using `Pillow`.
3. Click-Through Overlays:** Creates transparent, non-activating `WS_EX_TRANSPARENT` overlay windows positioned directly above each window's caption buttons, allowing native mouse clicks to pass straight through to the underlying window while rendering the Aero visuals on top.

---

 Known Limitations

Custom-Drawn Title Bars:** Applications that draw their own custom title bars (such as Chrome, Office, Windows Terminal, and modern WinUI 3 apps) ignore `DWMWA_CAPTION_COLOR`, so Glassless7 applies button overlays without forcing a blue caption background on those specific window classes.
Elevated (Admin) Windows:** Due to Windows UIPI (User Interface Privilege Isolation), overlays cannot sit above windows running as Administrator unless Glassless7 is also run with administrator privileges.

---

 License

This project is open-source. Feel free to modify, distribute, and contribute!
