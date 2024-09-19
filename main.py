import pygame
import pygame.freetype
import os
import json
import sys

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Terminal")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
GREEN = (100, 255, 100)
BLUE = (100, 100, 255)
YELLOW = (100, 255, 255)
RED = (255, 100, 100)

# Font setup
FONT_SIZE = 20
font = pygame.freetype.SysFont('Courier', FONT_SIZE)

# Terminal setup
terminal_height = HEIGHT // 2
terminal_surface = pygame.Surface((WIDTH, terminal_height))
terminal_rect = terminal_surface.get_rect(bottom=HEIGHT)

# Top half setup
top_half_surface = pygame.Surface((WIDTH, terminal_height))
top_half_rect = top_half_surface.get_rect(top=0)

# Input setup
input_text = ""
location = "~"
input_prefix = "$ "
cursor_visible = True
cursor_timer = 0

# Global variables
location = "~"
command_history = []
top_half_text = [
    {"text": "You have been dropped into an unknown filesystem.", "color": WHITE},
    {"text": "You have no memory of how you got here, but you know some things:", "color": WHITE},
    {"text": "- Look around you by typing 'ls'", "color": GREEN},
    {"text": "- Read scrolls (.txt) by typing 'cat file_name.txt'", "color": GREEN},
    {"text": "- Pickup items using 'cat file_name'", "color": GREEN},
   
]

# File system structure
with open("level_1/files.json", "r") as f:
    print("files found")
    files = json.load(f)

# Global variables
location = "~"
command_history = []
inventory = [] # Stores items for player in a list

# Command functions
def cmd_ls(args):
    files_in_location = []
    for file in files:
        if file["path"].startswith(location) and file["path"] != location:
            relative_path = file["path"][len(location):].strip('/')
            components = relative_path.split('/')
            if len(components) == 1 and components[0]:
                entry = components[0] + ('/' if file["is_directory"] else '')
                color = BLUE if file["is_directory"] else GREEN
                files_in_location.append({"text": entry, "color": color})
    if files_in_location:
        command_history.append(f"Files in directory {location}:")
        return files_in_location
    else:
        return ["ls: no files or directories found in this directory"]

def cmd_cd(args):
    global location
    if not args:
        return ["Usage: cd <directory>"]

    inp = args[0]        

    if location[-1] != "/":
        inp = "/" + inp
    
    if inp == "..":
        new_loc = "/".join(location.split("/")[:-2]) + "/"
        if new_loc == "~/":
            new_loc = "~"
    elif inp == "~":
        new_loc = "~"
    else:
        new_loc = location + inp if (location.endswith('/') or location == "~") else location + '/' + inp
        new_loc = new_loc if new_loc.endswith('/') else new_loc + '/'

    for file in files:
        if file["path"] == new_loc and file["is_directory"]:
            if file["access"] == "open":
                location = new_loc
                return []
            else:
                return [f"cd: {inp} is locked"]
    
    return [f"cd: {inp}: No such file or directory"]

def cmd_clear(args):
    global command_history
    command_history.clear()
    return []

def cmd_pwd(args):
    return [location]

def cmd_cat(args): # Edited cmd_cat for key functionality
    global location
    global files
    global inventory

    if not args:
        return [{"text": "Usage: cat <.txt file> or cat <item>", "color": YELLOW}]
    
    inp = args[0]
    target = location + inp
    
    for file in files:
        if file["path"] == target:
            # If the player is trying to 'cat' the key, pick it up instead of just reading
            if file["path"] == "~/ruins/hole/key":
                if "key" not in inventory:
                    inventory.append("key")
                    top_half_text.append({"text": "*You pick up the KEY! KEY can be USED with \"mv\"*", "color": GREEN})
                    return []
                else:
                    return [{"text": "You already have the key.", "color": YELLOW}]
            
            # For normal txt files, show the content
            print_to_top(file["content"], color=GREEN)
            return []  # Stop once we find the file and display its content

    # If we loop through all files and don'tgg find the target
    return [{"text": f"File not found: {inp}", "color": RED}]

def cmd_mkdir(args):
    global location
    global files
    if not args:
        return ["Usage: mkdir <new directory>"]
    
    if location[-1] == "/":
         new_dir = location
    else:
        new_dir = location + "/"
    # Construct the new directory path
    inp = new_dir + args[0] + "/"
    
    # Append the new directory to the files list
    files.append({"path": inp, "is_directory": True, "access": "open"})
    return [f"New directory {inp} added"]

def cmd_echo(args):
    global location
    global files
    if len(args) == 1:
        echo_text = args[0]
        return [echo_text]
    
    elif len(args) == 3:
        if args[1] == ">>":
            target_file = location + args[2]
            for file in files:
                if target_file in file["path"]:
                    file["content"] = file["content"] +"\n" + args[0]
                    return [f"{args[0]} added to {args[2]}"]
            return [f"{args[0]} added to {args[2]}"]
        else:
            return ["Usage 1: echo <text> to print in terminal" , "Usage 2: echo <text> >> <target_file> to append text to file"] 
          
    else:
        return ["Usage 1: echo <text> to print in terminal" , "Usage 2: echo <text> >> <target_file> to append text to file"]

