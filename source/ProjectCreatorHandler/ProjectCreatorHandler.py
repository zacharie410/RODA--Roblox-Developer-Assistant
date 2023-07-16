import os
import subprocess
import re
import sys

class ProjectCreatorHandler:
    def __init__(self, api, viewer):
        self.api = api
        self.viewer = viewer

    def sanitize_string_for_filename(self, string):
        # Replace invalid characters with an underscore
        sanitized_string = re.sub(r'[\/:*?"<>|# ]', '-', string)
        return sanitized_string
    
    def create_project(self, name, description, file_path1, init):
        sanitized = self.sanitize_string_for_filename(name)
        file_path = os.path.join(file_path1, sanitized)
        new_project = {'id': self.api.generate_unique_key(), 'name': name, 'description': description, 'file_path': file_path}
        os.makedirs(file_path)
        if init:
            self.run_rojo_init(sanitized, file_path1)
            self.run_rojo_build(file_path)
        self.api.create_project(new_project)

        self.viewer.populate_project_list()

    def load_project(self, name, description, file_path, init):
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

    def run_rojo_init(self, sanitized, file_path1):
        if sys.platform == "win32":
            command = f"rojo init {sanitized}"
            subprocess.run(command, cwd=file_path1, shell=True, creationflags=subprocess.CREATE_NO_WINDOW, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sys.platform == "darwin" or sys.platform.startswith("linux"):
            command = f"rojo init {sanitized}"
            subprocess.run(command, cwd=file_path1, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print("Unsupported operating system.")

    def run_rojo_build(self, file_path):
        if sys.platform == "win32":
            command = "rojo build -o build.rbxlx"
            subprocess.run(command, cwd=file_path, shell=True, creationflags=subprocess.CREATE_NO_WINDOW, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sys.platform == "darwin" or sys.platform.startswith("linux"):
            command = "rojo build -o build.rbxlx"
            subprocess.run(command, cwd=file_path, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print("Unsupported operating system.")