import customtkinter
import tkinter as tk
import subprocess
import os
import json
import urllib.request
import shutil
import zipfile
import subprocess
import sys
import threading
import time
from pathlib import Path

class InstallManager(customtkinter.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.installing = False
        # Installations page
        self.installations_listbox = customtkinter.CTkFrame(self)
        self.installations_listbox.pack(fill="both", expand=True, padx=20, pady=20)

        self.selected_checkboxes = []
                # List of recommended installs
        self.installations_list = [
            {"name": "Aftman Toolchain Manager", "versionName": "aftman", "dependency": "", "var": customtkinter.BooleanVar(), "restart": True},
            {"name": "Rojo CLI", "versionName": "rojo-rbx/rojo", "dependency": "aftman", "var": customtkinter.BooleanVar(), "restart": True},
            {"name": "Wally CLI", "versionName": "UpliftGames/wally", "dependency": "aftman", "var": customtkinter.BooleanVar(), "restart": True},
            {"name": "Rojo Plugin", "versionName": "rojo/plugin", "dependency": "rojo-rbx/rojo", "var": customtkinter.BooleanVar(), "restart": False},
            {"name": "RBXLX to Rojo", "versionName": "rojo/converter", "dependency": "", "var": customtkinter.BooleanVar(), "restart": False},
        ]
        self.install_buttons = {}
        self.update_installations_list()  # Initial update


        # Create the Uninstall and Install buttons
        self.buttons_frame = customtkinter.CTkFrame(self)
        self.buttons_frame.pack(fill="x", padx=20, pady=10)

        self.select_button = customtkinter.CTkButton(self.buttons_frame, text="Select All", command=lambda: self.select_all_tools())
        self.select_button.pack(side="left", padx=5)

        self.uninstall_button = customtkinter.CTkButton(self.buttons_frame, text="Uninstall", command=lambda: self.uninstall_tools())
        self.uninstall_button.pack(side="right", padx=5)

        self.install_button = customtkinter.CTkButton(self.buttons_frame, text="Install", command=lambda: self.install_tools())
        self.install_button.pack(side="right", padx=5)

        self.progressbar_1 = customtkinter.CTkProgressBar(self)
        self.progressbar_1.set(.6)

    def check_file_exists(self, directory, filename):
        filepath = os.path.join(directory, filename)
        if os.path.exists(filepath):
            return True
        else:
            return False

    def download_file(self, url, directory):
        # Create the directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)

        # Set the local path for saving the file
        filepath = os.path.join(directory, url.split("/")[-1])

        try:
            # Download the file using urllib
            urllib.request.urlretrieve(url, filepath)
        except Exception as e:
            return
        
    def delete_file_if_exists(self, directory, filename):
        filepath = os.path.join(directory, filename)
        if os.path.exists(filepath):
            os.remove(filepath)

    def install_rojo_plugin(self):
        url = "https://github.com/rojo-rbx/rojo/releases/latest/download/Rojo.rbxm"
        directory = self.get_robolox_plugins_directory()

        self.delete_file_if_exists(directory, "Rojo.rbxm")
        self.delete_file_if_exists(directory, "RojoManagedPlugin.rbxm")
        self.download_file(url, directory)

    def get_robolox_plugins_directory(self):
        system = sys.platform
        home_directory = os.path.expanduser("~")

        if system == "win32":
            return os.path.join(home_directory, "AppData", "Local", "Roblox", "Plugins")
        elif system == "darwin": # MacOS
            return os.path.join(home_directory, "Library", "Application Support", "Roblox", "Plugins")
        elif system == "linux":
            return os.path.join(home_directory, ".config", "Roblox", "Plugins")
        else:
            print("Unsupported operating system.")
            return ""

    def install_rbxlx_converter(self):
        url = ""
        directory = ""

        system = sys.platform
        user_home = str(Path.home())

        if system == "win32":
            url = "https://github.com/rojo-rbx/rbxlx-to-rojo/releases/latest/download/rbxlx-to-rojo.exe"
            directory = os.path.join(os.path.join(user_home, "RODAssistant"), "Utility")
        elif system == "darwin": #MacOS
            url = "https://github.com/rojo-rbx/rbxlx-to-rojo/releases/latest/download/rbxlx-to-rojo-macos"
            directory = os.path.join(os.path.join(user_home, "RODAssistant"), "Utility")
        else: # This tool does not support other OS
            print("Unsupported operating system.")
            return

        self.delete_file_if_exists(directory, "rbxlx-to-rojo")
        self.download_file(url, directory)

    def install_aftman(self):
        # Set the GitHub repository URL
        aftmanRepoUrl = "https://api.github.com/repos/LPGhatguy/aftman/releases/latest"
        # Get Aftman data
        # Fetch release information using the GitHub API
        response = urllib.request.urlopen(aftmanRepoUrl)
        release_data = json.loads(response.read().decode())

        # Save the response data to release.json
        with open("release.json", "w") as file:
            json.dump(release_data, file)
        # Parse the JSON response to get the latest version
        aftmanVersion = release_data["tag_name"]
        # Clean up the temporary JSON file
        os.remove("release.json")
        # Output the latest version
        aftmanVersion = aftmanVersion[1:6]

        if sys.platform == "win32":
            zipName = f"aftman-{aftmanVersion}-windows-x86_64.zip"
            downloadUrl = f"https://github.com/LPGhatguy/aftman/releases/latest/download/{zipName}"
            installDir = os.path.join(os.environ["TEMP"], "aftman")
            # Check if aftman is already installed
            if os.path.exists(os.path.join(installDir, "aftman.exe")):
                shutil.rmtree(installDir)

            urllib.request.urlretrieve(downloadUrl, zipName)
            with zipfile.ZipFile(zipName, "r") as zip_ref:
                zip_ref.extractall(installDir)

            # Elevate the aftman installer
            subprocess.call([os.path.join(installDir, "aftman.exe"), "self-install"], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

            # Cleanup extracted files and downloaded zip
            os.remove(zipName)
            shutil.rmtree(installDir)
        elif sys.platform == "darwin": #MacOS
            zipName = f"aftman-{aftmanVersion}-macos-x86_64.zip"
            downloadUrl = f"https://github.com/LPGhatguy/aftman/releases/latest/download/{zipName}"
            installDir = os.path.join(Path.home(), "aftman")
            # Check if aftman is already installed
            if os.path.exists(os.path.join(installDir, "aftman")):
                shutil.rmtree(installDir)

            urllib.request.urlretrieve(downloadUrl, zipName)
            with zipfile.ZipFile(zipName, "r") as zip_ref:
                zip_ref.extractall(installDir)

            # Make the extracted aftman file executable
            aftmanPath = os.path.join(installDir, "aftman")
            subprocess.call(["chmod", "+x", aftmanPath])

            # Run the aftman installer
            subprocess.call([aftmanPath, "self-install"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Cleanup extracted files and downloaded zip
            os.remove(zipName)
            shutil.rmtree(installDir)
        else:
            print("Aftman installation is currently only supported on Windows and macOS.")

        # Update installations list
        self.update_installations_list()


    def is_installed(self, installToFind):
        try:
            if installToFind == "rojo/plugin":
                if sys.platform == "win32":
                    directory = os.path.expanduser("~/AppData/Local/Roblox/Plugins")
                elif sys.platform == "darwin":
                    directory = os.path.expanduser("~/Library/Application Support/Roblox/Plugins")
                elif sys.platform == "linux":
                    directory = os.path.expanduser("~/.config/Roblox/Plugins")
                else:
                    print("Unsupported operating system.")
                    return False

                return self.check_file_exists(directory, "Rojo.rbxm")
            
            elif installToFind == "rojo/converter":
                user_home = str(Path.home())
                directory = os.path.join(os.path.join(user_home, "RODAssistant"), "Utility")
                
                return self.check_file_exists(directory, "rbxlx-to-rojo.exe")
            
            else:
                if sys.platform == "win32":
                    directory = os.path.expanduser(os.path.join("~", ".aftman", "bin"))
                elif sys.platform == "darwin":
                    directory = os.path.expanduser(os.path.join("~", ".aftman", "bin"))
                elif sys.platform == "linux":
                    directory = os.path.expanduser(os.path.join("~", ".aftman", "bin"))
                else:
                    print("Unsupported operating system.")
                    return False

                if os.path.exists(directory):
                    out = ""
                    if installToFind == "aftman":
                        result = subprocess.run(["aftman", "-V"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        out = result.stdout
                    else:
                        result = subprocess.run(["aftman", "list"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        out = result.stdout

                    if out.find(installToFind) != -1:
                        return True
                    else:
                        return False
                else:
                    return False

        except subprocess.CalledProcessError:
            return False
        except FileNotFoundError:
            print("Error: 'aftman' not found")
        except Exception as e:
            print("Unexpected error:", e)

    def install_tool(self, item, thread, previous_thread):
        if previous_thread is not False:
            while previous_thread is not None and previous_thread.is_alive():
                time.sleep(0.5)

        self.installing = True
        self.app.loading_start("Installing " + item["name"] + " . . .")

        versionName = item["version"]
        # Logic to perform the installation
        # Replace this with your implementation
        if versionName == "rojo/plugin":
            self.install_rojo_plugin()
        elif versionName == "rojo/converter":
            self.install_rbxlx_converter()
        elif versionName == "aftman":
            self.install_aftman()
        else:
            if sys.platform == "win32":
                subprocess.run(["aftman", "trust", versionName], creationflags=subprocess.CREATE_NO_WINDOW)
                subprocess.run(["aftman", "add", "--global", versionName], creationflags=subprocess.CREATE_NO_WINDOW)
                subprocess.run(["aftman", "install"], creationflags=subprocess.CREATE_NO_WINDOW)
            elif sys.platform == "darwin":
                subprocess.run(["aftman", "trust", versionName])
                subprocess.run(["aftman", "add", "--global", versionName])
                subprocess.run(["aftman", "install"])
            elif sys.platform.startswith("linux"):
                subprocess.run(["aftman", "trust", versionName])
                subprocess.run(["aftman", "add", "--global", versionName])
                subprocess.run(["aftman", "install"])
            else:
                print("Unsupported operating system.")

        self.update_installations_list()
        self.app.loading_end(self)
        self.installing = False

        if item["restart"]:
            self.app.loading_start("App must restart . . .")
            self.app.restart_app()

    def uninstall_tool(self, item):
        v = item["version"]
        # Logic to perform the uninstallation
        # Replace this with your implementation
        if v == "rojo/plugin":
            if sys.platform == "win32":
                directory = os.path.expanduser("~/AppData/Local/Roblox/Plugins")
            elif sys.platform == "darwin":
                directory = os.path.expanduser("~/Library/Application Support/Roblox/Plugins")
            elif sys.platform.startswith("linux"):
                directory = os.path.expanduser("~/.config/Roblox/Plugins")
            else:
                print("Unsupported operating system.")
                return

            self.delete_file_if_exists(directory, "Rojo.rbxm")
            self.delete_file_if_exists(directory, "RojoManagedPlugin.rbxm")
        elif v == "rojo/converter":
            user_home = str(Path.home())
            directory = os.path.join(os.path.join(user_home, "RODAssistant"), "Utility")
            self.delete_file_if_exists(directory, "rbxlx-to-rojo.exe")
        elif v == "aftman":
            if sys.platform == "win32":
                user_home = str(Path.home())
                directory = os.path.join(user_home, ".aftman")
                if os.path.exists(directory):
                    shutil.rmtree(directory)
            elif sys.platform == "darwin":
                subprocess.run(["aftman", "uninstall"])
            elif sys.platform.startswith("linux"):
                subprocess.run(["aftman", "uninstall"])
            else:
                print("Unsupported operating system.")
                return

        self.deselect_all_tools()

    def install_tools(self):
        if self.installing == True:
            return
        
        previous_thread = False
        for item in self.selected_checkboxes:
            if item["checkbox_var"].get() == True:
                self.installing = True
                thread = False#init reference
                thread = threading.Thread(target=self.install_tool, args=(item, thread, previous_thread))
                thread.start()
                previous_thread=thread
                if item["restart"] == True:
                    break
        self.deselect_all_tools()

    def uninstall_tools(self):
        for item in self.selected_checkboxes:
            if item["checkbox_var"].get() == True:
                self.uninstall_tool(item)
        self.update_installations_list()

    def select_all_tools(self):
        for item in self.selected_checkboxes:
            item["checkbox_var"].set(True)
    def deselect_all_tools(self):
        for item in self.selected_checkboxes:
            item["checkbox_var"].set(False)
    def update_installations_list(self):
        # Update the listbox based on the installation status
        for item in self.installations_list:
            item_text = item["name"]
            version = item["versionName"]
            installed = self.is_installed(version)
            checkbox_var = item["var"]
            if installed:
                item_text += " (Installed)"
            else:
                item_text += " (Not Installed)"
                if item["restart"] == True:
                    item_text += " *App must restart"


            for item2 in self.installations_list:
                if item2["versionName"] == item["dependency"]:
                    item_text = item_text + " *Requires " + item2["name"] + "*"
                    break

            s=tk.NORMAL
            if item["dependency"] != "" and not self.is_installed(item["dependency"]):
                s=tk.DISABLED
                installed = False #Chaneg gui color

            if version in self.install_buttons:
                self.install_buttons[version][1].configure(text=item_text)
            else:
                self.install_buttons[version] = [customtkinter.CTkFrame(self.installations_listbox)]
                self.install_buttons[version].append(customtkinter.CTkCheckBox(self.install_buttons[version][0], text=item_text, variable=checkbox_var, state=s))
                self.install_buttons[version][0].pack(fill="x", padx=5, pady=5)
                self.install_buttons[version][1].pack(side="left")
                
                # Add the checkbox variable to the selected_checkboxes array
                self.selected_checkboxes.append({"checkbox_var": checkbox_var, "version": version, "name": item["name"], "restart": item["restart"]})


            if installed:
                self.install_buttons[version][1].configure(text_color="#90EE90")
            else:
                self.install_buttons[version][1].configure(text_color="#FFA500")
