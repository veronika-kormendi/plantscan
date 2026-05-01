import watchdog.events
import watchdog.observers
import time
import config_refactor as config
# use this for annotated images
# import watchdog_pipeline as w_pipe
# use this for new images to identify
import watchdog_pipeline_for_new_images_no_annotation as w_pipe

class Handler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self):
        # Set the patterns for PatternMatchingEventHandler
        watchdog.events.PatternMatchingEventHandler.__init__(self, patterns=['*.HEIC'],
                                                             ignore_directories=True, case_sensitive=False)
#when new file is added to the folder
    def on_created(self, event):
        uploaded_filepath = event.src_path
        print("Watchdog received created event, new file is saved to the folder - % s" % event.src_path)
        # call watchdog pipeline code here
        gscale_path = w_pipe.preprocess_cropped_image(uploaded_filepath) #get the image preprocessed
        w_pipe.process_cropped_image(gscale_path) # continue with pipeline tasks

    def on_modified(self, event):
        print("Watchdog received modified event - % s." % event.src_path)

def start_folder_watcher():
    src_path = config.FOLDER_TO_WATCH
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

# for testing this unit
# if __name__ == "__main__":
#     start_folder_watcher()