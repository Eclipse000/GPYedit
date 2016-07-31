
import os

from utils import find_file

CONFIG_FILE = "gpyedit_settings.ini"

class Preferences:

        """
        Manage user preferences
        """

        settings = { "window_width": 779,
                    "window_height": 419,
                        "font_face": "monospace",
                 "background_color": "#FFFFFF",
                 "foreground_color": "#000000" }

        def __init__(this):
                """
                Read the configuration file and set up the
                preferences so that they are ready to be accessed
                by the main application.

                """
                if not os.path.exists(CONFIG_FILE): config_file_location = find_file(CONFIG_FILE, os.environ["HOME"])
                else:
                        config_file_location = os.getcwd() + os.sep + CONFIG_FILE

                if config_file_location is None: return  # Configuration not found. Use default settings
                else:
                        this.process_options(open(config_file_location, "r").readlines())


        def process_options(this, config):
                """
                Parse configuration options in the gpyedit_settings.ini file.
                """
                for option in config:
                        if option.startswith('#'):       # Skip comments
                                continue

                        data = option.split(":")         # Get [option, value]

                        if len(data) != 2:
                                continue

                        opt, val = (data[0].strip(), data[1].strip())
                        if opt in this.settings.keys():
                                this.settings[opt] = val

        def run_dialog(this):
                """
                Create the preferences dialog box accessible through Edit > Preferences in
                the application window menu bar.
                """
                


        def get_font(this):
                """
                Return the font that should be used for editing text.
                """
                return Preferences.settings["font_face"]


        def get_background_color(this):
                """
                Return the background color of the editing area.
                """
                return Preferences.settings["background_color"]


        def get_foreground_color(this):
                """
                Return the foreground color of the editing area.
                """
                return Preferences.settings["foreground_color"]


        def get_window_dimensions(this):
                """
                Retrieve the toplevel window dimensions as a width and height
                """
                return (int(this.settings["window_width"]), int(this.settings["window_height"]))
