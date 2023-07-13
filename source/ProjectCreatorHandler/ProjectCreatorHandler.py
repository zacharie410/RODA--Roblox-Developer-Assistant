import os
import subprocess
import re

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
            subprocess.run("rojo init "+sanitized, cwd=file_path1, shell=True)
            subprocess.run("rojo build -o build.rbxlx", cwd=file_path, shell=True)
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
        else:
            print(f"Project with ID {project_id} does not exist.")
    
    def delete_project(self, project_id):
        deleted = self.api.delete_project(project_id)
        if deleted:
            print(f"Project with ID {project_id} deleted successfully.")
        else:
            print(f"Failed to delete project with ID {project_id}.")