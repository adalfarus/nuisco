from aplustools.logs import TypeLogger, LogType
from pathlib import Path
import os
from aplustools import environment as env
import re
from aplustools.updaters import vNum
from aplustools.system import System
from aplustools.database import DBManager
import requests
from typing import Optional, List
import cProfile
import pstats
import sys

# You can remove this
import time

from modules.classes import clss_init, AdvancedQMessageBox
from modules.gui import gui_init, MainController
from modules import link

env.set_working_dir_to_main_script_location()
__cwd__ = os.getcwd()
__program_name__ = "{{project_name}}"
__version__ = "0.0.1.0"
__os__ = "Windows"
__os_version__ = "any"
__major_os_version__ = ["10", "11"]
__py_version__ = tuple(map(int, "{{pyversion}}".split(".")))

class Settings:
    def __init__(self, new, db, overwrite_settings: Optional[dict]=None):
        self.new = new
        self.db = db
        self.settings = {
            "test": "True"
        }
        if overwrite_settings:
            self.settings.update(overwrite_settings)
        if self.new == True: self.setup_database(self.settings)
        self.fetch_data()

    def boolean(self, to_boolean: str) -> bool:
        return to_boolean.lower() == "true"
        
    def str_to_list(self, s: str) -> List[str]:
        return s.split(", ")

    def list_to_str(self, lst: List[str]) -> str:
        return ', '.join(lst)

    def get(self, key: str):
        value = self.settings.get(key)
        if key in ["test"]:
            return self.boolean(value)
        return value

    def set(self, key: str, value):
        if key in ["test"]:
            value = str(value)
        self.settings[key] = value
        self.update_data()
        
    def get_test(self):
        return self.get("provider")

    def set_test(self, value):
        self.set("provider", value)

    def setup_database(self, settings):
        # Define tables and their columns
        tables = {
            "settings": ["key TEXT", "value TEXT"]
        }
        # Code to set up the database, initialize password hashes, etc.
        for table_name, columns in tables.items():
            self.db.create_table(table_name, columns)
        for i in self.settings:
            self.db.update_info(i, "settings", ["key", "value"])
        
    def fetch_data(self):
        fetched_data = self.db.get_info("settings", ["key", "value"])
        for item in fetched_data:
            key, value = item
            self.settings[key] = value

    def update_data(self):
        for key, value in self.settings.items():
            self.db.update_info((key, value), "settings", ["key", "value"])


