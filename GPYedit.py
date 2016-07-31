#!/usr/bin/env python

import os
import sys

from GtkApp           import *
from GPYedit_conf     import Preferences
from GPYedit_file     import GPYedit_File
from GPYedit_state    import EditableState, NoneditableState

APPLICATION_NAME = 'GPYedit'

class GPYedit(GtkApp_Toplevel):

        """
        Main application class
        """

        def __init__(this):
                """
                This is where it all starts.  Begin by setting
                the window geometry and title and decide whether
                to create a new empty file or use the arguments provided.

                """
                GtkApp_Toplevel.__init__(this)

                # For each tab in the notebook, we will store
                # our data representing each file (or empty buffer)
                # in a list.  Each item is a dictionary keeping track of the:
                #   - Python file object
                #   - Three components of editing area: scrolled window, textview, and buffer (per tab)
                #   - Full pathname of the file being edited
                #   - Text shown in the notebook widget tabs

                this.open_files = [ ]

                # Keep track of which buffer we're dealing with.
                # Each time the notebook page is switched, this number
                # will change (see 'on_nb_page_switched' callback).  This value 
                # is used as the index into the open files list to get at the
                # file-specific information and widgets.

                this.current_tab = 0

                # User preferences will be accessible through this attribute.
                # The Preferences class will be initialized from directives
                # found in the gpyedit_settings.ini file.

                this.preferences = Preferences()

                this.editable_state = EditableState(this)
                this.noneditable_state = NoneditableState(this)
                this.ui = GPYedit_UI(this)
                if len(sys.argv) > 1:
                        names = sys.argv[1:]
                        for name in names:
                                if os.path.exists(name) and os.path.isfile(name):
                                        this.tab_new_from_contents(name)
                                else:
                                        print 'File "' + name + '" doesn\'t exist.'
                else:
                        this.create_new_file()

                this.set_state(this.editable_state)


        def create_new_file(this, menu_item = None):
                """
                Create a blank buffer with no associated Python file object or name (yet)
                NOTE: menu_item is a parameter here because
                this method will be used as a signal handler
                also for the File menu 'new' item and the prototype
                for that handler requires this parameter.  It is not used though.

                """
                edit_area = this.ui.editing_area_new()

                new_file = GPYedit_File(edit_area)

                this.open_files.append(new_file)

                notebook = this.ui.notebook
                index = notebook.append_page(edit_area["scrolled_window"], new_file.get_tab_label())
                notebook.show_all()
                return this.open_files[index]


        def tab_new_from_contents(this, filename):
                """
                Open a new tab and dump the contents of a file
                into it.
                """
                # Remove this conditional
               # if this.check_for_used_file_name(filename):
                #        return

                edit_area = this.ui.editing_area_new()

                new_file = GPYedit_File(edit_area, filename)
                new_file.load_data_from_file()

                this.open_files.append(new_file)

                notebook = this.ui.notebook
                index = notebook.append_page(edit_area["scrolled_window"], new_file.get_tab_label())
                notebook.show_all()
                return this.open_files[index]


        def open_file(this, menu_item = None):
                """
                Open a file
                NOTE: May need to revise a little bit. What happens when there
                      is no tab?
                """
                error = False

                chooser = gtk.FileChooserDialog("Open A File", this.window)
                chooser.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
                chooser.add_button(gtk.STOCK_OPEN, gtk.RESPONSE_OK)
                response = chooser.run()
                if response == gtk.RESPONSE_OK:
                        filename = chooser.get_filename()
                        if os.path.exists(filename) and os.path.isfile(filename):
                                # Might remove conditional or function
                                if this.check_for_used_file_name(filename):
                                        gtk.Widget.destroy(chooser)
                                        return
                                try:
                                        F = this.get_current_file()
                                except IndexError:
                                        # If there are no tabs, we can't grab the file data
                                        # so make sure there's something to work with.
                                        F = this.create_new_file()
                                if F.get_filename() is None and not F.get_edit_area("textbuffer").get_modified():
                                        F.set_filename(filename)
                                        F.load_data_from_file()
                                        this.ui.notebook.set_tab_label_text(F.get_edit_area("scrolled_window"), F.get_tab_label_text())
                                        this.open_files[this.current_tab] = F
                                else:
                                        F = this.tab_new_from_contents(filename)
                                this.ui.set_window_title(filename)
                        else:
                                error = gtk.MessageDialog(parent = this.window,
                                                          type = gtk.MESSAGE_ERROR,
                                                          buttons = gtk.BUTTONS_OK,
                                                          message_format = "The file '" + filename + "' doesn't exist!")

                gtk.Widget.destroy(chooser)

                if error:
                        error.run()
                        error.destroy()


        def close_file(this, menu_item = None):
                """
                Close a file.  Determines whether the 'file' to be closed
                is just a scratch buffer with some text in it or if it has
                a file name (in which case there is an associated Python file object).
                If the buffer has been modified since it was either opened or the user
                typed some text in, give them a chance to save the data to a file on disk
                before removing the tab from the notebook widget.
                """
                this.state.close_file()


        def save_file(this, filename = None, data = ''):
                """
                Write the contents of a buffer to a file on disk.
                """
                notebook = this.ui.notebook
                if notebook.get_n_pages() == 0:
                        return

                current_file = this.get_current_file()

                start, end = current_file['edit_area']['buffer'].get_bounds()

                text_to_write = current_file['edit_area']['buffer'].get_text(start, end)

                if filename is not None:
                        if len(data) > 0:
                                obj = open(filename, 'w')
                                obj.write(data)
                                obj.close()
                        else:
                                # Filename given but no data passed. Dump contents of current buffer
                                # into a file specified by 'filename' argument.
                                obj = open(filename, 'w')
                                obj.write(text_to_write)
                                obj.close()
                else:
                        # Filename to save to was not provided.
                        # If the current buffer has no file name, then show a "Save As"
                        # dialog and prompt them to specify a file name.
                        if current_file['filename'] is None:
                                (action, selected_filename) = this.ui.run_save_as_dialog()
                                if action == gtk.RESPONSE_OK:
                                        current_file['filename'] = selected_filename
                                        current_file['file_object'] = open(selected_filename, 'w+')
                                        current_file['file_object'].write(text_to_write)
                                        current_file['label'].set_text(os.path.basename(selected_filename))
                                        current_file['edit_area']['buffer'].set_modified(False)
                                        this.open_files[this.current_tab] = current_file
                                        this.ui.set_window_title(selected_filename)
                        else:
                                # Current buffer has associated file name.
                                # Save to that file.
                                curr_file_obj = current_file['file_object']
                                curr_file_obj.truncate(0)
                                curr_file_obj.seek(0)
                                curr_file_obj.write(text_to_write)
                                current_file['edit_area']['buffer'].set_modified(False)


        def save_file(this, filename = None, data = ""):
                """
                Write the contents of the GtkTextBuffer to a file on disk.
                """
                if this.ui.notebook.get_n_pages() == 0:
                        return

                current_file = this.get_current_file()

                start, end = current_file.get_edit_area("textbuffer").get_bounds()

                contents_to_write = current_file.get_edit_area("textbuffer").get_text(start, end)

                


        def select_all(this):
                """
                Select all the text in the editing area.
                """
                current_file = this.get_current_file()
                textbuffer = current_file.get_edit_area("textbuffer")
                start, end = textbuffer.get_bounds()
                textbuffer.select_range(start, end)


        def document_search(this, widgets):
                """
                NOTE: Function not finished.
                By default, do a forward search on the document in
                the tab with focus.  To work, this function should
                get these widgets:
                        - find entry text box with the search text
                        - replace entry with replacement text
                        - match case checkbox
                        - text buffer for current file
                """
                if widgets['match_case'].get_active():
                        case_sensitive = True
                else:
                        case_sensitive = False

                current_file = this.get_current_file()

                print current_file

                textbuffer = current_file.get_edit_area("textbuffer")
                start_iter = textbuffer.get_start_iter()
                search_text = widgets['find_entry'].get_text()
                begin, end = start_iter.forward_search(search_text, gtk.TEXT_SEARCH_TEXT_ONLY)
                textbuffer.select_range(begin, end)
            
            
        def document_replace(this, widgets):
                """
                Find a search string and replace it with new text.
                By default, only one replacement is done but with
                the 'replace all occurences' checkbox selected then
                it will perform a global search and replace.
                """
                current_file = this.get_current_file()
                textbuffer = current_file.get_edit_area("textbuffer")
                start_iter = textbuffer.get_start_iter()
                search_text = widgets['find_entry'].get_text()
                if widgets['replace_entry'].get_text_length() > 0:
                        lower, upper = textbuffer.get_bounds()
                        contents = textbuffer.get_text(lower, upper)
                        replace_str = widgets['replace_entry'].get_text()
                        if widgets['replace_all'].get_active():
                                # REPLACE ALL
                                updated_text = contents.replace(search_text, replace_str)
                        else:
                                # REPLACE ONCE
                                updated_text = contents.replace(search_text, replace_str, 1)
                        textbuffer.set_text(updated_text)
                        textbuffer.set_modified(False)
                else:
                        # ERROR: NO REPLACEMENT TEXT GIVEN
                        pass


        def check_for_used_file_name(this, name):
                """
                Any given file should only be opened in one tab.
                This method returns True if a specified file's name
                is already in use.
                
                for element in this.open_files:
                        values = element.values()
                        if name in values: return True
                """


        def delete_event(this, widget, event, data = None):
                """
                Override method to close all files if a user clicks the 'X'
                button to close the text editor without first manually closing
                them via the File > Close menu option. Just explicitly cleaning up.
                """
                for F in this.open_files:
                        file_to_clean_up = F.get_python_file_object()
                        if file_to_clean_up:
                                file_to_clean_up.close()
                return False


        def open_by_pattern(this):
                """
                Open all files that match a shell-style pattern.
                """
                items = glob.glob(os.environ['HOME'] + os.sep + '*.php')
                for item in items:
                        this.tab_new_from_contents(item)

        def get_current_file(this):
                """
                Return all the data and GTK+ widgets associated with
                an element in the open files list based on the active
                GtkNotebook tab number.
                """
                return this.open_files[this.current_tab]

        def set_current_tab(this, value):
                """
                Set the current tab indicator.
                """
                this.current_tab = value

        def set_state(this, state):
                this.state = state


########## Main ##########

if __name__ == "__main__":

        from GPYedit_UI import GPYedit_UI

        GPYedit().main()

##########################
