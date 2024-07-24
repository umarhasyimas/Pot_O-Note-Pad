import os
import sys
import subprocess
import shutil
import platform
import ctypes

def check_and_install_python():
    try:
        python_version = subprocess.check_output(['python', '--version'], stderr=subprocess.STDOUT).decode().strip()
        print(f"Python is installed: {python_version}")
    except subprocess.CalledProcessError:
        print("Python is not installed. Please install Python to continue.")
        sys.exit(1)

def check_and_install_pip():
    try:
        pip_version = subprocess.check_output([sys.executable, '-m', 'pip', '--version']).decode().strip()
        print(f"pip is installed: {pip_version}")
    except subprocess.CalledProcessError:
        print("pip is not installed. Installing pip...")
        subprocess.check_call([sys.executable, '-m', 'ensurepip', '--upgrade'])

def install_dependencies():
    required_packages = [
        'PyQt5',
        'QScintilla'
    ]

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def move_script_to_program_files(script_path):
    if platform.system() == "Windows":
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        target_dir = os.path.join(program_files, "Pot-O_Note_Pad")
    else:
        target_dir = "/usr/local/bin/Pot-O_Note_Pad"

    os.makedirs(target_dir, exist_ok=True)
    shutil.copy(script_path, target_dir)
    
    return target_dir

def create_shortcut(target_dir, icon_path):
    if platform.system() == "Windows":
        shortcut_path = os.path.join(os.path.expanduser("~"), "Desktop", "Pot-O_Note_Pad.lnk")
        target_path = os.path.join(target_dir, "Pot-O_Note_Pad_v0.0.1-beta.py")

        shell = ctypes.windll.shell32
        shortcut = shell.SHCreateShortcut(shortcut_path)
        shortcut.TargetPath = target_path
        shortcut.IconLocation = icon_path
        shortcut.Save()
    else:
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        shortcut_path = os.path.join(desktop_dir, "Pot-O_Note_Pad.desktop")
        target_path = os.path.join(target_dir, "Pot-O_Note_Pad_v0.0.1-beta.py")

        with open(shortcut_path, 'w') as shortcut:
            shortcut.write(f"[Desktop Entry]\n")
            shortcut.write(f"Version=1.0\n")
            shortcut.write(f"Name=Pot-O Note Pad\n")
            shortcut.write(f"Exec=python3 {target_path}\n")
            shortcut.write(f"Icon={icon_path}\n")
            shortcut.write(f"Terminal=false\n")
            shortcut.write(f"Type=Application\n")
            shortcut.write(f"Categories=Utility;Application;\n")
        
        os.chmod(shortcut_path, 0o755)

def main():
    script_path = os.path.abspath(sys.argv[0])
    icon_path = os.path.join(os.path.dirname(script_path), "/images/pea.png")  # Adjust the icon path if needed

    check_and_install_python()
    check_and_install_pip()
    install_dependencies()
    
    target_dir = move_script_to_program_files(script_path)
    
    create_shortcut(target_dir, icon_path)
    
    print("Installation complete!")

if __name__ == "__main__":
    main()
