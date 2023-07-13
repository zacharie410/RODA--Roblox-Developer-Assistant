
import customtkinter as ct
import tempfile
from tkinter import filedialog
import os
from pathlib import Path

class ProjectCreator(ct.CTkFrame):
    def __init__(self, parent, project_handler, my_projects):
        super().__init__(parent)

        self.project_handler = project_handler
        self.my_projects = my_projects

        # Project Type
        self.type_label = ct.CTkLabel(self, text="Project Type:")
        self.type_dropdown = ct.CTkOptionMenu(self, values=["New Project", "Load Project"], command=self.change_project_type_event)
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
        user_home = str(Path.home())
        directory = os.path.join(user_home, "RODAssistant/Projects")
        if new_type == "New Project":
            self.name_entry.insert(0, "New Project #"+projectNumber)
            self.description_entry.insert(0, "Auto Generated File Structure")
            self.file_path_entry.insert(0, directory)
            self.file_path_label.configure(text="Parent Folder:")
        elif new_type == "Load Project":
            self.name_entry.insert(0, "Loaded Project #"+projectNumber)
            self.description_entry.insert(0, "Load Existing Project Folder")
            self.file_path_entry.insert(0, directory)
            self.file_path_label.configure(text="Project Folder:")


    def browse_file(self):
        file_path = ""
        if self.project_type == "Load Project" or self.project_type == "New Project":
            file_path = filedialog.askdirectory()

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
            self.project_handler.create_project(name, description, file_path, True)
        elif project_type == "Load Project":
            self.project_handler.load_project(name, description, file_path, False)

        # Clear input fields after project creation
        self.change_project_type_event("New Project")

        self.my_projects()

    def validate_form(self, project_type, name, description, file_path):
        if not project_type or not name or not description or not file_path:
            self.warning_label.configure(text="Please fill in all fields.", fg_color="red")
            self.warning_label.place(relx=0, rely=0.7, relwidth=1)
            return False
        elif self.project_handler.api.get_project_by_name(name) or os.path.isdir(os.path.join(file_path, self.project_handler.sanitize_string_for_filename(name))):
            self.warning_label.configure(text="Please use a unique project name", fg_color="#DC4D01")
            self.warning_label.place(relx=0, rely=0.7, relwidth=1)
            return False
        # Add additional validation logic specific to each project type
        elif (project_type == "Load Project" or project_type == "New Project") and not os.path.isdir(file_path):
            self.warning_label.configure(text="Directory is not valid", fg_color="#DC4D01")
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