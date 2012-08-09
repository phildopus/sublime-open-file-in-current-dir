import sublime
import sublime_plugin
import os, re

class OpenFileInCurrentDirectoryCommand(sublime_plugin.WindowCommand):
    current_files = None

    def run(self):
        current = self.window.active_view().file_name()

        if current:
            self.select_file(current)

        else:
            message = "You must save the file before it has a directory"
            sublime.status_message(message)

    def is_enabled(self):
        return self.window.active_view() is not None

    def select_file(self, target):
        self.current_files = self.files(target)
        display_files = [[path, self.path(fullpath)] for path, fullpath in self.current_files]
        self.window.show_quick_panel(display_files, self.switch_to)

    def switch_to(self, index):
        if index < 0:
            return

        selected = self.current_files[index][1]

        if os.path.isdir(selected):
            self.select_file(selected)
        else:
            self.window.open_file(selected)

    def files(self, current):
        base_dir = current if os.path.isdir(current) else os.path.dirname(current)
        paths = os.listdir(base_dir)

        full = lambda p: "%s/%s" % (base_dir, p)
        disp = lambda f, p: "%s/" % p if os.path.isdir(f) else p

        files = [[disp(full(path), path), full(path)] for path in paths if not self.excluded(full(path))]
        files.insert(0, ["..", os.path.dirname(base_dir)])
        return files

    def path(self, fullpath):
        folders = self.window.folders()
        for folder in folders:
            if os.path.commonprefix([folder, fullpath]) == folder:
                relpath = os.path.relpath(fullpath, folder)
            
                if len(folders) > 1:
                    return os.path.join(os.path.basename(folder), relpath)

                return relpath

        return fullpath

    def excluded(self, fullpath):
        settings = self.window.active_view().settings()
        if os.path.isdir(fullpath):
            patterns = settings.get("folder_exclude_patterns", [])
        else:
            patterns = settings.get("file_exclude_patterns", [])

        wc2re = lambda wc: wc.replace(".", "\.").replace("*", "(.*)")
        for pattern in patterns:
            if re.search(wc2re(pattern), os.path.basename(fullpath)) is not None:
                return True

        return False
