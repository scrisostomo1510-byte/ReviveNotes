import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('GtkSource', '5')
from gi.repository import Gtk, Adw, GLib, Gio, GtkSource, Pango
import session
import os

class ReviveNotesWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("ReviveNotes")
        self.set_default_size(800, 600)

        self.tab_paths = {}
        self.zoom_level = 0
        self.search_context = None

        self.app_settings = session.load_settings()
        
        # Apply Theme
        style_manager = Adw.StyleManager.get_default()
        style_manager.connect("notify::dark", self.on_dark_changed)
        theme_setting = self.app_settings.get("theme", "system")
        if theme_setting == "dark":
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        elif theme_setting == "light":
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)

        # Main layout container
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(box)

        # Header bar
        self.header_bar = Adw.HeaderBar()
        box.append(self.header_bar)

        open_btn = Gtk.Button(icon_name="document-open-symbolic")
        open_btn.set_tooltip_text("Open File (Ctrl+O)")
        open_btn.connect("clicked", self.on_open_clicked)
        self.header_bar.pack_start(open_btn)

        new_tab_btn = Gtk.Button(icon_name="tab-new-symbolic")
        new_tab_btn.set_tooltip_text("New Tab (Ctrl+T)")
        new_tab_btn.connect("clicked", self.on_new_tab_clicked)
        self.header_bar.pack_start(new_tab_btn)

        self.setup_settings_menu()

        save_btn = Gtk.Button(icon_name="document-save-symbolic")
        save_btn.set_tooltip_text("Save File (Ctrl+S)")
        save_btn.connect("clicked", self.on_save_clicked)
        self.header_bar.pack_end(save_btn)

        # Find & Replace panel
        self.search_revealer = Gtk.Revealer()
        self.search_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        search_box.set_margin_start(12)
        search_box.set_margin_end(12)
        search_box.set_margin_top(6)
        search_box.set_margin_bottom(6)
        
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.connect("search-changed", self.on_search_changed)
        search_box.append(self.search_entry)
        
        self.replace_entry = Gtk.Entry()
        self.replace_entry.set_placeholder_text("Replace with...")
        search_box.append(self.replace_entry)
        
        btn_replace_all = Gtk.Button(label="Replace All")
        btn_replace_all.connect("clicked", self.on_replace_all)
        search_box.append(btn_replace_all)
        
        btn_close_search = Gtk.Button(icon_name="window-close-symbolic")
        btn_close_search.connect("clicked", lambda b: self.search_revealer.set_reveal_child(False))
        search_box.append(btn_close_search)
        
        self.search_revealer.set_child(search_box)
        box.append(self.search_revealer)

        # Tab system
        self.tab_view = Adw.TabView()
        self.tab_bar = Adw.TabBar()
        self.tab_bar.set_view(self.tab_view)
        
        box.append(self.tab_bar)
        self.tab_view.set_vexpand(True)
        box.append(self.tab_view)

        self.connect("close-request", self.on_close_request)

        self.css_provider = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(), 
            self.css_provider, 
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.apply_font_css()
        self.setup_actions()
        self.load_state()
        
        # Background Auto-Save (Every 30 seconds)
        GLib.timeout_add_seconds(30, self.auto_save_session)
        
    def auto_save_session(self):
        self.save_session_state()
        return True # keep running

    def setup_actions(self):
        action_new_tab = Gio.SimpleAction.new("new-tab", None)
        action_new_tab.connect("activate", lambda a, v: self.add_tab())
        self.add_action(action_new_tab)
        
        action_close_tab = Gio.SimpleAction.new("close-tab", None)
        action_close_tab.connect("activate", lambda a, v: self.close_current_tab())
        self.add_action(action_close_tab)

        action_search = Gio.SimpleAction.new("search", None)
        action_search.connect("activate", lambda a, v: self.toggle_search())
        self.add_action(action_search)
        
        action_replace = Gio.SimpleAction.new("replace", None)
        action_replace.connect("activate", lambda a, v: self.toggle_replace())
        self.add_action(action_replace)

        action_save = Gio.SimpleAction.new("save-file", None)
        action_save.connect("activate", lambda a, v: self.on_save_clicked(None))
        self.add_action(action_save)
        
        action_save_as = Gio.SimpleAction.new("save-as-file", None)
        action_save_as.connect("activate", lambda a, v: self.on_save_as_clicked())
        self.add_action(action_save_as)
        
        action_open = Gio.SimpleAction.new("open-file", None)
        action_open.connect("activate", lambda a, v: self.on_open_clicked(None))
        self.add_action(action_open)
        
        action_next_tab = Gio.SimpleAction.new("next-tab", None)
        action_next_tab.connect("activate", lambda a, v: self.select_next_tab())
        self.add_action(action_next_tab)
        
        action_prev_tab = Gio.SimpleAction.new("prev-tab", None)
        action_prev_tab.connect("activate", lambda a, v: self.select_prev_tab())
        self.add_action(action_prev_tab)
        
        action_zoom_in = Gio.SimpleAction.new("zoom-in", None)
        action_zoom_in.connect("activate", lambda a, v: self.on_zoom_in())
        self.add_action(action_zoom_in)

        action_zoom_out = Gio.SimpleAction.new("zoom-out", None)
        action_zoom_out.connect("activate", lambda a, v: self.on_zoom_out())
        self.add_action(action_zoom_out)

        action_zoom_reset = Gio.SimpleAction.new("zoom-reset", None)
        action_zoom_reset.connect("activate", lambda a, v: self.on_zoom_reset())
        self.add_action(action_zoom_reset)

        action_toggle_wrap = Gio.SimpleAction.new("toggle-wrap", None)
        action_toggle_wrap.connect("activate", lambda a, v: self.on_toggle_wrap())
        self.add_action(action_toggle_wrap)

    def on_zoom_in(self):
        self.zoom_level += 1
        self.apply_font_css()
        
    def on_zoom_out(self):
        self.zoom_level -= 1
        self.apply_font_css()
        
    def on_zoom_reset(self):
        self.zoom_level = 0
        self.apply_font_css()

    def on_toggle_wrap(self, *args):
        current = self.app_settings.get("wrap_mode", True)
        self.app_settings["wrap_mode"] = not current
        self.apply_wrap_mode()

    def select_next_tab(self):
        n = self.tab_view.get_n_pages()
        if n > 1:
            page = self.tab_view.get_selected_page()
            idx = self.tab_view.get_page_position(page)
            self.tab_view.set_selected_page(self.tab_view.get_nth_page((idx + 1) % n))

    def select_prev_tab(self):
        n = self.tab_view.get_n_pages()
        if n > 1:
            page = self.tab_view.get_selected_page()
            idx = self.tab_view.get_page_position(page)
            self.tab_view.set_selected_page(self.tab_view.get_nth_page((idx - 1) % n))

    def setup_settings_menu(self):
        settings_btn = Gtk.MenuButton()
        settings_btn.set_icon_name("open-menu-symbolic")
        self.header_bar.pack_end(settings_btn)

        popover = Gtk.Popover()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox.set_margin_start(12)
        vbox.set_margin_end(12)
        vbox.set_margin_top(12)
        vbox.set_margin_bottom(12)
        popover.set_child(vbox)
        settings_btn.set_popover(popover)

        # Theme dropdown
        theme_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        theme_label = Gtk.Label(label="Theme")
        self.theme_dropdown = Gtk.DropDown.new_from_strings(["System Default", "Light Mode", "Dark Mode"])
        self.theme_dropdown.set_valign(Gtk.Align.CENTER)
        
        theme_setting = self.app_settings.get("theme", "system")
        if theme_setting == "light":
            self.theme_dropdown.set_selected(1)
        elif theme_setting == "dark":
            self.theme_dropdown.set_selected(2)
        else:
            self.theme_dropdown.set_selected(0)
            
        self.theme_dropdown.connect("notify::selected", self.on_theme_selected)
        theme_box.append(theme_label)
        theme_box.append(self.theme_dropdown)
        vbox.append(theme_box)

        # Font selection
        font_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        font_label = Gtk.Label(label="Font")
        
        font_dialog = Gtk.FontDialog()
        font_btn = Gtk.FontDialogButton(dialog=font_dialog)
        font_desc = Pango.FontDescription.from_string(self.app_settings.get("font", "Monospace 12"))
        font_btn.set_font_desc(font_desc)
        font_btn.connect("notify::font-desc", self.on_font_selected)
        
        font_box.append(font_label)
        font_box.append(font_btn)
        vbox.append(font_box)

        # Word Wrap toggle
        wrap_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        wrap_label = Gtk.Label(label="Word Wrap")
        self.wrap_switch = Gtk.Switch()
        self.wrap_switch.set_valign(Gtk.Align.CENTER)
        self.wrap_switch.set_active(self.app_settings.get("wrap_mode", True))
        self.wrap_switch.connect("notify::active", self.on_wrap_switched)
        wrap_box.append(wrap_label)
        wrap_box.append(self.wrap_switch)
        vbox.append(wrap_box)

    def on_wrap_switched(self, switch, gparam):
        self.app_settings["wrap_mode"] = switch.get_active()
        self.apply_wrap_mode()

    def apply_wrap_mode(self):
        wrap = self.app_settings.get("wrap_mode", True)
        self.wrap_switch.set_active(wrap)
        mode = Gtk.WrapMode.WORD_CHAR if wrap else Gtk.WrapMode.NONE
        for i in range(self.tab_view.get_n_pages()):
            page = self.tab_view.get_nth_page(i)
            text_view = page.get_child().get_child()
            text_view.set_wrap_mode(mode)

    def on_theme_selected(self, dropdown, gparam):
        selected = dropdown.get_selected()
        style_manager = Adw.StyleManager.get_default()
        if selected == 1:
            self.app_settings["theme"] = "light"
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        elif selected == 2:
            self.app_settings["theme"] = "dark"
            style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:
            self.app_settings["theme"] = "system"
            style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)

    def on_font_selected(self, font_btn, gparam):
        font_desc = font_btn.get_font_desc()
        if font_desc:
            font_str = font_desc.to_string()
            self.app_settings["font"] = font_str
            self.apply_font_css()

    def on_dark_changed(self, style_manager, gparam):
        self.update_source_style_scheme()

    def update_source_style_scheme(self):
        manager = GtkSource.StyleSchemeManager.get_default()
        style_manager = Adw.StyleManager.get_default()
        is_dark = style_manager.get_dark()
        
        scheme_id = "Adwaita-dark" if is_dark else "Adwaita"
        scheme = manager.get_scheme(scheme_id)
        if not scheme:
            scheme_id = "oblivion" if is_dark else "classic"
            scheme = manager.get_scheme(scheme_id)
            
        if not scheme:
            return

        for i in range(self.tab_view.get_n_pages()):
            page = self.tab_view.get_nth_page(i)
            text_view = page.get_child().get_child()
            buffer = text_view.get_buffer()
            buffer.set_style_scheme(scheme)

    def apply_font_css(self):
        font_str = self.app_settings.get("font", "Monospace 12")
        font_desc = Pango.FontDescription.from_string(font_str)
        family = font_desc.get_family()
        size = font_desc.get_size()
        
        if family is None:
            family = "monospace"
            
        css_lines = ["textview {"]
        css_lines.append(f"font-family: '{family}', monospace;")
        
        if size > 0:
            if not font_desc.get_size_is_absolute():
                size = size / Pango.SCALE
            size += (self.zoom_level * 2)
            if size < 4: size = 4
            css_lines.append(f"font-size: {size}pt;")
            
        css_lines.append("}")
        css = "\n".join(css_lines)
        self.css_provider.load_from_data(css.encode('utf-8'))

    def create_text_view(self, content=""):
        text_view = GtkSource.View()
        text_view.set_show_line_numbers(True)
        text_view.set_highlight_current_line(True)
        text_view.set_auto_indent(True)
        text_view.set_smart_home_end(GtkSource.SmartHomeEndType.BEFORE)
        
        text_view.set_left_margin(24)
        text_view.set_right_margin(24)
        text_view.set_top_margin(24)
        text_view.set_bottom_margin(24)
        text_view.set_pixels_above_lines(2)
        text_view.set_pixels_below_lines(2)
        
        wrap = self.app_settings.get("wrap_mode", True)
        mode = Gtk.WrapMode.WORD_CHAR if wrap else Gtk.WrapMode.NONE
        text_view.set_wrap_mode(mode)
        
        buffer = text_view.get_buffer()
        buffer.set_enable_undo(True)
        buffer.set_text(content, -1)
        
        manager = GtkSource.StyleSchemeManager.get_default()
        style_manager = Adw.StyleManager.get_default()
        is_dark = style_manager.get_dark()
        scheme_id = "Adwaita-dark" if is_dark else "Adwaita"
        scheme = manager.get_scheme(scheme_id)
        if not scheme:
            scheme_id = "oblivion" if is_dark else "classic"
            scheme = manager.get_scheme(scheme_id)
        if scheme:
            buffer.set_style_scheme(scheme)
        
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(text_view)
        return scrolled_window, text_view

    def toggle_search(self):
        self.replace_entry.set_visible(False)
        is_revealed = self.search_revealer.get_reveal_child()
        self.search_revealer.set_reveal_child(not is_revealed)
        if not is_revealed:
            self.search_entry.grab_focus()

    def toggle_replace(self):
        self.replace_entry.set_visible(True)
        self.search_revealer.set_reveal_child(True)
        self.search_entry.grab_focus()

    def on_search_changed(self, entry):
        text = entry.get_text()
        page = self.tab_view.get_selected_page()
        if not page:
            return
        
        buffer = page.get_child().get_child().get_buffer()
        
        if not self.search_context or self.search_context.get_buffer() != buffer:
            if self.search_context:
                self.search_context.set_highlight(False)
            settings = GtkSource.SearchSettings()
            self.search_context = GtkSource.SearchContext.new(buffer, settings)
            self.search_context.set_highlight(True)
            
        self.search_context.get_settings().set_search_text(text)
        
    def on_replace_all(self, btn):
        if self.search_context:
            replace_text = self.replace_entry.get_text()
            try:
                self.search_context.replace_all(replace_text, -1)
            except Exception as e:
                print(f"Replace all error: {e}")

    def on_open_clicked(self, button):
        dialog = Gtk.FileDialog()
        dialog.open(self, None, self.on_open_response)

    def on_open_response(self, dialog, result):
        try:
            file = dialog.open_finish(result)
            if file:
                self.open_file(file.get_path())
        except GLib.Error as e:
            print(f"File dialog cancelled or error: {e}")

    def on_save_clicked(self, button):
        page = self.tab_view.get_selected_page()
        if not page:
            return
            
        file_path = self.tab_paths.get(page)
        if file_path:
            self._save_page_to_file(page, file_path)
        else:
            self.on_save_as_clicked()

    def on_save_as_clicked(self):
        page = self.tab_view.get_selected_page()
        if not page:
            return
        
        dialog = Gtk.FileDialog()
        dialog.set_initial_name(page.get_title())
        dialog.save(self, None, self.on_save_response, page)

    def on_save_response(self, dialog, result, page):
        try:
            file = dialog.save_finish(result)
            if file:
                file_path = file.get_path()
                self._save_page_to_file(page, file_path)
        except GLib.Error as e:
            print(f"File dialog cancelled or error: {e}")

    def _save_page_to_file(self, page, file_path):
        scrolled_window = page.get_child()
        text_view = scrolled_window.get_child()
        buffer = text_view.get_buffer()
        start, end = buffer.get_bounds()
        content = buffer.get_text(start, end, True)
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.tab_paths[page] = file_path
            page.set_title(os.path.basename(file_path))
        except Exception as e:
            print(f"Error saving to {file_path}: {e}")

    def on_new_tab_clicked(self, button):
        self.add_tab()

    def close_current_tab(self):
        page = self.tab_view.get_selected_page()
        if page:
            self.tab_view.close_page(page)

    def on_buffer_changed(self, buffer, page):
        if self.tab_paths.get(page):
            return
            
        start, end = buffer.get_bounds()
        content = buffer.get_text(start, end, True)
        first_line = content.split('\n')[0].strip()
        title = first_line[:50] if first_line else "Untitled"
        page.set_title(title)

    def add_tab(self, title="Untitled", content="", file_path=None):
        scrolled_window, text_view = self.create_text_view(content)
        page = self.tab_view.append(scrolled_window)
        page.set_title(title)
        
        if file_path:
            self.tab_paths[page] = file_path
            
        buffer = text_view.get_buffer()
        buffer.connect("changed", self.on_buffer_changed, page)
        
        if title == "Untitled" and content and not file_path:
            self.on_buffer_changed(buffer, page)
            
        self.tab_view.set_selected_page(page)
        return page

    def open_file(self, file_path):
        if not os.path.exists(file_path):
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            title = os.path.basename(file_path)
            self.add_tab(title=title, content=content, file_path=file_path)
        except Exception as e:
            print(f"Error opening file {file_path}: {e}")

    def load_state(self):
        tabs_data = session.load_session()
        if not tabs_data:
            self.add_tab()
        else:
            for tab_info in tabs_data:
                self.add_tab(title=tab_info.get("title", "Untitled"), 
                             content=tab_info.get("content", ""),
                             file_path=tab_info.get("file_path"))

    def save_session_state(self):
        session.save_settings(self.app_settings)
        tabs_data = []
        for i in range(self.tab_view.get_n_pages()):
            page = self.tab_view.get_nth_page(i)
            scrolled_window = page.get_child()
            text_view = scrolled_window.get_child()
            buffer = text_view.get_buffer()
            start, end = buffer.get_bounds()
            content = buffer.get_text(start, end, True)
            tabs_data.append({
                "title": page.get_title(),
                "content": content,
                "file_path": self.tab_paths.get(page)
            })
        session.save_session(tabs_data)

    def on_close_request(self, window):
        self.save_session_state()
        return False
