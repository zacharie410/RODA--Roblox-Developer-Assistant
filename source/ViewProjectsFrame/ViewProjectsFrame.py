import subprocess
import os
import customtkinter as ct
from PIL import Image
import lxml.html
import urllib.request
import subprocess
import threading
import time
import tkinter.simpledialog as tkSimpleDialog
import tkinter.messagebox as messagebox

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
        self.back_button.place(relwidth=0.2, relheight=0.1, rely=0.89, relx=0.79)

        # Project Details Labels
        self.project_name_label = ct.CTkLabel(self.project_details_container, font=("Arial", 18, "bold"), anchor="w")
        self.project_name_label.place(relwidth=0.6, relheight=0.1, relx=0.05, rely=0.01)
        self.project_description_label = ct.CTkLabel(self.project_details_container, anchor="w")
        self.project_description_label.place(relwidth=0.5, relheight=0.1, relx=0.1, rely=0.15)
        self.project_path_label = ct.CTkLabel(self.project_details_container, anchor="w")
        self.project_path_label.place(relwidth=0.5, relheight=0.1, relx=0.1, rely=0.25)

        # Launch VS Code Button
        self.launch_explorer_button = ct.CTkButton(self.project_details_container, text="Open File Explorer", command=self.launch_explorer)
        self.launch_explorer_button.place(relwidth=0.24, relheight=0.1, relx=0.75, rely=0.75)
        self.edit_name_button = ct.CTkButton(self.project_details_container, text="Edit Name", command=self.edit_name)
        self.edit_name_button.place(relwidth=0.24, relheight=0.1, relx=0.75, rely=0.01)
        self.edit_desc = ct.CTkButton(self.project_details_container, text="Edit Description", command=self.edit_description)
        self.edit_desc.place(relwidth=0.24, relheight=0.1, relx=0.75, rely=0.12)
        self.edit_path_button = ct.CTkButton(self.project_details_container, text="Edit Path", command=self.edit_path)
        self.edit_path_button.place(relwidth=0.24, relheight=0.1, relx=0.75, rely=0.23)
        self.delete_project_button = ct.CTkButton(self.project_details_container, text="Delete Project", command=self.delete_project)
        self.delete_project_button.place(relwidth=0.24, relheight=0.1, relx=0.75, rely=0.5)

        #Sync status
        self.sync_status = ct.CTkLabel(self.project_details_container, font=("Arial", 18, "bold"), anchor="w")
        self.sync_status.place(relwidth=.5, relheight=0.1, relx=0.05, rely=0.4)
        self.sync_type = ct.CTkLabel(self.project_details_container, font=("Arial", 14), anchor="w")
        self.sync_type.place(relwidth=.5, relheight=0.1, relx=0.05, rely=0.5)
        self.uplink_time = ct.CTkLabel(self.project_details_container, font=("Arial", 14), anchor="w")
        self.uplink_time.place(relwidth=.5, relheight=0.1, relx=0.05, rely=0.6)
        self.sync_info = ct.CTkLabel(self.project_details_container, font=("Arial", 14), anchor="w")
        self.sync_info.place(relwidth=.5, relheight=0.1, relx=0.05, rely=0.7)

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
        self.sync_thread = threading.Timer(5, self.update_sync)
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

    def edit_path(self):
       t = tkSimpleDialog.askstring("Edit", "New Path")
       if not os.path.exists(t):
        return False
       self.current_project["file_path"] = t
       self.project_api.update_project(self.current_project["id"], self.current_project)
       self.project_path_label.configure(text="Path: " + t)
       self.populate_project_list()

    def stop_thread(self):
        self.running.clear()

    def default_sync_status(self):
        self.sync_status.configure(text="Loading File Sync Services . . .")
        self.sync_type.configure(text="Service Name: Rojo")
        self.uplink_time.configure(text="Service Uptime: Boot")
        self.sync_info.configure(text="Rojo server is launching")
        self.slider_progressbar_frame.place(relwidth=0.75, relheight=0.1, rely=0.9)

    def update_sync(self):
        self.default_sync_status()
        while self.running.is_set():
            time.sleep(1)
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
                if self.running.is_set():
                    self.default_sync_status()
                    time.sleep(1)


    def run_server(self):
        subprocess.run("rojo serve", cwd=self.current_project["file_path"], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

    def launch_rojo(self):
        self.app.kill_rojo_processes()

        self.app.server_thread = threading.Timer(1, self.run_server)
        self.app.server_thread.start()
       

    def open_file_explorer_windows(self, directory):
        os.startfile(directory)

    def launch_explorer(self):
        self.open_file_explorer_windows(self.current_project["file_path"])

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
        

        ficon = ct.CTkImage(light_image=Image.open("images/folder_icon.png"), dark_image=Image.open("images/folder_icon.png"), size=(32, 32))
        nficon = ct.CTkImage(light_image=Image.open("images/new_folder_icon.png"), dark_image=Image.open("images/new_folder_icon.png"), size=(32, 32))

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
        self.default_sync_status()
        # Display the project details in the project details container
        self.display_project_details(project)
        #self.app.show_cmd()
        self.launch_rojo()


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
        self.app.kill_rojo_processes()

    def delete_project(self):
        user_confirmation = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete?")
        if user_confirmation:
            self.project_api.delete_project(self.current_project["id"])
            self.populate_project_list()
            self.back_to_projects()
        else:
            # User canceled the delete operation
            print("Delete operation canceled.")

    def clear_project_details(self):
        self.project_name_label.configure(text="")
        self.project_description_label.configure(text="")