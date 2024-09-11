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
    {"text": "You have no memory of how you got here, but you know 2 things:", "color": WHITE},
    {"text": "- Look around you by typing ls", "color": GREEN},
    {"text": "- Read scrolls (.txt) by typing cat file_name.txt", "color": GREEN}
]

# File system structure
files = [
    {"path": "~", "is_directory": True, "access": "open"},
    {"path": "~note.txt", "is_directory": False, "access": "open"},
    {"path": "~/ruins/", "is_directory": True, "access": "open"},
    {"path": "~/ruins/chest.txt", "is_directory": False, "access": "open"},
    {"path": "~/exit/", "is_directory": True, "access": "locked"},
    {"path": "~/ruins/hole/key", "is_directory": False, "access": "open"}
]

# Global variables
location = "~"
command_history = []

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
    
    return files_in_location

def cmd_cd(args):
    global location
    if not args:
        return ["Usage: cd <directory>"]
    
    if str(args[0]) == "..":
        if location == "~":
            return location
        else: 
            location = "/".join(location.rstrip("/").split("/")[:-1])
            return location

    inp = args[0]
    print(inp)
    print(location[-1])
    if location[-1] != "/":
        inp = "/" + inp
    
    if inp == "..":
        new_loc = "/".join(location.split("/")[:-2]) + "/"
        new_loc = "~" if new_loc == "" else new_loc
    else:
        new_loc = location + inp if (location.endswith('/') or location == "~") else location + '/' + inp
        new_loc = new_loc if new_loc.endswith('/') else new_loc + '/'
    print(new_loc)
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

def cmd_cat(args):
    global location
    if not args:
        return [{"text": "Usage: cat <.txt file>", "color": YELLOW}]
    inp = args[0]
    target = location + inp

    files_in_location = [f["path"] for f in files 
                         if f["path"].startswith(location) 
                         and not f["is_directory"]
                         and "/" not in f["path"][len(location):]]
    
    try:
        with open(inp, 'r') as file:
            content = file.read()
        print_to_top(content, GREEN)
        return []
    except FileNotFoundError:
        return [{"text": f"File not found: {inp}", "color": RED}]

def cmd_mkdir(args):
    global location
    global files
    if not args:
        return ["Usage: mkdir <new directory>"]
    
    if location[-1] == "/":
         print("location ends with /")  
         new_dir = location
    else:
        new_dir = location + "/"
        print(new_dir)
    # Construct the new directory path
    inp = new_dir + args[0] + "/"
    
    # Append the new directory to the files list
    files.append({"path": inp, "is_directory": True, "access": "open"})
    return ["Path added"]

def cmd_mv(args):
    global location
    old_loc = args[0]
    new_loc = args[1]
    print(old_loc, new_loc)
    return []

def cmd_touch(args):
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
