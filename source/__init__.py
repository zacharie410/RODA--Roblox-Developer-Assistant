# source/__init__.py

# Import necessary modules or names to be directly accessible when importing the package
from customtkinter import (
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

from .EmbeddedCommandPrompt import EmbeddedCommandPrompt
from .ProjectAPI import ProjectAPI
from .ProjectCreatorHandler import ProjectCreatorHandler
from .ViewProjectsFrame import ViewProjectsFrame
from .ProjectCreator import ProjectCreator
from .InstallManager import InstallManager

