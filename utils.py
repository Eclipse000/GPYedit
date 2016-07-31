
import os

def find_file(name, root = None, trace = False):
        """
        Return the full path to a specified file by looking in
        the directory rooted at 'root' and below (in subdirs).
        If no path is given, use the current working directory.
        """
        if root is None:
                root = os.getcwd()

        for (dirpath, dirnames, filenames) in os.walk(root):
                if trace: print "Looking in", dirpath
                filename = os.path.join(dirpath, name)
                if os.path.isfile(filename):
                        return filename
        else:
                if trace: print "'%s' not found!" % name
