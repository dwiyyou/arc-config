#!/usr/bin/env python3
import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

class HyprlandConfigGUI(Gtk.Window):
    def __init__(self):
        super().__init__(title="Hyprland Configuration Tool")
        self.set_default_size(1000, 700)
        
        # Path to Hyprland config file
        self.config_path = os.path.expanduser("~/.config/hypr/hyprland.conf")
        
        # Load current config
        self.config_data = self.load_config()
        
        # Create main interface
        self.create_main_interface()
        
    def load_config(self):
        """Load the current Hyprland config file"""
        try:
            with open(self.config_path, 'r') as f:
                return f.readlines()
        except FileNotFoundError:
            print("Hyprland config file not found!")
            return []
    
    def save_config(self):
        """Save changes to the config file"""
        with open(self.config_path, 'w') as f:
            f.writelines(self.config_data)
        # You might want to add a way to reload Hyprland config here
    
    def create_main_interface(self):
        """Create the main application interface"""
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.add(main_box)
        
        # Sidebar with navigation
        sidebar = Gtk.ListBox()
        sidebar.set_size_request(200, -1)
        main_box.pack_start(sidebar, False, False, 0)
        
        # Add sidebar items
        sections = [
            "Keybindings", "Animations", "Blur Effects", 
            "Window Rules", "Workspaces", "Monitor Setup", "Environment"
        ]
        
        for section in sections:
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=section)
            row.add(label)
            sidebar.add(row)
        
        # Main content area
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(300)
        
        # Create each section
        self.create_keybindings_section()
        self.create_animations_section()
        self.create_blur_section()
        self.create_window_rules_section()
        self.create_workspaces_section()
        self.create_monitor_section()
        self.create_environment_section()
        
        main_box.pack_start(self.stack, True, True, 0)
        
        # Connect sidebar selection to stack
        sidebar.connect("row-selected", self.on_sidebar_selected)
    
    def on_sidebar_selected(self, listbox, row):
        """Handle sidebar selection changes"""
        if row is not None:
            index = row.get_index()
            self.stack.set_visible_child_name(str(index))
    
    def create_keybindings_section(self):
        """Create the keybindings configuration section"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        # Scrollable area
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        # Keybindings list
        self.keybind_list = Gtk.ListBox()
        scrolled.add(self.keybind_list)
        
        # Add existing keybindings
        self.load_keybindings()
        
        # Add new keybinding button
        add_btn = Gtk.Button(label="Add New Keybinding")
        add_btn.connect("clicked", self.on_add_keybinding)
        
        box.pack_start(scrolled, True, True, 0)
        box.pack_start(add_btn, False, False, 0)
        
        self.stack.add_titled(box, "0", "Keybindings")
    
    def load_keybindings(self):
        """Load existing keybindings from config"""
        # Parse the config file for bind directives
        for line in self.config_data:
            if line.strip().startswith("bind"):
                parts = line.strip().split("=", 1)
                if len(parts) == 2:
                    keybind, action = parts
                    self.add_keybinding_row(keybind.strip(), action.strip())
    
    def add_keybinding_row(self, keybind, action):
        """Add a keybinding row to the list"""
        row = Gtk.ListBoxRow()
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        key_entry = Gtk.Entry()
        key_entry.set_text(keybind)
        
        action_entry = Gtk.Entry()
        action_entry.set_text(action)
        
        del_btn = Gtk.Button.new_from_icon_name("edit-delete", Gtk.IconSize.BUTTON)
        del_btn.connect("clicked", self.on_delete_keybinding, row)
        
        box.pack_start(key_entry, True, True, 0)
        box.pack_start(action_entry, True, True, 0)
        box.pack_start(del_btn, False, False, 0)
        
        row.add(box)
        self.keybind_list.add(row)
    
    def on_add_keybinding(self, button):
        """Handle adding a new keybinding"""
        self.add_keybinding_row("bind ", "")
    
    def on_delete_keybinding(self, button, row):
        """Handle deleting a keybinding"""
        self.keybind_list.remove(row)
    
    # Similar methods would be created for other sections
    def create_animations_section(self):
        """Create the animations configuration section"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        # Animation controls would go here
        label = Gtk.Label(label="Animation Settings")
        box.pack_start(label, False, False, 0)
        
        self.stack.add_titled(box, "1", "Animations")
    
    def create_blur_section(self):
        """Create the blur effects section"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        # Blur controls would go here
        label = Gtk.Label(label="Blur Effects Settings")
        box.pack_start(label, False, False, 0)
        
        self.stack.add_titled(box, "2", "Blur Effects")
    
    def create_window_rules_section(self):
        """Create the window rules section"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        # Window rule controls would go here
        label = Gtk.Label(label="Window Rules Settings")
        box.pack_start(label, False, False, 0)
        
        self.stack.add_titled(box, "3", "Window Rules")
    
    def create_workspaces_section(self):
        """Create the workspaces section"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        # Workspace controls would go here
        label = Gtk.Label(label="Workspace Settings")
        box.pack_start(label, False, False, 0)
        
        self.stack.add_titled(box, "4", "Workspaces")
    
    def create_monitor_section(self):
        """Create the monitor setup section"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        # Monitor controls would go here
        label = Gtk.Label(label="Monitor Setup")
        box.pack_start(label, False, False, 0)
        
        self.stack.add_titled(box, "5", "Monitor Setup")
    
    def create_environment_section(self):
        """Create the environment variables section"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        # Environment variable controls would go here
        label = Gtk.Label(label="Environment Variables")
        box.pack_start(label, False, False, 0)
        
        self.stack.add_titled(box, "6", "Environment")
    
    def on_save(self, button):
        """Handle save button click"""
        self.save_config()
        self.show_save_notification()
    
    def show_save_notification(self):
        """Show a save notification"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Configuration Saved"
        )
        dialog.format_secondary_text("Your changes have been saved to the config file.")
        dialog.run()
        dialog.destroy()

def main():
    app = HyprlandConfigGUI()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
