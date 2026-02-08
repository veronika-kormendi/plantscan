from PIL import Image
import pillow_heif

# register HEIF opener with Pillow
pillow_heif.register_heif_opener()

# open the HEIC file
img = Image.open('G:\\My Drive\\plantscan_photos_to_process\\IMG_7522.HEIC')

# save image as JPG
img.save('G:\\My Drive\\plantscan_photos_to_process\\IMG_7522.jpg', format='JPEG')


def hello_world():
    print("Hello World!")

hello_world()

