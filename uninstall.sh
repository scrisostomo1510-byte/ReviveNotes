#!/bin/bash

BIN_DIR="$HOME/.local/bin"
APP_SHARE_DIR="$HOME/.local/share/applications"

echo "Uninstalling ReviveNotes..."

# Remove terminal shortcut
if [ -f "$BIN_DIR/revivenotes" ]; then
    rm "$BIN_DIR/revivenotes"
    echo "Removed terminal shortcut."
fi

# Remove desktop entry
if [ -f "$APP_SHARE_DIR/revivenotes.desktop" ]; then
    rm "$APP_SHARE_DIR/revivenotes.desktop"
    echo "Removed desktop entry."
fi

# Update desktop database
update-desktop-database "$APP_SHARE_DIR" 2>/dev/null

echo "Uninstallation complete!"
