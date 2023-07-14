import subprocess
import sys
import os
import customtkinter as ct
from PIL import Image
from tkinter import filedialog
import tempfile
import lxml.html
import urllib.request

import json
import uuid
import tkinter as tk
import subprocess
import threading
import queue
import sys
import time
import tkinter.simpledialog as tkSimpleDialog

class EmbeddedCommandPrompt(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.output_text = tk.Text(self, bg='black', fg='green', insertbackground='green', font=('Courier New', 12))
        self.output_text.place(relheight=1, relwidth=1)


        self.command_process = subprocess.Popen(
            "cmd",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP  # To enable sending Ctrl+C to process group
        )

        self.output_queue = queue.Queue()
        self.stop_reading = threading.Event()
        self.thread_completed = False

        self.read_output_thread = threading.Thread(target=self.read_output)
        self.read_output_thread.start()

        self.update_output_text()

        self.output_text.bind("<Return>", self.process_command)

    def process_command(self, event):
        command_start = self.output_text.search(">", "end-1c", backwards=True, exact=True, stopindex="1.0")
        command_end = "end-1c"
        command = self.output_text.get(command_start, command_end)
        
        # Remove leading ">" character and any leading whitespace
        command = command.lstrip(">").lstrip()

        self.output_text.delete(command_start, tk.END)

        self.command_process.stdin.write(command + "\n")
        self.command_process.stdin.flush()

    def read_output(self):
        while not self.stop_reading.is_set():
            char = self.command_process.stdout.read(1)
            if char == "":
                break
            self.output_queue.put(char)

        self.command_process.stdout.close()
        self.stop_reading.set()

    def update_output_text(self):
        while not self.output_queue.empty():
            output = ""
            while not self.output_queue.empty():
                output += self.output_queue.get()
            self.output_text.insert(tk.END, output)
            self.output_text.see(tk.END)

        if not self.stop_reading.is_set():
            self.after(100, self.update_output_text)
        elif self.thread_completed:
            self.stop_thread()
            self.wait_for_process_exit()

    def stop_thread(self):
        self.stop_reading.set()
        if sys.platform.startswith("win"):
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.command_process.pid)], shell=True)

    def wait_for_process_exit(self):
        self.command_process.wait()

    def destroy(self):
        self.stop_thread()
        self.wait_for_process_exit()
        super().destroy()

ct.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ct.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class ProjectAPI:
    def __init__(self, json_file):
        self.json_file = json_file
        self.projects = self.load_projects()

    def generate_unique_key(self):
        unique_key = str(uuid.uuid4())
        return unique_key

    def load_projects(self):
        try:
            with open(self.json_file) as file:
                projects = json.load(file)
                return projects
        except FileNotFoundError:
            return []

    def save_projects(self):
        with open(self.json_file, 'w') as file:
            json.dump(self.projects, file, indent=4)

    def get_projects(self):
        return self.projects

    def create_project(self, project):
        self.projects.append(project)
        self.save_projects()

    def get_project(self, project_id):
        for project in self.projects:
            if project['id'] == project_id:
                return project
        return None
    
    def get_project_by_name(self, project_name):
        for project in self.projects:
            if project['name'] == project_name:
                return project
        return None

    def update_project(self, project_id, project_data):
        for project in self.projects:
            if project['id'] == project_id:
                project.update(project_data)
                self.save_projects()
                return project
        return None

    def delete_project(self, project_id):
        for project in self.projects:
            if project['id'] == project_id:
                self.projects.remove(project)
                self.save_projects()
                return True
        return False

class ProjectCreatorHandler:
    def __init__(self, api, viewer):
        self.api = api
        self.viewer = viewer
    
    def create_project(self, name, description, file_path):
        new_project = {'id': self.api.generate_unique_key(), 'name': name, 'description': description, 'file_path': file_path}
        self.api.create_project(new_project)
        self.viewer.populate_project_list()
    
    def edit_project(self, project_id, updated_name=None, updated_description=None, updated_file_path=None):
        project = self.api.get_project(project_id)
        if project:
            updated_project = {
                'name': updated_name if updated_name else project['name'],
                'description': updated_description if updated_description else project['description'],
                'file_path': updated_file_path if updated_file_path else project['file_path']
            }
            self.api.update_project(project_id, updated_project)
        else:
            print(f"Project with ID {project_id} does not exist.")
    
    def delete_project(self, project_id):
        deleted = self.api.delete_project(project_id)
        if deleted:
            print(f"Project with ID {project_id} deleted successfully.")
        else:
            print(f"Failed to delete project with ID {project_id}.")

