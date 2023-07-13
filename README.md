# RODA: Roblox Developer Assistant

- [RODA: Roblox Developer Assistant](#roda-roblox-developer-assistant)
  - [Features](#features)
  - [Screenshots](#screenshots)
    - [Project Management](#project-management)
    - [Project Creation](#project-creation)
    - [Install Manager](#install-manager)
    - [Automatic Rojo Syncing](#automatic-rojo-syncing)
- [Usage Guide](#usage-guide)
  - [Installing RODA](#installing-roda)
  - [After installing RODA](#after-installing-roda)
  - [1. Creating a new project](#1-creating-a-new-project)
  - [2. Loading an existing project](#2-loading-an-existing-project)
  - [3. Importing an existing Roblox Place](#3-importing-an-existing-roblox-place)
  - [4. Syncing to studio](#4-syncing-to-studio)
- [Developer Documentation](#developer-documentation)
    - [This section is for developer use only!](#this-section-is-for-developer-use-only)
  - [Contributing](#contributing)
  - [Build Instructions](#build-instructions)
  - [ProjectAPI Documentation](#projectapi-documentation)
  - [Acknowledgements](#acknowledgements)

RODA is a Python GUI application designed to simplify the management of multiple Roblox projects. It provides a user-friendly interface for managing and organizing your Roblox projects efficiently.

Note: No builds are currently released but will be dropped in the next few days

## Features

- **Project Management:** RODA allows you to view and manage your Roblox projects easily. You can browse through your projects, access project details, and perform various actions such as creating, updating, and deleting projects.

- **Project Creation:** With RODA, creating new Roblox projects is a breeze. The intuitive project creation interface lets you specify project details, set up project configurations, and create a new project with just a few clicks.

- **RBXLX Import:** RODA enables you to import RBXLX files into your projects effortlessly. Simply choose the RBXLX file you want to import, and RODA will handle the process of integrating it into your project, making it quick and convenient to incorporate existing assets and designs.

- **Install Manager:** RODA comes with an Install Manager that simplifies the installation and management of dependencies for your Roblox projects. The Install Manager provides an easy-to-use interface to search, install, update, and remove dependencies, ensuring that your projects have the required assets and libraries seamlessly.

## Screenshots

### Project Management

![Projects](/screenshots/projects.png)
![Sync](/screenshots/sync.png)
- The Projects screen gives you an overview of all your Roblox projects. You can see project details, such as name, description, and last modified date, and easily navigate through your projects. Perform actions like creating a new project, updating existing projects, or deleting projects.

### Project Creation

![Creator](/screenshots/creator.png)

- The Project Creator screen offers a user-friendly interface to create new Roblox projects. Fill in project details, set up project configurations, and customize settings to get started with a new project in no time.

### Install Manager

![Installer](/screenshots/installer.png)

- The Install Manager screen simplifies the installation and management of dependencies for your Roblox projects. Search for dependencies, install or update them, and remove unwanted dependencies with ease. Keep your projects up to date and ensure they have the necessary assets and libraries.

### Automatic Rojo Syncing

![Synced](/screenshots/synced.png)

- RODA provides automatic Rojo syncing to keep your projects in sync with your Roblox workspace. Any changes made within RODA are seamlessly synchronized with your Roblox projects, ensuring consistency and efficiency in your development workflow.

# Usage Guide
## Installing RODA
[You can install RODA for windows here](https://github.com/zacharie410/RODA--Roblox-Developer-Assistant/releases)
## After installing RODA
Make sure you install aftman and the ROJO CLI as they are dependencies for many of the application features

## 1. Creating a new project
   To create a new project, navigate to the Create Project menu.
   - Select New Project from the options
   - Configure the parameters to your liking
   - Press Create Project
   - [Syncing to studio](#4-syncing-to-studio)

## 2. Loading an existing project
   To load an existing project, navigate to the Create Project menu.
 - Select Load Project
 - For the path, select an existing Rojo File structure project directoy.
 - Press Create Project
 - [Syncing to studio](#4-syncing-to-studio)

## 3. Importing an existing Roblox Place
   To import an existing roblox place, press Import RBXLX on the left sidebar
   - The file you convert must be an RBXLX, you can generate this by selecting RBXLX as the SaveAs option in Roblox Studio when saving
   - Select your RBXLX file, then select the directory where you wish to build the project folder
   - Once this is complete, follow the steps from [Loading an existing project](#2-loading-an-existing-project)
   - [Syncing to studio](#4-syncing-to-studio)

## 4. Syncing to studio
   After you have created or loaded a project, follow these steps to sync with roblox.
   - In the project viewer, press the Open File explorer to have access to project directory
   - Once inside the project directory, open with VS Code to begin editing
   - Open the roblox build file in Roblox Studio
   - Navigate to Roblox Studio Plugins bar
   - Click on Rojo
   - When RODA tells you the syncing service is ready, press connect to server in roblox studio
   - You are ready to edit your new project!

# Developer Documentation
### This section is for developer use only!

## Contributing
Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please create an issue or submit a pull request.

## Build Instructions
To build the project with your own changes follow these steps:
1. Ensure pyinstaller is installed `pip install pyinstaller`
2. Navigate to root project folder in a terminal window
3. In the same window, run: `python -m PyInstaller -wF RodaApp.py --collect-all customtkinter -w`
4. Wait 1-3 minutes and your project be built
5. Currently you must copy the images folder into your dist folder after building

## ProjectAPI Documentation

The ProjectAPI module provides a ProjectAPI class for managing projects. You can instantiate the class and call its methods to perform various operations on projects.

**Data Structure:**

The data structure for a project includes the following fields:

- `id` (string): Unique identifier for the project.
- `name` (string): Name of the project.
- `description` (string): Description of the project.
- `file_path` (string): File path associated with the project.

**Class: ProjectAPI**

This class provides the following methods:

1. **`__init__(self, json_file)`**

   Description: Initializes the ProjectAPI instance.

   Parameters:
   - `json_file` (string): Path to the JSON file storing project data.

   Example Usage:
   ```python
   project_api = ProjectAPI("projects.json")
   ```

2. **`get_projects(self)`**

   Description: Retrieves all projects.

   Returns:
   - `projects` (list): List of project dictionaries.

   Example Usage:
   ```python
   projects = project_api.get_projects()
   ```

3. **`create_project(self, project)`**

   Description: Creates a new project.

   Parameters:
   - `project` (dict): Dictionary representing the project with fields `name`, `description`, and `file_path`.

   Example Usage:
   ```python
   new_project = {
       "name": "New Project",
       "description": "This is a new project",
       "file_path": "/path/to/new_project"
   }
   project_api.create_project(new_project)
   ```

4. **`get_project(self, project_id)`**

   Description: Retrieves a specific project by its ID.

   Parameters:
   - `project_id` (string): ID of the project to retrieve.

   Returns:
   - `project` (dict): Dictionary representing the project with fields `id`, `name`, `description`, and `file_path`.

   Example Usage:
   ```python
   project = project_api.get_project("2")
   ```

5. **`get_project_by_name(self, project_name)`**

   Description: Retrieves a specific project by its name.

   Parameters:
   - `project_name` (string): Name of the project to retrieve.

   Returns:
   - `project` (dict): Dictionary representing the project with fields `id`, `name`, `description`, and `file_path`.

   Example Usage:
   ```python
   project = project_api.get_project_by_name("New Project")
   ```

6. **`update_project(self, project_id, project_data)`**

   Description: Updates a specific project by its ID.

   Parameters:
   - `project_id` (string): ID of the project to update.
   - `project_data` (dict): Dictionary containing the updated project fields.

   Returns:
   - `project` (dict): Dictionary representing the updated project with fields `id`, `name`, `description`, and `file_path`.

   Example Usage:
   ```python
   updated_project_data = {
       "description": "Updated project 2"
   }
   updated_project = project_api.update_project("2", updated_project_data)
   ```

7. **`delete_project(self, project_id)`**

   Description: Deletes a specific project by its ID.

   Parameters:
   - `project_id` (string): ID of the project to delete.

   Returns:
   - `success` (bool): `True` if the project was successfully deleted, `False` otherwise.

   Example Usage:
   ```python
   success = project_api.delete_project("1")
   ```

Please note that this documentation assumes you have an instance of the `ProjectAPI` class initialized (`project_api` in the examples). You can call the methods on that instance accordingly to interact with the project data.

Let me know if you need any further clarification or have additional questions!

## Acknowledgements
This app was made possible using the Custom Tkinter library by Tom Schimansky: https://github.com/TomSchimansky/CustomTkinter (MIT License)