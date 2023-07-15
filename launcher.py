import subprocess
import urllib.request
import os
from pathlib import Path

def main():
    # Perform any pre-launch tasks here

    user_home = str(Path.home())
    directory = os.path.join(user_home, "RODAssistant")
    check_folder(directory)
    versionDir = os.path.join(directory, "App")
    check_folder(versionDir)

    # Local file paths
    local_version_file = "version.txt"
    local_app_file = "RodaApp.exe"

    # GitHub repository URL
    github_repo_url = "https://github.com/zacharie410/RODA--Roblox-Developer-Assistant/tree/main/"

    # Step 1: Read the local version
    with open(local_version_file, "r") as file:
        local_version = file.read().strip()

    # Step 2: Fetch the remote version from GitHub
    remote_version_url = github_repo_url + "version.txt"
    with urllib.request.urlopen(remote_version_url) as response:
        remote_version = response.read().decode().strip()

    # Step 3: Compare local and remote versions
    if local_version != remote_version:
        print("Update available!")

        # Step 4: Download the updated app.exe file
        remote_app_url = github_repo_url + "dist/RodaApp.exe"
        urllib.request.urlretrieve(remote_app_url, local_app_file)

        # Step 5: Replace the current app.exe file

        # Delete the current app.exe file
        if os.path.exists(local_app_file):
            os.remove(local_app_file)

        # Rename the downloaded file to app.exe
        # os.rename(local_app_file + ".download", local_app_file)

        # Step 6: Update the local version file
        with open(local_version_file, "w") as file:
            file.write(remote_version)
    else:
        print("No updates available.")

    # Launch your main program
    launch_program()

def launch_program():
    # Execute the RodaApp.py executable
    command = ["python", "RodaApp.py"]
    subprocess.run(command)


def check_folder(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

if __name__ == "__main__":
    main()
