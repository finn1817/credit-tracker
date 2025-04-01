import os
import sys
import time
import subprocess
import ctypes
import winreg
import random
from tkinter import Tk, Canvas, Label, PhotoImage, Frame
from threading import Thread
from PIL import Image, ImageTk

class InstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Poe Credit Tracker Installer")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#1E1E2E")
        
        # center window
        self.center_window()
        
        # set window icon
        if os.path.exists("icon.ico"):
            self.root.iconbitmap("icon.ico")
        
        # make the header
        self.header_frame = Frame(root, bg="#1E1E2E", height=100)
        self.header_frame.pack(fill="x", pady=(20, 0))
        
        self.title_label = Label(self.header_frame, 
                                text="Poe Credit Tracker", 
                                font=("Segoe UI", 24, "bold"), 
                                fg="#CBA6F7", bg="#1E1E2E")
        self.title_label.pack(pady=(10, 0))
        
        self.subtitle_label = Label(self.header_frame, 
                                   text="Enhanced Edition Installation", 
                                   font=("Segoe UI", 14), 
                                   fg="#A6E3A1", bg="#1E1E2E")
        self.subtitle_label.pack(pady=(0, 10))
        
        # create main frame
        self.main_frame = Frame(root, bg="#1E1E2E")
        self.main_frame.pack(fill="both", expand=True, padx=40, pady=20)
        
        # make canvas for progress visualization
        self.canvas_frame = Frame(self.main_frame, bg="#313244", bd=0, highlightthickness=0)
        self.canvas_frame.pack(fill="both", expand=True, pady=10)
        
        self.canvas = Canvas(self.canvas_frame, bg="#313244", bd=0, highlightthickness=0, height=250)
        self.canvas.pack(fill="both", expand=True, padx=2, pady=2)
        
        # the status label
        self.status_frame = Frame(root, bg="#1E1E2E", height=50)
        self.status_frame.pack(fill="x", side="bottom", pady=20)
        
        self.status_label = Label(self.status_frame, 
                                 text="Preparing installation...", 
                                 font=("Segoe UI", 10), 
                                 fg="#F5E0DC", bg="#1E1E2E")
        self.status_label.pack()
        
        self.detail_label = Label(self.status_frame, 
                                 text="", 
                                 font=("Segoe UI", 9), 
                                 fg="#B4BEFE", bg="#1E1E2E")
        self.detail_label.pack()
        
        # progress variables
        self.progress_width = 600
        self.progress_height = 20
        self.progress_x = 50
        self.progress_y = 220
        
        # draw progress bar background
        self.canvas.create_rectangle(
            self.progress_x, self.progress_y,
            self.progress_x + self.progress_width, self.progress_y + self.progress_height,
            fill="#45475A", outline="")
        
        # progress bar fill
        self.progress_fill = self.canvas.create_rectangle(
            self.progress_x, self.progress_y,
            self.progress_x, self.progress_y + self.progress_height,
            fill="#CBA6F7", outline="")
        
        # progress percentage
        self.progress_text = self.canvas.create_text(
            self.progress_x + self.progress_width // 2, self.progress_y + self.progress_height // 2,
            text="0%", fill="#FFFFFF", font=("Segoe UI", 9, "bold"))
        
        # create particle system
        self.particles = []
        self.max_particles = 50
        
        # start installation in a separate thread
        self.installation_thread = Thread(target=self.run_installation)
        self.installation_thread.daemon = True
        self.installation_thread.start()
        
        # start animation
        self.animate()
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def update_progress(self, value, status, detail=""):
        # update progress bar
        progress_width = (value / 100) * self.progress_width
        self.canvas.coords(self.progress_fill, 
                          self.progress_x, self.progress_y,
                          self.progress_x + progress_width, self.progress_y + self.progress_height)
        self.canvas.itemconfig(self.progress_text, text=f"{value:.1f}%")
        
        # Update status
        self.status_label.config(text=status)
        self.detail_label.config(text=detail)
        
        # add particles
        if random.random() < 0.3:
            self.add_particle(self.progress_x + progress_width, self.progress_y + self.progress_height // 2)
    
    def add_particle(self, x, y):
        if len(self.particles) < self.max_particles:
            color = random.choice(["#CBA6F7", "#F38BA8", "#A6E3A1", "#FAB387", "#89B4FA"])
            size = random.randint(2, 6)
            speed_x = random.uniform(1, 3)
            speed_y = random.uniform(-2, 2)
            life = random.randint(20, 50)
            
            particle = self.canvas.create_oval(x, y, x + size, y + size, fill=color, outline="")
            self.particles.append({
                "id": particle,
                "x": x,
                "y": y,
                "size": size,
                "speed_x": speed_x,
                "speed_y": speed_y,
                "life": life,
                "max_life": life
            })
    
    def animate(self):
        # update particles
        for particle in self.particles[:]:
            particle["x"] += particle["speed_x"]
            particle["y"] += particle["speed_y"]
            particle["life"] -= 1
            
            # calculate opacity based on remaining life
            opacity = particle["life"] / particle["max_life"]
            
            # update particle position
            self.canvas.coords(
                particle["id"],
                particle["x"], particle["y"],
                particle["x"] + particle["size"], particle["y"] + particle["size"]
            )
            
            # remove dead particles
            if particle["life"] <= 0 or particle["x"] > 700:
                self.canvas.delete(particle["id"])
                self.particles.remove(particle)
        
        # draw code rain effect
        if random.random() < 0.2:
            x = random.randint(50, 650)
            y = 50
            color = random.choice(["#CBA6F7", "#A6E3A1", "#89B4FA"])
            text = random.choice(["import", "class", "def", "for", "while", "if", "else", "return", "try", "except"])
            text_id = self.canvas.create_text(x, y, text=text, fill=color, font=("Courier New", 9))
            
            def animate_text(text_id, y=50, speed=2):
                if y < 200:
                    self.canvas.coords(text_id, x, y + speed)
                    self.root.after(50, lambda: animate_text(text_id, y + speed, speed))
                else:
                    self.canvas.delete(text_id)
            
            animate_text(text_id)
        
        # continue animation
        self.root.after(30, self.animate)
    
    def run_installation(self):
        try:
            # step 1: check python version
            self.update_progress(5, "Checking Python version...")
            time.sleep(1)
            
            python_version = sys.version_info
            if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
                self.update_progress(10, "Warning: Python 3.7+ recommended", 
                                    f"Current version: {python_version.major}.{python_version.minor}.{python_version.micro}")
                time.sleep(2)
            else:
                self.update_progress(10, "Python version check passed", 
                                    f"Using Python {python_version.major}.{python_version.minor}.{python_version.micro}")
                time.sleep(1)
            
            # step 2: check for required modules
            self.update_progress(15, "Checking required modules...")
            time.sleep(1)
            
            required_modules = ["tkinter", "matplotlib", "numpy", "tkcalendar", "pillow"]
            missing_modules = []
            
            for module in required_modules:
                try:
                    if module == "tkinter":
                        import tkinter
                    elif module == "matplotlib":
                        import matplotlib
                    elif module == "numpy":
                        import numpy
                    elif module == "tkcalendar":
                        import tkcalendar
                    elif module == "pillow":
                        import PIL
                    
                    self.update_progress(15 + (25 - 15) * (required_modules.index(module) + 1) / len(required_modules),
                                        f"Checking module: {module}", "✓ Found")
                    time.sleep(0.5)
                except ImportError:
                    missing_modules.append(module)
                    self.update_progress(15 + (25 - 15) * (required_modules.index(module) + 1) / len(required_modules),
                                        f"Checking module: {module}", "✗ Missing")
                    time.sleep(0.5)
            
            # step 3: install missing modules
            if missing_modules:
                self.update_progress(25, "Installing missing modules...")
                
                for i, module in enumerate(missing_modules):
                    real_name = module
                    if module == "pillow":
                        real_name = "Pillow"
                    
                    progress = 25 + (60 - 25) * (i + 1) / len(missing_modules)
                    self.update_progress(progress, f"Installing {module}...", "This may take a moment")
                    
                    # run pip install
                    process = subprocess.Popen(
                        [sys.executable, "-m", "pip", "install", real_name],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    # show installation progress
                    for line in process.stdout:
                        self.update_progress(progress, f"Installing {module}...", line.strip())
                        time.sleep(0.1)
                    
                    process.wait()
                    
                    if process.returncode == 0:
                        self.update_progress(progress, f"Installed {module}", "✓ Success")
                    else:
                        self.update_progress(progress, f"Failed to install {module}", "✗ Error")
                        for line in process.stderr:
                            print(f"Error: {line.strip()}")
                    
                    time.sleep(1)
            else:
                self.update_progress(40, "All required modules are installed", "✓ Ready")
                time.sleep(1)
            
            # step 4: make a desktop shortcut
            self.update_progress(70, "Creating desktop shortcut...")
            time.sleep(1)
            
            try:
                # get desktop path
                desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                
                # Create .bat file for launching
                bat_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "launch_poe_tracker.bat")
                with open(bat_path, "w") as f:
                    f.write(f'@echo off\n')
                    f.write(f'cd "{os.path.dirname(os.path.abspath(__file__))}"\n')
                    f.write(f'start "" "{sys.executable}" poe_tracker.py\n')
                
                # create shortcut
                shortcut_path = os.path.join(desktop_path, "Poe Credit Tracker.lnk")
                
                # create shortcut using PowerShell
                ps_command = f'''
                $WshShell = New-Object -ComObject WScript.Shell
                $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
                $Shortcut.TargetPath = "{bat_path}"
                $Shortcut.WorkingDirectory = "{os.path.dirname(os.path.abspath(__file__))}"
                $Shortcut.Description = "Poe Credit Tracker"
                $Shortcut.IconLocation = "{sys.executable}, 0"
                $Shortcut.Save()
                '''
                
                # execute PowerShell command
                subprocess.run(["powershell", "-Command", ps_command], check=True)
                
                self.update_progress(80, "Desktop shortcut created", "✓ Success")
            except Exception as e:
                self.update_progress(80, "Failed to create desktop shortcut", f"Error: {str(e)}")
            
            time.sleep(1)
            
            # step 5: create icon file
            self.update_progress(85, "Creating application icon...")
            
            try:
                # Simple icon creation using PIL
                from PIL import Image, ImageDraw
                
                # create a 64x64 image with a transparent background
                icon = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
                draw = ImageDraw.Draw(icon)
                
                # draw a circle
                draw.ellipse((4, 4, 60, 60), fill=(203, 166, 247, 255))
                draw.ellipse((8, 8, 56, 56), fill=(30, 30, 46, 255))
                draw.ellipse((16, 16, 48, 48), fill=(166, 227, 161, 255))
                
                # save the icon
                icon.save("poe_icon.ico")
                
                self.update_progress(90, "Application icon created", "✓ Success")
            except Exception as e:
                self.update_progress(90, "Failed to create icon", f"Error: {str(e)}")
            
            time.sleep(1)
            
            # step 6: finalize installation
            self.update_progress(95, "Finalizing installation...")
            time.sleep(1)
            
            self.update_progress(100, "Installation complete!", "✓ Ready to use")
            time.sleep(1)
            
            # show completion message
            self.status_label.config(text="Installation complete! You can now close this window.")
            self.detail_label.config(text="Launch from desktop shortcut or run poe_tracker.py directly")
            
        except Exception as e:
            self.update_progress(100, "Installation failed", f"Error: {str(e)}")
            print(f"Installation error: {str(e)}")

if __name__ == "__main__":
    # enable high DPI awareness
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    root = Tk()
    app = InstallerGUI(root)
    root.mainloop()
  
