
import os

class GPYedit_File:

        """
        Class to represent a "file" in the GPYedit application.
        A file has several widgets that it is associated with as well
        as a Python file object and filename. The associated GTK+ widgets
        for the editing area are:
          - Label
          - Scrolled window
          - Textview and Textbuffer
        """

        def __init__(this, edit_area, filename = None):
                this.edit_area = edit_area
                this.file_object = None

                if filename:
                        this.file_object = open(filename, "r+w")

                this.filename = filename
                this.edit_area["label"].set_text(this.get_base_filename())


        def get_python_file_object(this):
                return this.file_object


        def get_edit_area(this, component):
                if component in this.edit_area: return this.edit_area[component]
                else:
                        return this.edit_area


        def get_filename(this):
                return this.filename


        def set_filename(this, filename):
                if this.file_object:
                        this.file_object.close()

                this.filename = filename
                this.file_object = open(filename, "r+w")


        def get_base_filename(this):
                if this.filename:
                        return os.path.basename(this.get_filename())

                return "Untitled"


        def get_tab_label(this):
                return this.edit_area["label"]


        def get_tab_label_text(this):
                return this.edit_area["label"].get_text()


        def load_data_from_file(this):
                if this.file_object is None:
                        raise Exception, "No file object association!"

                contents = this.file_object.read()
                this.edit_area["textbuffer"].set_text(contents)
                this.edit_area["textbuffer"].set_modified(False)
                this.edit_area["label"].set_text(this.get_base_filename())
