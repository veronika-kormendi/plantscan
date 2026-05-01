import watchdog.events
import watchdog.observers
import time
import config_refactor as config

class Handler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self):
        # Set the patterns for PatternMatchingEventHandler
        watchdog.events.PatternMatchingEventHandler.__init__(self, patterns=['*.HEIC'],
                                                             ignore_directories=True, case_sensitive=False)
#when new file is added to the folder
    def on_created(self, event):
        print("Watchdog received created event - % s." % event.src_path)
        # call watchdog pipeline code here

    def on_modified(self, event):
        print("Watchdog received modified event - % s." % event.src_path)
        # Event is modified, you can process it now


def start_folder_watcher():
    src_path = config.INPUT_FOLDER
    event_handler = Handler()
    observer = watchdog.observers.Observer()
    observer.schedule(event_handler, path=src_path, recursive=True)
    observer.start()
    print(f"Watchdog started. watching {src_path}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()