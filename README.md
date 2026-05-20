# ReviveNotes

*A disappointingly vibe-coded notepad app with automatic session saving. Now, enjoy the also-AI-written documentation.*

ReviveNotes is a modern, intuitive, GTK 4 + Libadwaita notepad application designed for Linux.

Its killer feature? **Never worry about saving again.** 
When you close the app, your entire session—all open tabs, their contents, and your unsaved ramblings—are silently and automatically saved. When you reopen ReviveNotes, everything is exactly as you left it. Just like Notepad on modern Windows, but natively on Linux.

## Features
- 🚀 **Crash-proof Auto-save**: Background session saving every 30 seconds.
- 🎨 **Modern Aesthetics**: Built with GTK 4 and Libadwaita.
- 🌓 **Dynamic Themes**: Seamless toggling between System, Light, and Dark modes.
- 🔍 **Find & Replace**: Native search and replace panel.
- ⌨️ **Keyboard Navigation**: Familiar shortcuts for opening, closing, zooming, and navigating tabs.
- 🛠 **Robust Editor**: Features `GtkSourceView` under the hood for line numbers, current line highlighting, and auto-indentation.

## Installation

Run the provided install script to add ReviveNotes to your system's application menu and set up a terminal command (`revivenotes`).

```bash
chmod +x install.sh
./install.sh
```

## Uninstallation

To remove the desktop entry and terminal shortcut:

```bash
chmod +x uninstall.sh
./uninstall.sh
```
