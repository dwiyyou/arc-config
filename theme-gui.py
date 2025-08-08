#!/usr/bin/env python3

import os
import sys
import subprocess
import configparser
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QComboBox, QPushButton, 
                             QMessageBox, QListWidget)
from PyQt5.QtCore import Qt

class ThemeManager:
    def __init__(self):
        # Direktori tema
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
        self.current_theme = self._get_current_theme()

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

    def _get_current_theme(self):
        current = {'gtk': '', 'kvantum': '', 'icon': ''}
        
        # Get GTK theme
        if os.path.exists(self.gtk3_settings_file):
            config = configparser.ConfigParser()
            config.read(self.gtk3_settings_file)
            if 'Settings' in config and 'gtk-theme-name' in config['Settings']:
                current['gtk'] = config['Settings']['gtk-theme-name']
        
        # Get Kvantum theme
        kvantum_config = os.path.expanduser("~/.config/Kvantum/kvantum.kvconfig")
        if os.path.exists(kvantum_config):
            config = configparser.ConfigParser()
            config.read(kvantum_config)
            if 'General' in config and 'theme' in config['General']:
                current['kvantum'] = config['General']['theme']
        
        # Get icon theme
        if os.path.exists(self.kde_globals_file):
            config = configparser.ConfigParser()
            config.read(self.kde_globals_file)
            if 'Icons' in config and 'Theme' in config['Icons']:
                current['icon'] = config['Icons']['Theme']
        
        return current

    def apply_theme(self, gtk_theme, kvantum_theme, icon_theme):
        # Apply GTK themes
        if gtk_theme and gtk_theme in self.gtk_themes:
            self._write_gtk_settings(3, gtk_theme, icon_theme)
            self._write_gtk_settings(4, gtk_theme, icon_theme)
        
        # Apply Kvantum theme
        if kvantum_theme and kvantum_theme in self.kvantum_themes:
            self._write_kvantum_settings(kvantum_theme)
            self._write_qt_settings(kvantum_theme)
        
        # Apply icon theme
        if icon_theme and icon_theme in self.icon_themes:
            self._write_kde_settings(icon_theme)
        
        # Update environment
        subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface', 'gtk-theme', gtk_theme], check=False)
        subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface', 'icon-theme', icon_theme], check=False)
        subprocess.run(['qt5ct', '--apply'], check=False)
        
        return "Theme applied successfully!\nYou may need to restart applications to see changes."

    def _write_gtk_settings(self, gtk_version, theme_name, icon_theme=None):
        config = configparser.ConfigParser()
        config.optionxform = str
        
        settings_file = self.gtk3_settings_file if gtk_version == 3 else self.gtk4_settings_file
        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
        
        if os.path.exists(settings_file):
            config.read(settings_file)
        
        if 'Settings' not in config:
            config['Settings'] = {}
        
        config['Settings']['gtk-theme-name'] = theme_name
        if icon_theme:
            config['Settings']['gtk-icon-theme-name'] = icon_theme
        
        with open(settings_file, 'w') as f:
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

    def _write_qt_settings(self, theme_name):
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

    def _write_kde_settings(self, icon_theme):
        config = configparser.ConfigParser()
        config.optionxform = str
        
        if os.path.exists(self.kde_globals_file):
            config.read(self.kde_globals_file)
        
        if 'Icons' not in config:
            config['Icons'] = {}
        
        config['Icons']['Theme'] = icon_theme
        
        with open(self.kde_globals_file, 'w') as f:
            config.write(f)

class ThemePreviewWidget(QWidget):
    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # GTK Theme Selection
        gtk_layout = QHBoxLayout()
        gtk_layout.addWidget(QLabel("GTK Theme:"))
        self.gtk_combo = QComboBox()
        self.gtk_combo.addItems(self.theme_manager.gtk_themes)
        if self.theme_manager.current_theme['gtk'] in self.theme_manager.gtk_themes:
            self.gtk_combo.setCurrentText(self.theme_manager.current_theme['gtk'])
        gtk_layout.addWidget(self.gtk_combo)
        layout.addLayout(gtk_layout)
        
        # Kvantum Theme Selection
        kvantum_layout = QHBoxLayout()
        kvantum_layout.addWidget(QLabel("Kvantum Theme:"))
        self.kvantum_combo = QComboBox()
        self.kvantum_combo.addItems(self.theme_manager.kvantum_themes)
        if self.theme_manager.current_theme['kvantum'] in self.theme_manager.kvantum_themes:
            self.kvantum_combo.setCurrentText(self.theme_manager.current_theme['kvantum'])
        kvantum_layout.addWidget(self.kvantum_combo)
        layout.addLayout(kvantum_layout)
        
        # Icon Theme Selection
        icon_layout = QHBoxLayout()
        icon_layout.addWidget(QLabel("Icon Theme:"))
        self.icon_combo = QComboBox()
        self.icon_combo.addItems(self.theme_manager.icon_themes)
        if self.theme_manager.current_theme['icon'] in self.theme_manager.icon_themes:
            self.icon_combo.setCurrentText(self.theme_manager.current_theme['icon'])
        icon_layout.addWidget(self.icon_combo)
        layout.addLayout(icon_layout)
        
        # Apply Button
        self.apply_button = QPushButton("Apply Theme")
        self.apply_button.clicked.connect(self.apply_theme)
        layout.addWidget(self.apply_button)
        
        # Theme Preview Area
        self.preview_list = QListWidget()
        self.preview_list.setSelectionMode(QListWidget.NoSelection)
        layout.addWidget(QLabel("Available Themes:"))
        layout.addWidget(self.preview_list)
        
        self.update_preview_list()
        self.setLayout(layout)
    
    def update_preview_list(self):
        self.preview_list.clear()
        
        # Add GTK themes
        self.preview_list.addItem("=== GTK Themes ===")
        for theme in self.theme_manager.gtk_themes:
            self.preview_list.addItem(f"GTK: {theme}")
        
        # Add Kvantum themes
        self.preview_list.addItem("\n=== Kvantum Themes ===")
        for theme in self.theme_manager.kvantum_themes:
            self.preview_list.addItem(f"Kvantum: {theme}")
        
        # Add Icon themes
        self.preview_list.addItem("\n=== Icon Themes ===")
        for theme in self.theme_manager.icon_themes:
            self.preview_list.addItem(f"Icon: {theme}")
    
    def apply_theme(self):
        gtk_theme = self.gtk_combo.currentText()
        kvantum_theme = self.kvantum_combo.currentText()
        icon_theme = self.icon_combo.currentText()
        
        result = self.theme_manager.apply_theme(gtk_theme, kvantum_theme, icon_theme)
        QMessageBox.information(self, "Theme Applied", result)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.theme_manager = ThemeManager()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Linux Theme Manager")
        self.setGeometry(300, 300, 600, 500)
        
        central_widget = ThemePreviewWidget(self.theme_manager)
        self.setCentralWidget(central_widget)
        
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
