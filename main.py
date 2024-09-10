import pygame
import pygame.freetype
import os

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Terminal")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)

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
top_half_text = ["You have been dropped into an unknown filesystem."
    , "You have no memory of how you got here, but you know 2 things:"
    , "- Look around you by typing ls"
    , "- Read scrolls (.txt) by typing cat file_name.txt"
    ]

# File system structure
files = [
    {"path": "~", "is_directory": True},
    {"path": "~note.txt", "is_directory": False},
    {"path": "~/ruins/", "is_directory": True},
    {"path": "~/ruins/chest.txt", "is_directory": False},
    {"path": "~/exit/", "is_directory": True},
    {"path": "~/ruins/hole/key", "is_directory": False}
]

# Global variables
location = "~"
command_history = []

# Command functions
def cmd_ls(args):
    files_in_location = []
    for file in files:
        if file["path"].startswith(location) and file["path"] != location:
            # Remove the current location from the file path
            relative_path = file["path"][len(location):]
            relative_path = relative_path.strip('/')
            components = relative_path.split('/')
            # Check if the file is directly under the current location
            if len(components) == 1 and components[0]:
                # Append '/' to directories for clarity
                entry = components[0] + ('/' if file["is_directory"] else '')
                files_in_location.append(entry)
    files_str = " ".join(files_in_location)
    print(files_str)
    return [files_str]

def cmd_cd(args):
    global location
    if not args:
        return ["Usage: cd <directory>"]
    
    if str(args[0]) == "..":
        if location == "~":
            return location
        else: 
            location = "/".join(location.rstrip("/").split("/")[:-1]) + "/"
            return location

    inp = args[0]
    if inp == "..":
        new_loc = "/".join(location.split("/")[:-2]) + "/"
        new_loc = "~" if new_loc == "" else new_loc
    else:
        new_loc = location + inp if (location.endswith('/') or location == "~") else location + '/' + inp
        new_loc = new_loc if new_loc.endswith('/') else new_loc + '/'
    
    for file in files:
        if file["path"] == new_loc and file["is_directory"]:
            location = new_loc
            return []
    
    return [f"cd: {inp}: No such file or directory"]

def cmd_clear(args):
    global command_history
    command_history.clear()
    return []

def cmd_pwd(args):
    return [location]

def cmd_cat(args):
    global location
    if not args:
        return ["Usage: cat <.txt file>"]
    inp = args[0]
    target = location + inp

    files_in_location = [f["path"] for f in files 
                         if f["path"].startswith(location) 
                         and not f["is_directory"]
                         and "/" not in f["path"][len(location):]]
    
    try:
        with open(inp, 'r') as file:
            content = file.read()
        print_to_top(content)
        return []
    except FileNotFoundError:
        return [f"File not found: {inp}"]

def cmd_mkdir(args):
    global location
    global files
    
    if location[-1] == "/":
         print("location ends with /")  
         new_dir = location
    else:
        new_dir = location + "/"
        print(new_dir)
    # Construct the new directory path
    inp = new_dir + args[0] + "/"
    
    # Append the new directory to the files list
    files.append({"path": inp, "is_directory": True})
    return ["Path added"]

def cmd_mv(args):
    print(args)
    return []

# Command dispatcher
commands = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "clear": cmd_clear,
    "pwd": cmd_pwd,
    "cat": cmd_cat,
    "mkdir": cmd_mkdir,
    "mv": cmd_mv
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
        command_history.append(f"Command not found: {cmd}")

def draw_terminal():
    terminal_surface.fill(BLACK)
    
    history_start_y = terminal_height - FONT_SIZE * 2 - 20
    for line in reversed(command_history[-9:]):
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
        font.render_to(top_half_surface, (10, i * FONT_SIZE), line, WHITE)
    
    screen.blit(top_half_surface, top_half_rect)

def print_to_top(text):
    lines = text.split('\n')
    for line in lines:
        top_half_text.append(line)

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