def cmd_mv(args):
    global location
    global files
    global inventory
    global top_half_text  # Access to top text display
    
    if len(args) != 2:
        return ["Usage: mv <file> <new location>"]

    old_file = location + args[0]
    new_file = args[1]
    
    # Check if the player is moving the key and has it in their inventory
    if "key" in inventory and args[0] == "key" and new_file == "~/exit":
        # Unlock the exit
        for file in files:
            if file["path"] == "~/exit/":
                file["access"] = "open"
                inventory.remove("key")  # Remove the key from the inventory after it's used
                                
                for file_entry in files:
                    if file_entry["path"] == "~/ruins/hole/key":
                        content_lines = file_entry["content"].split("\n")
                        for line in content_lines:
                            top_half_text.append({"text": line, "color": GREEN})

                return []  # Return empty so nothing is printed in the terminal

    # Handle regular mv operations if it's not the key
    exist = False
    for file in files:
        if file["path"] == old_file:
            exist = True
            break

    if exist:
        if "/" in new_file:
            target_dir = new_file.rsplit("/", 1)[0] + "/"
        else:
            target_dir = "~"
        
        # Check if the target directory exists and is open
        for file in files:
            if file["path"] == target_dir and file["is_directory"]:
                if file["access"] == "open":
                    files = [file for file in files if file["path"] != old_file]  # Remove old file
                    files.append({"path": new_file, "is_directory": False, "access": "open"})  # Add new file location
                    return [f"{old_file} moved to {new_file}"]
                else:
                    return [f"{target_dir} is locked."]
    
    return [f"mv: {old_file}: File not found"]
    
def cmd_touch(args):
    global location
    global files
    if not args:
        return ["Usage: touch <new_file.file_type>"]


    if location[-1] == "/":
        dir_for_file = location  
    else:
        dir_for_file = location + "/"
    
    new_file = {"path": dir_for_file + args[0], "is_directory": False, "access": "open"}


    if new_file not in files:
        files.append(new_file)
        return ["File created"]

    else:
        return ["File alreade exists."]
        

def cmd_exit(args):
    pygame.quit()
    sys.exit()

# Command dispatcher
commands = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "clear": cmd_clear,
    "pwd": cmd_pwd,
    "cat": cmd_cat,
    "mkdir": cmd_mkdir,
    "mv": cmd_mv,
    "touch": cmd_touch,
    "exit": cmd_exit,
    "echo": cmd_echo
    }

def process_command(user_input):
    parts = user_input.split()
    if not parts:
        return
    
    cmd = parts[0].lower()
    args = parts[1:]
    
    if cmd in commands:
        result = commands[cmd](args)
        command_history.extend(result)
    else:
        command_history.append({"text": f"Command not found: {cmd}", "color": RED})

def draw_terminal():
    terminal_surface.fill(BLACK)
    
    history_start_y = terminal_height - FONT_SIZE * 2 - 20
    for line in reversed(command_history[-9:]):
        if isinstance(line, dict):
            font.render_to(terminal_surface, (10, history_start_y), line["text"], line["color"])
        else:
            font.render_to(terminal_surface, (10, history_start_y), line, WHITE)
        history_start_y -= FONT_SIZE
    
    input_y = terminal_height - FONT_SIZE - 10
    font.render_to(terminal_surface, (10, input_y), location + input_prefix + input_text, WHITE)
    
    if cursor_visible:
        cursor_x = 10 + font.get_rect(location + input_prefix + input_text[:len(input_text)])[2]
        pygame.draw.line(terminal_surface, WHITE, (cursor_x, input_y),
                         (cursor_x, input_y + FONT_SIZE - 2), 2)
    
    screen.blit(terminal_surface, terminal_rect)

def draw_top_half():
    top_half_surface.fill(GRAY)
    
    for i, line in enumerate(top_half_text[-12:]):  # Display up to 12 lines
        font.render_to(top_half_surface, (10, i * FONT_SIZE), line["text"], line["color"])
    
    screen.blit(top_half_surface, top_half_rect)

def print_to_top(text, color=WHITE):
    lines = text.split('\n')
    for line in lines:
        top_half_text.append({"text": line, "color": color})

running = True
clock = pygame.time.Clock()
input_text = ""

#This is the main game loop

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                process_command(input_text)
                input_text = ""
            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            else:
                input_text += event.unicode
    #This section handles cursor blinking
    cursor_timer += clock.get_time()
    if cursor_timer >= 500:
        cursor_visible = not cursor_visible
        cursor_timer = 0
    #Draws the screen 
    screen.fill(GRAY)
    draw_top_half()
    draw_terminal()
    pygame.display.flip()
    
    clock.tick(60)

pygame.quit()
hello
