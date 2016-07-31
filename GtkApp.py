
import gtk, pygtk, pango

pygtk.require('2.0')

class GtkApp_Toplevel:
      """
      This class creates a standard toplevel GtkWindow
      widget with default handlers connected to delete_event
      and destroy signals, respectively. To use, simply derive
      new classes from this base and extend your new classes
      constructor by calling back to the __init__ here. Example:

      class MyGUI(GtkApp_Toplevel):
            def __init__(this):
                  GtkApp_Toplevel.__init__(this)
                  ...custom extension code...

      if __name__ == "__main__":
            Obj = MyGUI().main()

      Attributes defined: this.window
      """
      def __init__(this):
            this.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            this.window.connect("delete_event", this.delete_event)
            this.window.connect("destroy", this.destroy)

      def delete_event(this, widget, event, data = None):
            """
            By returning False, we ask that GTK+ emit the destroy signal.
            Override this function in a derived class to change this behavior.
            """
            return False

      def destroy(this, widget, data = None):
            gtk.main_quit()

      def main(this):
            """
            Control of our application ends here. GTK+ will sleep in its main
            event loop waiting for events to occur. e.g. mouse clicks
            """
            this.window.show_all()
            gtk.main()

########## Main ##########

if __name__ == "__main__":
      GtkApp_Toplevel().main()

##########################
