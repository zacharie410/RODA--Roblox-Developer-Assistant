from source import (
    CTk,
    CTkFrame,
    CTkLabel,
    CTkButton,
    CTkOptionMenu,
    CTkProgressBar,
    CTkFont,
    set_appearance_mode,
    set_default_color_theme,
    set_widget_scaling
)

from source import (
    ProjectAPI,
    ProjectCreatorHandler,
    ViewProjectsFrame,
    ProjectCreator,
    InstallManager
)
import ctypes
import psutil
import sys
import os
from pathlib import Path
import subprocess

set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

VERSION = "1.0.4"

class App(CTk):
    def __init__(self):
        super().__init__()
        user_home = str(Path.home())
        directory = os.path.join(user_home, "RODAssistant")

        self.version = VERSION

        self.check_folder(directory)
        self.check_folder(os.path.join(directory, "Projects"))
        self.check_folder(os.path.join(directory, "Utility"))
        self.check_folder(os.path.join(directory, "Images"))

        self.api = ProjectAPI(os.path.join(directory, "projects.json"))
        self.server_thread = False

        # configure window
        self.title("RODA: Roblox Developer Assistant v" + VERSION)

                # Set the desired aspect ratio
        self.aspect_ratio = 16 / 9  # For example, 16:9

        # Set the minimum window size
        self.min_width = 800
        self.min_height = int(self.min_width / self.aspect_ratio)

        # Force aspect ratio and minimum size
        self.geometry(f"{self.min_width}x{self.min_height}")
        self.minsize(self.min_width, self.min_height)

        paddingx=0.02
        offsetx=0.01
        paddingy=0.02
        offsety=0.01
        # create sidebar frame
        self.sidebar_frame = CTkFrame(self)
        self.sidebar_frame.place(relwidth=0.25-paddingx, relx=offsetx, relheight=1-paddingy, rely=offsety)

        # create container frame
        self.container_frame = CTkFrame(self, fg_color="transparent")
        self.container_frame.place(relwidth=0.75-paddingx, relx=offsetx + 0.25, relheight=1-paddingy, rely=offsety)


        # create subframes
        self.loading_frame = CTkFrame(self.container_frame)
        self.loading_frame.place_forget()

        self.projects_frame = ViewProjectsFrame(self.container_frame, self.api, self.create_project, self)
        self.projects_frame.place_forget()

        self.project_creator = ProjectCreator(self.container_frame, ProjectCreatorHandler(self.api, self.projects_frame), self.my_projects)
        self.project_creator.place_forget()

        self.install_manager = InstallManager(self.container_frame, self)
        self.install_manager.place_forget()

        # create slider and progressbar frame
        self.load_label = CTkLabel(self.loading_frame, text="Loading", font=CTkFont(size=16, weight="bold", family="Arial"))
        self.load_label.place(relwidth=1, relheight=0.5)

        self.slider_progressbar_frame = CTkFrame(self.loading_frame, fg_color="transparent")
        self.slider_progressbar_frame.place(relwidth=1, relheight=0.1, rely=0.5)

        self.progressbar_1 = CTkProgressBar(self.slider_progressbar_frame)
        self.progressbar_1.place(relwidth=.8, relheight=.8, rely=0.1, relx=0.1)

        #SidebarWidgets

        sbx=0.9
        sby=0.05
        px=0.05
        py=0.025

        self.logo_label = CTkLabel(self.sidebar_frame, text="Projects", font=CTkFont(size=20, weight="bold"))
        self.logo_label.place(relwidth=sbx, relheight=sby, relx=px, rely=py)

        self.sidebar_button_1 = CTkButton(self.sidebar_frame, text="My Projects", command=self.my_projects)
        self.sidebar_button_1.place(relwidth=sbx, relheight=sby, rely=0.1, relx=px)
        self.sidebar_button_2 = CTkButton(self.sidebar_frame, text="Create Project", command=self.create_project)
        self.sidebar_button_2.place(relwidth=sbx, relheight=sby, rely=0.2, relx=px)
        self.sidebar_button_23 = CTkButton(self.sidebar_frame, text="Import RBXLX", command=self.import_rbxlx)
        self.sidebar_button_23.place(relwidth=sbx, relheight=sby, rely=0.3, relx=px)

        self.logo_label_2 = CTkLabel(self.sidebar_frame, text="Settings", font=CTkFont(size=20, weight="bold"))
        self.logo_label_2.place(relwidth=sbx, relheight=sby, rely=0.4+py, relx=px)
        self.sidebar_button_3 = CTkButton(self.sidebar_frame, text="Install Manager", command=self.manage_installs)
        self.sidebar_button_3.place(relwidth=sbx, relheight=sby, rely=0.5, relx=px)
        
        self.appearance_mode_label = CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.place(relwidth=sbx, relheight=sby, rely=0.6, relx=px)
        self.appearance_mode_optionemenu = CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.place(relwidth=sbx, relheight=sby, rely=0.7, relx=px)
        self.scaling_label = CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.place(relwidth=sbx, relheight=sby, rely=0.8, relx=px)
        self.scaling_optionemenu = CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.place(relwidth=sbx, relheight=sby, rely=0.9, relx=px)

        # set default values
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")
        self.progressbar_1.configure(mode="indeterminnate")
        self.progressbar_1.start()

        self.loading = False

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.manage_installs()

    def kill_rojo_processes(self):
        # Find the process IDs of rojo.exe using tasklist command on Windows

        
        result = subprocess.run(['tasklist', '/fi', 'imagename eq rojo.exe'], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        output = result.stdout

        # Parse the output to extract the process IDs
        process_ids = []
        for line in output.splitlines()[3:]:
            if line.strip() != '':
                process_id = int(line.split()[1])
                process_ids.append(process_id)

        # Terminate the rojo.exe processes
        for process_id in process_ids:
            subprocess.run(['taskkill', '/f', '/pid', str(process_id)], creationflags=subprocess.CREATE_NO_WINDOW)

    def kill_all_executables(self):
        current_pid = os.getpid()
        current_exe = os.path.abspath(__file__)

        # Iterate over all running processes
        for process in psutil.process_iter(['pid', 'name', 'exe']):
            pid = process.info['pid']
            exe = process.info['exe']

            # Check if the process is an executable of the current file
            if exe == current_exe and pid != current_pid:
                # Terminate the process
                try:
                    process.kill()
                    print(f"Process with PID {pid} has been terminated.")
                except psutil.NoSuchProcess:
                    print(f"Process with PID {pid} no longer exists.")

    def import_rbxlx(self):
        user_home = str(Path.home())
        file = os.path.join(os.path.join(os.path.join(user_home, "RODAssistant"), "Utility"), "rbxlx-to-rojo.exe")
        if os.path.exists(file):
            subprocess.Popen(file, shell=False, creationflags=subprocess.CREATE_NEW_CONSOLE)

    def kill_current_file_processes(self):
        current_file = os.path.basename(__file__)
        try:
            subprocess.run(['taskkill', '/F', '/FI', f'IMAGENAME eq RodaApp'], creationflags=subprocess.CREATE_NO_WINDOW)
        except subprocess.CalledProcessError:
            print(f"Failed to terminate processes matching '{current_file}'.")


    def on_closing(self):
        self.kill_rojo_processes()
        self.projects_frame.stop_thread()
        self.kill_all_executables()
        self.kill_current_file_processes()
        self.destroy()

    
    def hide_cmd(self):
        return

    def show_cmd(self):
        return #fix later

    def change_appearance_mode_event(self, new_appearance_mode: str):
        set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        set_widget_scaling(new_scaling_float)
        
    def setWidgetHidden(self, widget, bool):
        if bool:
            widget.place_forget()
        else:
            widget.place(relwidth=1, relheight=1)
            
    def loading_start(self, text):
        self.loading = True
        self.setWidgetHidden(self.projects_frame, True)
        self.setWidgetHidden(self.project_creator, True)
        self.setWidgetHidden(self.install_manager, True)
        self.projects_frame.back_to_projects()
        self.load_label.configure(text=text)
        self.setWidgetHidden(self.loading_frame, False)

    def loading_end(self, widget):
        self.loading = False
        self.setWidgetHidden(widget, False)
        self.setWidgetHidden(self.loading_frame, True)

    def my_projects(self):
        if self.loading == False:
            self.loading_start("Loading Projects Viewer . . .")
            self.after(500, lambda: self.loading_end(self.projects_frame))

    def create_project(self):
        if self.loading == False:
            self.loading_start("Loading Project Creator . . .")
            self.after(500, lambda: self.loading_end(self.project_creator))

    def manage_installs(self):
        if self.loading == False:
            self.loading_start("Loading Install Manager . . .")
            self.after(500, lambda: self.loading_end(self.install_manager))

    def check_folder(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

if __name__ == "__main__":
    # Check if the script is already running with administrative privileges
    if not ctypes.windll.shell32.IsUserAnAdmin():
        # Re-launch the script with administrative privileges
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        app = App()
        
        app.mainloop()
        del app