class ProjectCreator(ct.CTkFrame):
    def __init__(self, parent, project_handler, my_projects):
        super().__init__(parent)

        self.project_handler = project_handler
        self.my_projects = my_projects

        # Project Type
        self.type_label = ct.CTkLabel(self, text="Project Type:")
        self.type_dropdown = ct.CTkOptionMenu(self, values=["New Project", "Load Project", "Import Project From RBXLX"], command=self.change_project_type_event)
        self.type_label.place(relx=0, rely=0.1, relwidth=0.2, anchor="w")
        self.type_dropdown.place(relx=0.2, rely=0.1, relwidth=0.75, anchor="w")

        # Project File Path
        self.file_path_label = ct.CTkLabel(self, text="File Path:")
        self.file_path_entry = ct.CTkEntry(self)
        self.file_path_label.place(relx=0, rely=0.2, relwidth=0.2, anchor="w")
        self.file_path_entry.place(relx=0.2, rely=0.2, relwidth=0.5, anchor="w")

        # Project Name
        self.name_label = ct.CTkLabel(self, text="Name:")
        self.name_entry = ct.CTkEntry(self)
        self.name_label.place(relx=0, rely=0.4, relwidth=0.2, anchor="w")
        self.name_entry.place(relx=0.2, rely=0.4, relwidth=0.5, anchor="w")

        # Project Description
        self.description_label = ct.CTkLabel(self, text="Description:")
        self.description_entry = ct.CTkEntry(self)
        self.description_label.place(relx=0, rely=0.3, relwidth=0.2, anchor="w")
        self.description_entry.place(relx=0.2, rely=0.3, relwidth=0.5, anchor="w")

        # Warning Label
        self.warning_label = ct.CTkLabel(self, text="", fg_color="transparent")

        # Browse Button
        self.browse_button = ct.CTkButton(self, text="Browse", command=self.browse_file)
        self.browse_button.place(relx=0.75, rely=0.2, relwidth=0.2, anchor="w")

        # Create Project Button
        self.create_button = ct.CTkButton(self, text="Create Project", command=self.create_project)
        self.create_button.place(relx=0.5, rely=0.5, anchor="center")

        self.change_project_type_event("New Project")

    def change_project_type_event(self, new_type: str):
        self.clear_input_fields()
        self.project_type = new_type
        projectNumber = str(len(self.project_handler.api.get_projects()) + 1)
        if new_type == "New Project":
            self.name_entry.insert(0, "New Project #"+projectNumber)
            self.description_entry.insert(0, "Auto Generated File Structure")
            temp_dir = tempfile.gettempdir()  # Get temporary directory path
            self.file_path_entry.insert(0, temp_dir)
            self.file_path_label.configure(text="Parent Folder:")
        elif new_type == "Load Project":
            self.name_entry.insert(0, "Loaded Project #"+projectNumber)
            self.description_entry.insert(0, "Load Existing Project Folder")
            temp_dir = tempfile.gettempdir()  # Get temporary directory path
            self.file_path_entry.insert(0, temp_dir)
            self.file_path_label.configure(text="Project Folder:")
        elif new_type == "Import Project From RBXLX":
            self.name_entry.insert(0, "Imported Project #"+projectNumber)
            self.description_entry.insert(0, "Convert RBXLX to Project Files")
            temp_dir = tempfile.gettempdir()  # Get temporary directory path
            self.file_path_entry.insert(0, temp_dir)
            self.file_path_label.configure(text="RBXLX File:")

    def browse_file(self):
        file_path = ""
        if self.project_type == "Load Project" or self.project_type == "New Project":
            file_path = filedialog.askdirectory()
        elif self.project_type == "Import Project From RBXLX":
            file_path = filedialog.askopenfilename(filetype=[("Roblox Files", "*.rbxlx")])
        self.file_path_entry.delete(0, ct.END)
        self.file_path_entry.insert(ct.END, file_path)

    def create_project(self):
        project_type = self.project_type
        name = self.name_entry.get()
        description = self.description_entry.get()
        file_path = self.file_path_entry.get()

        if not self.validate_form(project_type, name, description, file_path):
            return

        if project_type == "New Project":
            self.project_handler.create_project(name, description, file_path)
        elif project_type == "Load Project":
            self.project_handler.load_project(name, description, file_path)
        elif project_type == "Generate Project From RBXLX":
            self.project_handler.generate_project(name, description, file_path)

        # Clear input fields after project creation
        self.change_project_type_event("New Project")

        self.my_projects()

    def validate_form(self, project_type, name, description, file_path):
        if not project_type or not name or not description or not file_path:
            self.warning_label.configure(text="Please fill in all fields.", fg_color="red")
            self.warning_label.place(relx=0, rely=0.7, relwidth=1)
            return False
        elif self.project_handler.api.get_project_by_name(name):
            self.warning_label.configure(text="Please use a unique project name", fg_color="#DC4D01")
            self.warning_label.place(relx=0, rely=0.7, relwidth=1)
            return False
        # Add additional validation logic specific to each project type
        elif (project_type == "Load Project" or project_type == "New Project") and not os.path.isdir(file_path):
            self.warning_label.configure(text="Directory is not valid", fg_color="#DC4D01")
            self.warning_label.place(relx=0, rely=0.7, relwidth=1)
            return False
        elif project_type == "Generate Project From RBXLX" and not file_path.endswith(".rbxlx"):
            self.warning_label.configure(text="Invalid RBXLX file", fg_color="#DC4D01")
            self.warning_label.place(relx=0, rely=0.7, relwidth=1)
            return False
        # Add any other project type-specific validations here
        # ...

        self.warning_label.place_forget()
        return True

    def clear_input_fields(self):
        self.name_entry.delete(0, ct.END)
        self.description_entry.delete(0, ct.END)
        self.file_path_entry.delete(0, ct.END)