class MainApp:
    def __init__(self):
        def check_for_update():
            response = requests.get("https://raw.githubusercontent.com/adalfarus/update_check/main/tpp/update.json")
            try:
                update_json = response.json()
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                return
            except requests.exceptions.JSONDecodeError as e:
                print(f"An error occurred: {e}")
                return
            except ValueError as e:
                print(f"An error occurred: {e}")
                return
            newestVersion = vNum(update_json["metadata"]["newestVersion"])
            newestVersionData = update_json["versions"][-1]
            push = newestVersionData["push"].title() == "True"
            count = 2
            while (not push and newestVersion > __version__) and count <= len(update_json["versions"]):
                newestVersionData = update_json["versions"][-count]
                count += 1
                push, newestVersion = newestVersionData["push"].title() == "True", vNum(newestVersionData['versionNumber'])
            if newestVersion > __version__ and self.settings.get_update_info() and push:
                title = "There is an update available"
                text = f"There is a newer version ({newestVersion}) available.\nDo you want to open the link to the update?"
                description = newestVersionData.get("Description", newestVersionData["description"])
                checkbox = QCheckBox("Do not show again")
                msg_box = AdvancedQMessageBox(self, QMessageBox.Question, title, text, description, checkbox, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

                retval = msg_box.exec()

                if checkbox.isChecked():
                    print("Do not show again selected")
                    self.settings.set_update_info(False)
                if retval == QMessageBox.Yes:
                    link = "https://github.com/adalfarus/update_check/blob/main/sorry.md"
                    QDesktopServices.openUrl(QUrl(link))
            elif self.settings.get_no_update_info() and (push or newestVersion == __version__):
                title = "Info"
                text = f"No new updates available.\nChecklist last updated {update_json['metadata']['lastUpdated'].replace('-', '.')}."
                description = newestVersionData.get("Description", newestVersionData["description"])
                checkbox = QCheckBox("Do not show again")
                msg_box = AdvancedQMessageBox(self, QMessageBox.Information, title, text, description, checkbox, QMessageBox.Ok, QMessageBox.Ok)
                
                retval = msg_box.exec()

                if checkbox.isChecked():
                    print("Do not show again selected")
                    self.settings.set_no_update_info(False)
            elif self.settings.get_no_update_info() and not push:
                title = "Info"
                text = f"New version available, but not recommended {newestVersion}.\nChecklist last updated {update_json['metadata']['lastUpdated'].replace('-', '.')}."
                description = newestVersionData.get("Description", newestVersionData["description"])
                checkbox = QCheckBox("Do not show again")
                msg_box = AdvancedQMessageBox(self, QMessageBox.Information, title, text, description, checkbox, QMessageBox.Ok, QMessageBox.Ok)
                
                retval = msg_box.exec()

                if checkbox.isChecked():
                    print("Do not show again selected")
                    self.settings.set_no_update_info(False)
            else: print("Bug, please fix me.")
        log("Running ...", LogType.DEBUG)
        self.gui = MainController() # Find a way to run gui as instance, instead of main
        self.gui.start()
        #self.gui.changed.connect(self.check_changes)
        db_path = ".\\data.db"
        self.new = not os.path.isfile(db_path)
        self.db = DBManager(db_path)
        self.settings = Settings(self.new, self.db, {"test": "False"})
        self.settings.set_test(True)
        log(self.settings.get_test())
        
    def check_changes(self):
        changes = self.gui.changes()
        log(changes)
        
    def close(self):
        log("Closing MainApp", LogType.DEBUG)
        self.db.close()
    

profiler = cProfile.Profile()
profiler.enable()

def order_logs(logs_dir):
    if not logs_dir.is_dir(): os.mkdir(logs_dir)
    elif any([x == "latest.log" for x in os.listdir(logs_dir)]):
        name = logs_dir / "latest.log"
        with open(name, "r") as f: line = f.readline()
        try: date = re.search(r"[\[\(](\d{4}-\d{2}-\d{2})", line).group(1)
        except AttributeError: os.remove(name); return
        new_name = logs_dir / f"{date}.log"
        if not os.path.exists(new_name) and not os.path.exists(logs_dir / f"{date}-1.log"):
            os.rename(name, new_name)
        elif os.path.exists(new_name) and not os.path.exists(logs_dir / f"{date}-1.log"):
            os.rename(new_name, logs_dir / f"{date}-1.log")
            os.rename(name, logs_dir / f"{date}-2.log")
        else:
            def extract_num(name):
                match = re.search(r'(\d+)\.log$', name)
                return int(match.group(1)) if match else None
            names = [x for x in os.listdir(logs_dir) if date in x]
            new_number = max(extract_num(name) for name in names) + 1
            os.rename(name, logs_dir / f"{date}-{new_number}.log")

if __name__ == "__main__":
    sy, exit = System(), 0 # Check if environment is suitable
    if sy.get_os() != __os__: exit = 1
    if sy.get_os_version() != __os_version__ and __os_version__ != "any": exit = 1
    if not sy.get_major_os_version() in __major_os_version__: exit = 1
    if sys.version_info[:2] != __py_version__: exit = 1
    if exit: sys.exit(0)
    logs_dir = Path(os.path.abspath(".\\logs\\"))
    order_logs(logs_dir) # Making sure the logs are all in order
    with TypeLogger(logs_dir / "latest.log") as logger:
        link.init(logger); gui_init(); clss_init()
        global log
        log = link.log
        main = MainApp()
        time.sleep(10)
        main.close()
        
if profiler:
    profiler.disable()
    
    # Save profile results to a file
    profiler.dump_stats('profile_results.prof')
    
    # Load profile results from file
    p = pstats.Stats('profile_results.prof')

    # Strip directory names from file paths in the profile output
    p.strip_dirs()

    # Sort the profile results by cumulative time spent in functions
    p.sort_stats('cumulative')

    # Print the top 10 functions that took the most time
    p.print_stats(10)

    # Alternatively, you can filter the results to include only functions
    # that took more than a certain amount of time, for example, 0.1 seconds:
    p.fcn_list = [key for key, value in p.stats.items() if value[3] > 0.1]  # value[3] is the cumulative time
    p.print_stats()            

