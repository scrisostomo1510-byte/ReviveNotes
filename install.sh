#!/bin/bash

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
APP_SHARE_DIR="$HOME/.local/share/applications"

echo "Installing ReviveNotes..."

# Create directories if they don't exist
mkdir -p "$BIN_DIR"
mkdir -p "$APP_SHARE_DIR"

# Make sure main script is executable
chmod +x "$APP_DIR/main.py"

# Create terminal shortcut
cat << EOF > "$BIN_DIR/revivenotes"
#!/bin/bash
exec "$APP_DIR/main.py" "\$@"
EOF
chmod +x "$BIN_DIR/revivenotes"

# Create desktop entry
cat << EOF > "$APP_SHARE_DIR/revivenotes.desktop"
[Desktop Entry]
Name=ReviveNotes
Comment=A disappointingly vibe-coded notepad app with automatic session saving
Exec=$APP_DIR/main.py %U
Icon=accessories-text-editor
Terminal=false
Type=Application
Categories=Utility;TextEditor;
MimeType=text/plain;
StartupNotify=true
EOF
chmod +x "$APP_SHARE_DIR/revivenotes.desktop"

# Update desktop database
update-desktop-database "$APP_SHARE_DIR" 2>/dev/null || echo "Warning: update-desktop-database not found or failed, but installation is complete."

echo "Installation complete! You can now run 'revivenotes' in your terminal or find it in your application menu."
