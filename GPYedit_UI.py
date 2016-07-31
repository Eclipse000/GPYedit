
import os

from GtkApp  import *
from GPYedit import APPLICATION_NAME

class GPYedit_UI:

        """
        Handle user interface creation details.
        """

        def __init__(this, app_object):
                """
                Store a reference to the main application object
                and construct the user interface.
                """
                this.app = app_object
                this.window = app_object.window
                this.preferences = app_object.preferences
                this.window.set_title(APPLICATION_NAME)
                width, height = this.preferences.get_window_dimensions()
                this.window.set_default_size(width, height)
                this.build_GUI()
            

        def build_GUI(this):
                """
                Create the main interface components.
                These are
                        - vbox: Main vertical box for laying out widgets
                        - menu_bar: self explanatory
                        - notebook: The tabbed container holding our file buffers
                """
                this.vbox = gtk.VBox(False, 0)
                this.menu_bar = gtk.MenuBar()
                this.notebook = gtk.Notebook()
                this.notebook.set_scrollable(True)
                this.notebook.connect("switch-page", this.on_nb_page_switch)
                this.create_menus()
                this.create_toolbar()
                this.vbox.pack_start(this.notebook, True, True, 0)
                this.window.add(this.vbox)


        def editing_area_new(this):
                """
                Build the set of widgets necessary to allow
                for the editing of text.  This includes:
                        - scrolled window: allow viewing area to scroll
                        - text view: widget to edit text
                """
                scrolled_window = gtk.ScrolledWindow()
                scrolled_window.set_shadow_type(gtk.SHADOW_ETCHED_IN)
                scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
                scrolled_window.set_border_width(3)
                textview = gtk.TextView()
                textview.set_left_margin(3)
                textview.set_right_margin(3)
                textview.set_pixels_above_lines(1)
                textbuffer = textview.get_buffer()
                scrolled_window.add(textview)

                label = gtk.Label()

                textview.modify_base(gtk.STATE_NORMAL,
                        gtk.gdk.Color(this.preferences.get_background_color()))

                textview.modify_text(gtk.STATE_NORMAL,
                        gtk.gdk.Color(this.preferences.get_foreground_color()))

                # Set the default font used for editing

                textview.modify_font(
                        pango.FontDescription(this.preferences.get_font()))

                # Return a dictionary of the three elements.
                # Note that the scrolled window itself holds the
                # textview which in turn contains the buffer.  But
                # this helps avoid having to extract the children of
                # the scrolled window every time we need access to either
                # the view or the buffer inside it.

                return { "scrolled_window": scrolled_window,
                                "textview": textview,
                              "textbuffer": textbuffer,
                                   "label": label }


        def on_nb_page_switch(this, notebook, page, page_num):
                """
                Each time the user selects a tab to work with, change
                the internal tab indicator so that it can be used to get
                the relevant data associated with that tab.  This is a callback
                and there is no need to call directly.  See GTK+ 'switch-page' signal.
                """
                this.app.set_current_tab(page_num)

                file_info = this.app.get_current_file()

                if file_info.get_filename() is not None:
                        this.set_window_title(file_info.get_filename())
                else:
                        this.set_window_title()


        def set_window_title(this, filename = None, alt_title = ''):
                """
                Set the window title to a specific string with alt_title
                or work with an expected file name.  The format for showing
                the title information is:
                filename (directory path) - application name
                """
                if alt_title:
                        this.window.set_title(alt_title)
                elif filename is None:
                        this.window.set_title("Untitled - " + APPLICATION_NAME)   # Default title
                else:
                        dirpath, fname = os.path.split(filename)
                        this.window.set_title(fname + " (" + dirpath + ") - " + APPLICATION_NAME)


        def popup_search_box(this, menu_item = None):
                """
                Display the search dialog.
                """
                dial = gtk.Dialog("Find and Replace", this.window)
                dial.add_buttons(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                 gtk.STOCK_CONVERT, gtk.RESPONSE_APPLY,
                                 gtk.STOCK_FIND, gtk.RESPONSE_OK)
                dial.set_response_sensitive(gtk.RESPONSE_OK, False)
                dial.set_response_sensitive(gtk.RESPONSE_APPLY, False)
                table = gtk.Table(4, 2, False)
                table.set_row_spacings(8)
                table.set_col_spacings(8)
                find_label = gtk.Label("Search for:")
                find_label.set_alignment(0, 0.5)
                replace_label = gtk.Label("Replace with:")
                replace_label.set_alignment(0, 0.5)
                find_entry = gtk.Entry()
                replace_entry = gtk.Entry()
                case_sens = gtk.CheckButton("Case sensitive")
                replace_all = gtk.CheckButton("Replace all occurences")
                table.attach(find_label, 0, 1, 0, 1)
                table.attach(find_entry, 1, 2, 0, 1)
                table.attach(replace_label, 0, 1, 1, 2)
                table.attach(replace_entry, 1, 2, 1, 2)
                table.attach(case_sens, 0, 2, 2, 3)
                table.attach(replace_all, 0, 2, 3, 4)
                content_area = dial.get_content_area()
                content_area.pack_start(table)
                table.set_border_width(8)
                find_entry.connect("insert-text", this.search_buttons_sensitive, dial)
                find_entry.connect("backspace", this.search_buttons_insensitive, dial)
                dt_id = find_entry.connect("delete-text", this.search_buttons_insensitive_del_text, dial)
                find_entry.set_data('del_text_sig_id', dt_id)

                widgets = { 'find_entry': find_entry,
                         'replace_entry': replace_entry,
                            'match_case': case_sens,
                           'replace_all': replace_all }

                dial.connect("response", this.search_dialog_response, widgets)
                dial.show_all()
                dial.run()


        def search_buttons_insensitive_del_text(this, editable, start, end, search_dialog):
                """
                Similar to search_buttons_insensitive(), except that this
                handler is connected for the 'delete-text' signal.  It allows
                a user to highlight some text and delete it all at once.  In the
                case where they select and delete everything in the search box, the
                buttons along the bottom of the search dialog should become unusable.
                """
                if editable.get_text_length() > 0:
                        editable.handler_block(editable.get_data('del_text_sig_id'))
                        editable.delete_text(start, end)
                        editable.handler_unblock(editable.get_data('del_text_sig_id'))

                if editable.get_text_length() == 0:
                        search_dialog.set_response_sensitive(gtk.RESPONSE_OK, False)
                        search_dialog.set_response_sensitive(gtk.RESPONSE_APPLY, False)


        def search_buttons_sensitive(this, editable, new_text, new_text_length, pos, search_dialog):
                """
                Determine whether the buttons should be sensitive, thereby
                allowing the user to search, if there is text in the search box.
                """
                if editable.get_text_length() > 0:
                        return

                if new_text_length > 0:
                        search_dialog.set_response_sensitive(gtk.RESPONSE_OK, True)
                        search_dialog.set_response_sensitive(gtk.RESPONSE_APPLY, True)


        def search_buttons_insensitive(this, editable, search_dialog):
                """
                Make the search buttons insensitive when there is no
                text in the search box.
                """
                if editable.get_text_length() == 1:
                        search_dialog.set_response_sensitive(gtk.RESPONSE_OK, False)
                        search_dialog.set_response_sensitive(gtk.RESPONSE_APPLY, False)


        def run_save_as_dialog(this):
                """
                Display a Save As dialog box and allow the user to specify
                a file name to save to.
                """
                save_as = gtk.FileChooserDialog("Save As",
                                                this.window,
                                                gtk.FILE_CHOOSER_ACTION_SAVE,
                                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                gtk.STOCK_SAVE, gtk.RESPONSE_OK))
                action_id = save_as.run()
                save_as.hide()
                if action_id == gtk.RESPONSE_OK:
                        ret_val = (action_id, save_as.get_filename())
                else:
                        ret_val = (action_id, None)
                save_as.destroy()
                return ret_val


        def toggle_tb_visible(this, widget, data = None):
                """
                Callback to control visiblity of the toolbar
                """
                if widget.get_active():
                        this.toolbar.show()
                else:
                        this.toolbar.hide()


        def create_toolbar(this):
                """
                Create toolbar and buttons before packing into
                the main window.
                """
                this.toolbar = gtk.Toolbar()

                # Make toolbar widget buttons
                this.tb_new = gtk.ToolButton(gtk.STOCK_NEW)
                this.tb_open = gtk.ToolButton(gtk.STOCK_OPEN)
                this.tb_save = gtk.ToolButton(gtk.STOCK_SAVE)
                this.tb_save_as = gtk.ToolButton(gtk.STOCK_SAVE_AS)

                # Insert buttons into toolbar
                this.toolbar.insert(this.tb_new, 0)
                this.toolbar.insert(this.tb_open, 1)
                this.toolbar.insert(this.tb_save, 2)
                this.toolbar.insert(this.tb_save_as, 3)

                this.view_menu_toolbar.connect("toggled", this.toggle_tb_visible)

                # Tool bar 'new' button creates a new file.  The method signature
                # doesn't match the required parameters for this signal though so
                # we use a sort of pass-through function to get there.
                this.tb_new.connect("clicked",  lambda tool_item: this.app.create_new_file())
                this.tb_open.connect("clicked", lambda tool_item: this.app.open_file())
                this.tb_save.connect("clicked", lambda tool_item: this.app.save_file())

                # Pack toolbar into window vbox
                this.vbox.pack_start(this.toolbar, False, False, 0)


        def search_dialog_response(this, dialog, response, widgets):
                """
                Process the response returned from the search and replace dialog.
                """
                if response == gtk.RESPONSE_OK:
                        this.app.document_search(widgets)
                elif response == gtk.RESPONSE_CANCEL:
                        dialog.destroy()
                elif response == gtk.RESPONSE_APPLY:
                        this.app.document_replace(widgets)


        def create_menus(this):
                """
                Create the menu bar and associated menu items.
                """
                accel_group = gtk.AccelGroup()

                # Associate with main window
                this.window.add_accel_group(accel_group)

                this.create_file_menu(this.app, accel_group)
                this.create_edit_menu(this.app, accel_group)
                this.create_view_menu(this.app, accel_group)
                this.create_search_menu(this.app, accel_group)
                this.create_help_menu(this.app, accel_group)

                # Pack menu bar into main window
                this.vbox.pack_start(this.menu_bar, False, False, 0)


        def create_file_menu(this, app, accel_group):
                """
                Construct the File menu
                """
                # Create File menu
                this.file_menu = gtk.Menu()
                this.file_menu.set_accel_group(accel_group)
                this.file_menu_item = gtk.MenuItem("File")
                this.file_menu_item.set_submenu(this.file_menu)

                # Create menu items
                this.file_menu_new = gtk.ImageMenuItem(gtk.STOCK_NEW)
                this.file_menu_new.add_accelerator("activate", accel_group, ord('n'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
                this.file_menu_open = gtk.ImageMenuItem(gtk.STOCK_OPEN)
                this.file_menu_open.add_accelerator("activate", accel_group, ord('o'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
                this.file_menu_open_files_by_pattern = gtk.MenuItem("Open Files By Pattern")
                this.file_menu_save = gtk.ImageMenuItem(gtk.STOCK_SAVE)
                this.file_menu_save.add_accelerator("activate", accel_group, ord('s'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
                this.file_menu_save_as = gtk.ImageMenuItem(gtk.STOCK_SAVE_AS)
                this.file_menu_save_as.add_accelerator("activate",
                                                       accel_group,
                                                       ord('s'),
                                                       gtk.gdk.SHIFT_MASK | gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
                this.file_menu_close = gtk.ImageMenuItem(gtk.STOCK_CLOSE)
                this.file_menu_close.add_accelerator("activate", accel_group, ord('w'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
                this.file_menu_quit = gtk.ImageMenuItem(gtk.STOCK_QUIT)
                this.file_menu_quit.add_accelerator("activate", accel_group, ord('q'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)

                # Add them to File menu
                this.file_menu.append(this.file_menu_new)
                this.file_menu.append(this.file_menu_open)
                this.file_menu.append(this.file_menu_open_files_by_pattern)
                this.file_menu.append(this.file_menu_save)
                this.file_menu.append(this.file_menu_save_as)
                this.file_menu.append(this.file_menu_close)
                this.file_menu.append(this.file_menu_quit)

                # Connect signals
                this.file_menu_new.connect("activate", app.create_new_file)
                this.file_menu_open.connect("activate", app.open_file)
                this.file_menu_open_files_by_pattern.connect("activate", lambda menu_item: app.open_by_pattern())
                this.file_menu_save.connect("activate", lambda menu_item: app.save_file())
                this.file_menu_close.connect("activate", app.close_file)
                this.file_menu_quit.connect("activate", gtk.main_quit)

                # Add to menu bar
                this.menu_bar.append(this.file_menu_item)


        def create_edit_menu(this, app, accel_group):
                """
                Create the Edit menu
                """
                # Create Edit menu
                this.edit_menu = gtk.Menu()
                this.edit_menu_item = gtk.MenuItem("Edit")
                this.edit_menu_item.set_submenu(this.edit_menu)

                # Create menu items
                this.edit_menu_cut = gtk.ImageMenuItem(gtk.STOCK_CUT)
                this.edit_menu_cut.add_accelerator("activate", accel_group, ord('x'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
                this.edit_menu_copy = gtk.ImageMenuItem(gtk.STOCK_COPY)
                this.edit_menu_copy.add_accelerator("activate", accel_group, ord('c'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
                this.edit_menu_paste = gtk.ImageMenuItem(gtk.STOCK_PASTE)
                this.edit_menu_paste.add_accelerator("activate", accel_group, ord('v'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
                this.edit_menu_select_all = gtk.MenuItem("Select All")
                this.edit_menu_select_all.add_accelerator("activate", accel_group, ord('a'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
                this.edit_menu_preferences = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)

                # Add them to Edit menu
                this.edit_menu.append(this.edit_menu_cut)
                this.edit_menu.append(this.edit_menu_copy)
                this.edit_menu.append(this.edit_menu_paste)
                this.edit_menu.append(this.edit_menu_select_all)
                this.edit_menu.append(this.edit_menu_preferences)

                # Connect signals
                this.edit_menu_select_all.connect("activate", lambda menu_item: app.select_all())

                # Add to menu bar
                this.menu_bar.append(this.edit_menu_item)


        def create_view_menu(this, app, accel_group):
                """
                Create the View menu
                """
                # Create View menu
                this.view_menu = gtk.Menu()
                this.view_menu_item = gtk.MenuItem("View")
                this.view_menu_item.set_submenu(this.view_menu)

                # Create menu items
                this.view_menu_toolbar = gtk.CheckMenuItem("Toolbar")
                this.view_menu_toolbar.set_active(True)
                this.view_menu_file_explorer_pane = gtk.CheckMenuItem("File Browser Pane")

                # Add them to View menu
                this.view_menu.append(this.view_menu_toolbar)
                this.view_menu.append(this.view_menu_file_explorer_pane)

                # Add to menu bar
                this.menu_bar.append(this.view_menu_item)


        def create_search_menu(this, app, accel_group):
                """
                Create the Search menu
                """
                # Create Search menu
                this.search_menu = gtk.Menu()
                this.search_menu_item = gtk.MenuItem("Search")
                this.search_menu_item.set_submenu(this.search_menu)

                # Create menu items
                this.search_menu_s_and_r = gtk.ImageMenuItem(gtk.STOCK_FIND_AND_REPLACE)

                # Add them to Search menu
                this.search_menu.append(this.search_menu_s_and_r)

                # Connect signals
                this.search_menu_s_and_r.connect("activate", this.popup_search_box)

                # Add to menu bar
                this.menu_bar.append(this.search_menu_item)


        def create_help_menu(this, app, accel_group):
                """
                Create the Help menu
                """
                # Create Help menu
                this.help_menu = gtk.Menu()
                this.help_menu_item = gtk.MenuItem("Help")
                this.help_menu_item.set_submenu(this.help_menu)

                # Create menu items
                this.help_menu_about = gtk.ImageMenuItem(gtk.STOCK_HELP)

                # Add them to Help menu
                this.help_menu.append(this.help_menu_about)

                # Add to menu bar
                this.menu_bar.append(this.help_menu_item)