class ViewProjectsFrame(ct.CTkFrame):
    def __init__(self, parent, project_api, create_project, app):
        super().__init__(parent)
        self.project_api = project_api
        self.create_project = create_project
        self.app = app
        # Create two container frames
        self.projects_container = ct.CTkFrame(self)
        self.project_details_container = ct.CTkFrame(self)

        # Populate Project List
        self.populate_project_list()
        self.configure(fg_color="transparent")

        # Back to Projects Button
        self.back_button = ct.CTkButton(self.project_details_container, text="Exit Project", command=self.back_to_projects)
        self.back_button.place(relwidth=0.2, relheight=0.1, rely=0.01, relx=0.79)

        # Project Details Labels
        self.project_name_label = ct.CTkLabel(self.project_details_container, font=("Arial", 18, "bold"), anchor="w")
        self.project_name_label.place(relwidth=0.6, relheight=0.1, relx=0.05, rely=0.01)
        self.project_description_label = ct.CTkLabel(self.project_details_container, anchor="w")
        self.project_description_label.place(relwidth=0.5, relheight=0.1, relx=0.1, rely=0.15)
        self.project_path_label = ct.CTkLabel(self.project_details_container, anchor="w")
        self.project_path_label.place(relwidth=0.5, relheight=0.1, relx=0.1, rely=0.25)

        # Launch VS Code Button
        self.launch_explorer_button = ct.CTkButton(self.project_details_container, text="Open File Explorer", command=self.launch_vscode)
        self.launch_explorer_button.place(relwidth=0.5, relheight=0.1, relx=0.5, rely=0.25)
        self.edit_desc = ct.CTkButton(self.project_details_container, text="Edit Description", command=self.edit_description)
        self.edit_desc.place(relwidth=0.5, relheight=0.1, relx=0.5, rely=0.15)
        self.edit_name_button = ct.CTkButton(self.project_details_container, text="Edit Name", command=self.edit_name)
        self.edit_name_button.place(relwidth=0.25, relheight=0.1, relx=0.5, rely=0.01)
        #Sync status
        self.sync_status = ct.CTkLabel(self.project_details_container, font=("Arial", 18, "bold"), anchor="w")
        self.sync_status.place(relwidth=1, relheight=0.1, relx=0.05, rely=0.4)
        self.sync_type = ct.CTkLabel(self.project_details_container, font=("Arial", 14), anchor="w")
        self.sync_type.place(relwidth=1, relheight=0.1, relx=0.05, rely=0.5)
        self.uplink_time = ct.CTkLabel(self.project_details_container, font=("Arial", 14), anchor="w")
        self.uplink_time.place(relwidth=1, relheight=0.1, relx=0.05, rely=0.6)
        self.sync_info = ct.CTkLabel(self.project_details_container, font=("Arial", 14), anchor="w")
        self.sync_info.place(relwidth=1, relheight=0.1, relx=0.05, rely=0.7)

        self.slider_progressbar_frame = ct.CTkFrame(self.project_details_container, fg_color="transparent")
        
        self.progressbar_1 = ct.CTkProgressBar(self.slider_progressbar_frame)
        self.progressbar_1.place(relwidth=.8, relheight=.8, rely=0.1, relx=0.1)
        self.progressbar_1.configure(mode="indeterminnate")
        self.progressbar_1.start()

        # Initially show the projects container and hide the project details container
        self.projects_container.place(relwidth=.96, relheight=2)

        self.project_details_container.place_forget()

        self.slider_1 = ct.CTkSlider(self, width=16, from_=0, to=100, orientation="vertical", progress_color="transparent")
        self.slider_1.set(100)
        self.slider_1.place(relheight=1, relx=.96)
        self.slider_1.configure(command=self.scroll)

        self.running=threading.Event()
        self.running.set()
        self.sync_thread = threading.Thread(target=self.update_sync)
        self.sync_thread.start()

    def edit_description(self):
       t = tkSimpleDialog.askstring("Edit", "New description")
       self.current_project["description"] = t
       self.project_api.update_project(self.current_project["id"], self.current_project)
       self.project_description_label.configure(text="Description: " + t)
       self.populate_project_list()

    def edit_name(self):
       t = tkSimpleDialog.askstring("Edit", "New name")
       if self.project_api.get_project_by_name(t):
        return False
       self.current_project["name"] = t
       self.project_api.update_project(self.current_project["id"], self.current_project)
       self.project_name_label.configure(text="Project: " + t)
       self.populate_project_list()

    def stop_thread(self):
        self.running.clear()

    def update_sync(self):
        while self.running.is_set():
            try:
                mysite = urllib.request.urlopen('http://localhost:34872/').read()
                lxml_mysite = lxml.html.fromstring(mysite)

                if not self.running.is_set():
                    print("Process ended before thread completed")
                    return
                        
                # Find the specific <div> element
                div_element = lxml_mysite.xpath("//div[@class='stats']")[0]

                # Find all labels within the <div> element
                label_elements = div_element.xpath(".//span[@class='stat-value']")

                version = ""
                uptime = ""
                # Extract values from the label elements
                for index, label in enumerate(label_elements):
                    value = label.text_content()
                    if index == 0:
                        version = value
                    elif index== 2:
                        uptime = value
                
                self.sync_status.configure(text="Files Ready to Sync")
                self.sync_type.configure(text="Service Name: Rojo V"+version)
                self.uplink_time.configure(text="Service Uptime: " + uptime)
                self.sync_info.configure(text="Ready to sync files from Roblox")
                self.slider_progressbar_frame.place_forget()
            except Exception as e:
                print("Failed to sync server:", str(e))
                self.sync_status.configure(text="Loading File Sync Services . . .")
                self.slider_progressbar_frame.place(relwidth=1, relheight=0.1, rely=0.5)
            time.sleep(1)

    def launch_rojo(self):
        # Method to launch Rojo server in an external terminal from a specific file location
        
        # Get the platform (Windows, macOS, Linux)
        platform = sys.platform

        # Set the desired file location
        file_location = self.current_project["file_path"]

        if not os.path.isdir(file_location):
            print(f"Invalid file location: {file_location}")
            return

        if platform == "win32":  # Windows
            cmd = ["start", "cmd", "/k", "rojo", "serve"]
        elif platform == "darwin":  # macOS
            cmd = ["osascript", "-e", f'tell app "Terminal" to do script "cd {file_location} && rojo serve"']
        elif platform.startswith("linux"):  # Linux
            cmd = ["x-terminal-emulator", "-e", f"bash -c 'cd {file_location} && rojo serve'"]
        else:
            print("Unsupported platform. Rojo server launch not implemented for this platform.")
            return

        try:
            subprocess.Popen(cmd, cwd=file_location)
        except FileNotFoundError:
            print("Rojo command not found. Make sure Rojo is installed and added to your system's PATH.")


    def launch_vscode(self):
        # Method to open Visual Studio Code at a specific folder location

        # Get the platform (Windows, macOS, Linux)
        platform = sys.platform

        # Set the desired folder location
        folder_location = self.current_project["file_path"]

        if not os.path.isdir(folder_location):
            print(f"Invalid folder location: {folder_location}")
            return

        if platform == "win32":  # Windows
            cmd = ["code", folder_location]
        elif platform == "darwin":  # macOS
            cmd = ["open", "-a", "Visual Studio Code", folder_location]
        elif platform.startswith("linux"):  # Linux
            cmd = ["code", folder_location]
        else:
            print("Unsupported platform. VS Code launch not implemented for this platform.")
            return

        try:
            subprocess.Popen(cmd)
        except FileNotFoundError:
            print("Visual Studio Code command not found. Make sure VS Code is installed and added to your system's PATH.")

    def scroll(self, num):
        self.projects_container.place(relwidth=0.96, relheight=2, rely=-1+num/100)

    def populate_project_list(self):
        projects = self.project_api.get_projects()
        for child in self.projects_container.winfo_children():
            child.destroy()

        columns=3
        ratex=0.33
        ratey=0.1

        def get_coordinates(index):
            x = index % columns
            y = index // columns
            return x, y
        

        ficon = ct.CTkImage(light_image=Image.open("folder_icon.png"), dark_image=Image.open("folder_icon.png"), size=(32, 32))
        nficon = ct.CTkImage(light_image=Image.open("new_folder_icon.png"), dark_image=Image.open("new_folder_icon.png"), size=(32, 32))

        num = 0
        for id, project in enumerate(projects):
            x, y = get_coordinates(id)
            num = id+1
            pb = ct.CTkButton(self.projects_container, font=("Roboto", 12),text=project["name"], image=ficon, compound="top")
            pb.configure(command= lambda p= project: self.open_project(p))
            pb.place(relwidth=0.3, relheight=0.1, relx=(ratex*x)+0.025, rely=(ratey+0.05)*y+0.05)

        x, y = get_coordinates(num)
        newb = ct.CTkButton(self.projects_container, font=("Roboto", 12),text="New", image=nficon, compound="top", command=self.create_project)
        newb.place(relwidth=0.2, relheight=0.1, relx=(ratex*x)+0.025, rely=(ratey+0.05)*y+0.05)

    def open_project(self, project):
        self.current_project = project
        # Hide the projects container
        self.projects_container.place_forget()
        self.slider_1.place_forget()

        # Show the project details container
        self.project_details_container.place(relwidth=1, relheight=1)

        # Display the project details in the project details container
        self.display_project_details(project)
        #self.app.show_cmd()


    def display_project_details(self, project):
        self.project_name_label.configure(text=f"Project: {project['name']}")
        self.project_description_label.configure(text=f"Description: {project['description']}")
        self.project_path_label.configure(text=f"Path: {project['file_path']}")

    def back_to_projects(self):
        # Hide the project details container
        self.project_details_container.place_forget()

        # Show the projects container
        self.projects_container.place(relwidth=.96, relheight=2)
        self.slider_1.place(relheight=1, relx=.96)

        # Clear the project details
        self.clear_project_details()
        self.app.hide_cmd()

    def clear_project_details(self):
        self.project_name_label.configure(text="")
        self.project_description_label.configure(text="")

