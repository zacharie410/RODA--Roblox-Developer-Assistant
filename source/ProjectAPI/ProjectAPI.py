import json
import uuid

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