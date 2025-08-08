#!/usr/bin/env python3

import curses
import subprocess
from curses import wrapper

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

def display_menu(stdscr, selected_row_idx, packages):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    # Judul
    title = "Arch Linux Package Manager (TUI)"
    stdscr.addstr(0, w//2 - len(title)//2, title, curses.A_BOLD)
    
    # Menu utama
    menu_items = [
        "Install Package",
        "Remove Package",
        "Upgrade All Packages",
        "List Installed Packages",
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

def install_package(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    curses.echo()
    stdscr.addstr(0, 0, "Enter package name to install: ")
    package = stdscr.getstr().decode('utf-8')
    curses.noecho()
    
    if package:
        stdscr.addstr(2, 0, f"Installing {package}...")
        stdscr.refresh()
        output = run_command(f"sudo pacman -S --noconfirm {package}")
        stdscr.addstr(4, 0, output)
    else:
        stdscr.addstr(2, 0, "No package name entered!")
    
    stdscr.addstr(h-1, 0, "Press any key to continue...")
    stdscr.getch()

def remove_package(stdscr, packages):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    if not packages:
        stdscr.addstr(0, 0, "No installed packages found!")
        stdscr.addstr(h-1, 0, "Press any key to continue...")
        stdscr.getch()
        return
    
    selected = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Select package to remove (Enter to confirm, q to cancel):")
        
        for idx, pkg in enumerate(packages):
            if idx == selected:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(idx+2, 0, pkg)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(idx+2, 0, pkg)
        
        key = stdscr.getch()
        
        if key == curses.KEY_UP and selected > 0:
            selected -= 1
        elif key == curses.KEY_DOWN and selected < len(packages)-1:
            selected += 1
        elif key == ord('\n'):
            package = packages[selected]
            stdscr.addstr(len(packages)+2, 0, f"Removing {package}...")
            stdscr.refresh()
            output = run_command(f"sudo pacman -R --noconfirm {package}")
            stdscr.addstr(len(packages)+3, 0, output)
            stdscr.addstr(len(packages)+4, 0, "Press any key to continue...")
            stdscr.getch()
            break
        elif key == ord('q'):
            break
    
def upgrade_packages(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    stdscr.addstr(0, 0, "Upgrading all packages...")
    stdscr.refresh()
    output = run_command("sudo pacman -Syu --noconfirm")
    stdscr.addstr(2, 0, output)
    
    stdscr.addstr(h-1, 0, "Press any key to continue...")
    stdscr.getch()

def list_installed_packages(stdscr):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    
    stdscr.addstr(0, 0, "Fetching installed packages...")
    stdscr.refresh()
    output = run_command("pacman -Qe | awk '{print $1}'")
    packages = output.splitlines()
    
    stdscr.clear()
    stdscr.addstr(0, 0, "Installed Packages (q to return):")
    
    for idx, pkg in enumerate(packages):
        if idx < h-2:
            stdscr.addstr(idx+1, 0, pkg)
    
    stdscr.addstr(h-1, 0, "Press q to return...")
    while stdscr.getch() != ord('q'):
        pass
    
    return packages

def main(stdscr):
    # Inisialisasi warna
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    
    current_row = 0
    packages = []
    
    while True:
        display_menu(stdscr, current_row, packages)
        
        key = stdscr.getch()
        
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < 4:
            current_row += 1
        elif key == ord('\n'):
            if current_row == 0:  # Install
                install_package(stdscr)
            elif current_row == 1:  # Remove
                packages = list_installed_packages(stdscr)
                remove_package(stdscr, packages)
            elif current_row == 2:  # Upgrade
                upgrade_packages(stdscr)
            elif current_row == 3:  # List
                packages = list_installed_packages(stdscr)
            elif current_row == 4:  # Exit
                break
        elif key == ord('q'):
            break

if __name__ == "__main__":
    wrapper(main)