class App(ct.CTk):
    def __init__(self):
        super().__init__()

        self.api = ProjectAPI('projects.json')

        # configure window
        self.title("RODA: Roblox Developer Assistant")

                # Set the desired aspect ratio
        self.aspect_ratio = 16 / 9  # For example, 16:9

        # Set the minimum window size
        self.min_width = 600
        self.min_height = int(self.min_width / self.aspect_ratio)

        # Force aspect ratio and minimum size
        self.geometry(f"{self.min_width}x{self.min_height}")
        self.minsize(self.min_width, self.min_height)

        paddingx=0.02
        offsetx=0.01
        paddingy=0.02
        offsety=0.01
        # create sidebar frame
        self.sidebar_frame = ct.CTkFrame(self)
        self.sidebar_frame.place(relwidth=0.25-paddingx, relx=offsetx, relheight=1-paddingy, rely=offsety)

        # create container frame
        self.container_frame = ct.CTkFrame(self, fg_color="transparent")
        self.container_frame.place(relwidth=0.75-paddingx, relx=offsetx + 0.25, relheight=1-paddingy, rely=offsety)

        self.embedded_command = EmbeddedCommandPrompt(self)

        self.embedded_command.place_forget()
        # create subframes
        self.loading_frame = ct.CTkFrame(self.container_frame)
        self.loading_frame.place_forget()

        self.projects_frame = ViewProjectsFrame(self.container_frame, self.api, self.create_project, self)
        self.projects_frame.place_forget()

        self.project_creator = ProjectCreator(self.container_frame, ProjectCreatorHandler(self.api, self.projects_frame), self.my_projects)
        self.project_creator.place_forget()


        # create slider and progressbar frame
        self.load_label = ct.CTkLabel(self.loading_frame, text="Loading", font=ct.CTkFont(size=16, weight="bold", family="Arial"))
        self.load_label.place(relwidth=1, relheight=0.5)

        self.slider_progressbar_frame = ct.CTkFrame(self.loading_frame, fg_color="transparent")
        self.slider_progressbar_frame.place(relwidth=1, relheight=0.1, rely=0.5)

        self.progressbar_1 = ct.CTkProgressBar(self.slider_progressbar_frame)
        self.progressbar_1.place(relwidth=.8, relheight=.8, rely=0.1, relx=0.1)

        #SidebarWidgets

        sbx=0.9
        sby=0.05
        px=0.05
        py=0.025

        self.logo_label = ct.CTkLabel(self.sidebar_frame, text="Projects", font=ct.CTkFont(size=20, weight="bold"))
        self.logo_label.place(relwidth=sbx, relheight=sby, relx=px, rely=py)

        self.sidebar_button_1 = ct.CTkButton(self.sidebar_frame, text="My Projects", command=self.my_projects)
        self.sidebar_button_1.place(relwidth=sbx, relheight=sby, rely=0.1, relx=px)
        self.sidebar_button_2 = ct.CTkButton(self.sidebar_frame, text="Create Project", command=self.create_project)
        self.sidebar_button_2.place(relwidth=sbx, relheight=sby, rely=0.2, relx=px)


        self.logo_label_2 = ct.CTkLabel(self.sidebar_frame, text="Settings", font=ct.CTkFont(size=20, weight="bold"))
        self.logo_label_2.place(relwidth=sbx, relheight=sby, rely=0.4+py, relx=px)
        self.sidebar_button_3 = ct.CTkButton(self.sidebar_frame, text="Install Manager", command=self.create_project)
        self.sidebar_button_3.place(relwidth=sbx, relheight=sby, rely=0.5, relx=px)
        
        self.appearance_mode_label = ct.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.place(relwidth=sbx, relheight=sby, rely=0.6, relx=px)
        self.appearance_mode_optionemenu = ct.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.place(relwidth=sbx, relheight=sby, rely=0.7, relx=px)
        self.scaling_label = ct.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.place(relwidth=sbx, relheight=sby, rely=0.8, relx=px)
        self.scaling_optionemenu = ct.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.place(relwidth=sbx, relheight=sby, rely=0.9, relx=px)

        # set default values
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")
        self.progressbar_1.configure(mode="indeterminnate")
        self.progressbar_1.start()

        self.loading = False

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.projects_frame.stop_thread()
        self.destroy()
    
    def hide_cmd(self):
        self.embedded_command.place_forget()

    def show_cmd(self):
        self.embedded_command.place(relwidth=0.7, relheight=0.4, relx=0.275, rely=0.55)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ct.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ct.set_widget_scaling(new_scaling_float)
        
    def setWidgetHidden(self, widget, bool):
        if bool:
            widget.place_forget()
        else:
            widget.place(relwidth=1, relheight=1)


            
    def loading_start(self, text):
        self.loading = True
        self.setWidgetHidden(self.projects_frame, True)
        self.setWidgetHidden(self.project_creator, True)
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


if __name__ == "__main__":
    app = App()
    
    app.mainloop()
    del app
