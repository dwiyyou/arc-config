#!/usr/bin/env python3

import os
import curses
from curses import wrapper
import subprocess
import configparser
from pathlib import Path

class ThemeManager:
    def __init__(self):
        # Direktori tempat tema disimpan
        self.gtk_themes_dir = "/usr/share/themes"
        self.icon_themes_dir = "/usr/share/icons"
        self.kvantum_themes_dir = os.path.expanduser("~/.config/Kvantum")
        
        # File konfigurasi
        self.gtk3_settings_file = os.path.expanduser("~/.config/gtk-3.0/settings.ini")
        self.gtk4_settings_file = os.path.expanduser("~/.config/gtk-4.0/settings.ini")
        self.qt_settings_file = os.path.expanduser("~/.config/qt5ct/qt5ct.conf")
        self.kde_globals_file = os.path.expanduser("~/.config/kdeglobals")
        
        # Daftar tema
        self.gtk_themes = self._get_themes(self.gtk_themes_dir)
        self.icon_themes = self._get_themes(self.icon_themes_dir)
        self.kvantum_themes = self._get_kvantum_themes()
        
    def _get_themes(self, theme_dir):
        try:
            return [d for d in os.listdir(theme_dir) 
                   if os.path.isdir(os.path.join(theme_dir, d)) and not d.startswith('.')]
        except FileNotFoundError:
            return []
    
    def _get_kvantum_themes(self):
        themes = []
        if os.path.exists(self.kvantum_themes_dir):
            for theme in os.listdir(self.kvantum_themes_dir):
                if theme.endswith('.kvconfig') and theme != "Default.kvconfig":
                    themes.append(theme.replace('.kvconfig', ''))
        return themes
    
    def _write_gtk_settings(self, gtk_version, theme_name, icon_theme=None, cursor_theme=None):
        config = configparser.ConfigParser()
        config.optionxform = str  # Maintain case sensitivity
        
        settings_file = self.gtk3_settings_file if gtk_version == 3 else self.gtk4_settings_file
        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
        
        if os.path.exists(settings_file):
            config.read(settings_file)
        
        if 'Settings' not in config:
            config['Settings'] = {}
        
        config['Settings']['gtk-theme-name'] = theme_name
        if icon_theme:
            config['Settings']['gtk-icon-theme-name'] = icon_theme
        if cursor_theme:
            config['Settings']['gtk-cursor-theme-name'] = cursor_theme
        
        with open(settings_file, 'w') as f:
            config.write(f)
    
    def _write_qt_settings(self, theme_name, icon_theme=None):
        if not os.path.exists(self.qt_settings_file):
            return
        
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(self.qt_settings_file)
        
        if 'appearance' not in config:
            config['appearance'] = {}
        
        config['appearance']['style'] = 'kvantum'
        config['appearance']['color_scheme_path'] = ''
        
        with open(self.qt_settings_file, 'w') as f:
            config.write(f)
    
    def _write_kvantum_settings(self, theme_name):
        config_path = os.path.expanduser("~/.config/Kvantum/kvantum.kvconfig")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        config = configparser.ConfigParser()
        config.optionxform = str
        
        if os.path.exists(config_path):
            config.read(config_path)
        
        if 'General' not in config:
            config['General'] = {}
        
        config['General']['theme'] = theme_name
        
        with open(config_path, 'w') as f:
            config.write(f)
    
    def _write_kde_settings(self, icon_theme=None, cursor_theme=None):
        config = configparser.ConfigParser()
        config.optionxform = str
        
        if os.path.exists(self.kde_globals_file):
            config.read(self.kde_globals_file)
        
        if 'Icons' not in config:
            config['Icons'] = {}
        
        if icon_theme:
            config['Icons']['Theme'] = icon_theme
        
        if cursor_theme:
            if 'Mouse' not in config:
                config['Mouse'] = {}
            config['Mouse']['cursorTheme'] = cursor_theme
        
        with open(self.kde_globals_file, 'w') as f:
            config.write(f)
    
    def apply_theme(self, gtk_theme, kvantum_theme, icon_theme, cursor_theme=None):
        # Apply GTK themes
        if gtk_theme and gtk_theme in self.gtk_themes:
            self._write_gtk_settings(3, gtk_theme, icon_theme, cursor_theme)
            self._write_gtk_settings(4, gtk_theme, icon_theme, cursor_theme)
        
        # Apply Kvantum theme
        if kvantum_theme and kvantum_theme in self.kvantum_themes:
            self._write_kvantum_settings(kvantum_theme)
            self._write_qt_settings(kvantum_theme)
        
        # Apply icon theme
        if icon_theme and icon_theme in self.icon_themes:
            self._write_kde_settings(icon_theme, cursor_theme)
        
        # Update environment
        subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface', 'gtk-theme', gtk_theme], check=False)
        subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface', 'icon-theme', icon_theme], check=False)
        if cursor_theme:
            subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface', 'cursor-theme', cursor_theme], check=False)
        
        # Reload Qt applications
        subprocess.run(['qt5ct', '--apply'], check=False)
        
        return "Theme applied successfully! You may need to restart applications to see changes."

