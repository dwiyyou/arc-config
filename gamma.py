#!/usr/bin/env python3

import gi
import subprocess
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

class GammaControlApp(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="wl-gammactl Controller")
        self.set_border_width(10)
        self.set_default_size(400, 300)
        
        # Inisialisasi nilai default
        self.gamma_value = 1.0
        self.contrast_value = 1.0
        self.brightness_value = 1.0
        
        # Main container
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)
        
        # Gamma control
        gamma_label = Gtk.Label(label="Gamma (0.1 - 2.0)")
        vbox.pack_start(gamma_label, False, False, 0)
        
        self.gamma_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0.1, 2.0, 0.05)
        self.gamma_scale.set_value(1.0)
        self.gamma_scale.set_digits(2)
        self.gamma_scale.connect("value-changed", self.on_gamma_changed)
        vbox.pack_start(self.gamma_scale, False, False, 0)
        
        # Contrast control
        contrast_label = Gtk.Label(label="Contrast (0.1 - 3.0)")
        vbox.pack_start(contrast_label, False, False, 0)
        
        self.contrast_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0.1, 3.0, 0.05)
        self.contrast_scale.set_value(1.0)
        self.contrast_scale.set_digits(2)
        self.contrast_scale.connect("value-changed", self.on_contrast_changed)
        vbox.pack_start(self.contrast_scale, False, False, 0)
        
        # Brightness control
        brightness_label = Gtk.Label(label="Brightness (0.1 - 2.0)")
        vbox.pack_start(brightness_label, False, False, 0)
        
        self.brightness_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0.1, 2.0, 0.05)
        self.brightness_scale.set_value(1.0)
        self.brightness_scale.set_digits(2)
        self.brightness_scale.connect("value-changed", self.on_brightness_changed)
        vbox.pack_start(self.brightness_scale, False, False, 0)
        
        # Apply button
        apply_btn = Gtk.Button(label="Apply Settings")
        apply_btn.connect("clicked", self.on_apply_clicked)
        vbox.pack_start(apply_btn, False, False, 10)
        
        # Status label
        self.status_label = Gtk.Label(label="Ready")
        vbox.pack_start(self.status_label, False, False, 0)
        
        # Load saved values if any
        self.load_settings()
        
    def on_gamma_changed(self, scale):
        self.gamma_value = scale.get_value()
        
    def on_contrast_changed(self, scale):
        self.contrast_value = scale.get_value()
        
    def on_brightness_changed(self, scale):
        self.brightness_value = scale.get_value()
        
    def on_apply_clicked(self, button):
        self.save_settings()
        try:
            cmd = f"wl-gammactl -g {self.gamma_value:.2f} -c {self.contrast_value:.2f} -b {self.brightness_value:.2f}"
            subprocess.run(cmd, shell=True, check=True)
            self.status_label.set_text("Settings applied successfully")
        except subprocess.CalledProcessError as e:
            self.status_label.set_text(f"Error: {str(e)}")
    
    def save_settings(self):
        try:
            with open(GLib.get_user_config_dir() + "/wl-gamma-settings.conf", "w") as f:
                f.write(f"{self.gamma_value:.2f}\n")
                f.write(f"{self.contrast_value:.2f}\n")
                f.write(f"{self.brightness_value:.2f}\n")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_settings(self):
        try:
            with open(GLib.get_user_config_dir() + "/wl-gamma-settings.conf", "r") as f:
                lines = f.readlines()
                if len(lines) >= 3:
                    self.gamma_value = float(lines[0].strip())
                    self.contrast_value = float(lines[1].strip())
                    self.brightness_value = float(lines[2].strip())
                    
                    self.gamma_scale.set_value(self.gamma_value)
                    self.contrast_scale.set_value(self.contrast_value)
                    self.brightness_scale.set_value(self.brightness_value)
        except FileNotFoundError:
            pass  # First run, use defaults
        except Exception as e:
            print(f"Error loading settings: {e}")

win = GammaControlApp()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