def display_menu(stdscr, selected_row_idx, theme_manager, current_selections):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    # Judul
    title = "Linux Theme Manager (TUI)"
    stdscr.addstr(0, w//2 - len(title)//2, title, curses.A_BOLD)
    
    # Menu utama
    menu_items = [
        f"GTK Theme: {current_selections['gtk']}",
        f"Kvantum Theme: {current_selections['kvantum']}",
        f"Icon Theme: {current_selections['icon']}",
        "Apply Theme",
        "Exit"
    ]
    
    for idx, item in enumerate(menu_items):
        x = w//2 - len(item)//2
        y = h//2 - len(menu_items)//2 + idx
        if idx == selected_row_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, item)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, item)
    
    # Status bar
    status = "Navigate: ↑/↓  Select: Enter  Quit: q"
    stdscr.addstr(h-1, 0, status, curses.A_DIM)
    
    stdscr.refresh()

def select_theme(stdscr, themes, title):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    selected = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Select {title} (Enter to confirm, q to cancel):", curses.A_BOLD)
        
        if not themes:
            stdscr.addstr(2, 0, f"No {title} found in system!", curses.A_BOLD)
            stdscr.addstr(h-1, 0, "Press any key to continue...")
            stdscr.getch()
            return None
        
        for idx, theme in enumerate(themes):
            if idx < h-4:  # Prevent writing beyond screen
                if idx == selected:
                    stdscr.attron(curses.color_pair(1))
                    stdscr.addstr(idx+2, 0, theme)
                    stdscr.attroff(curses.color_pair(1))
                else:
                    stdscr.addstr(idx+2, 0, theme)
        
        key = stdscr.getch()
        
        if key == curses.KEY_UP and selected > 0:
            selected -= 1
        elif key == curses.KEY_DOWN and selected < len(themes)-1:
            selected += 1
        elif key == ord('\n'):
            return themes[selected]
        elif key == ord('q'):
            return None

def main(stdscr):
    # Inisialisasi
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    
    theme_manager = ThemeManager()
    current_row = 0
    current_selections = {
        'gtk': theme_manager.gtk_themes[0] if theme_manager.gtk_themes else "None",
        'kvantum': theme_manager.kvantum_themes[0] if theme_manager.kvantum_themes else "None",
        'icon': theme_manager.icon_themes[0] if theme_manager.icon_themes else "None"
    }
    
    while True:
        display_menu(stdscr, current_row, theme_manager, current_selections)
        key = stdscr.getch()
        
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < 4:
            current_row += 1
        elif key == ord('\n'):
            if current_row == 0:  # GTK Theme
                selected = select_theme(stdscr, theme_manager.gtk_themes, "GTK Theme")
                if selected:
                    current_selections['gtk'] = selected
            elif current_row == 1:  # Kvantum Theme
                selected = select_theme(stdscr, theme_manager.kvantum_themes, "Kvantum Theme")
                if selected:
                    current_selections['kvantum'] = selected
            elif current_row == 2:  # Icon Theme
                selected = select_theme(stdscr, theme_manager.icon_themes, "Icon Theme")
                if selected:
                    current_selections['icon'] = selected
            elif current_row == 3:  # Apply Theme
                result = theme_manager.apply_theme(
                    current_selections['gtk'],
                    current_selections['kvantum'],
                    current_selections['icon']
                )
                stdscr.clear()
                stdscr.addstr(0, 0, result)
                stdscr.addstr(2, 0, "Press any key to continue...")
                stdscr.getch()
            elif current_row == 4:  # Exit
                break
        elif key == ord('q'):
            break

if __name__ == "__main__":
    wrapper(main)
