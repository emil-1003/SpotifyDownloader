import requests
import eyed3
from io import BytesIO

def attach_image_to_mp3(mp3_file_path, image_url):
    # Download the image from the URL
    response = requests.get(image_url)
    if response.status_code != 200:
        print(f"Failed to download image from {image_url}")
        return

    # Open the MP3 file
    audiofile = eyed3.load(mp3_file_path)
    if audiofile is None:
        print(f"Failed to load MP3 file: {mp3_file_path}")
        return

    # Attach the downloaded image to the MP3 file
    audiofile.tag.images.set(3, response.content, 'image/jpeg', u"Description")

    # Save the changes
    audiofile.tag.save()

    print(f"Image attached to {mp3_file_path}")

# Example usage
mp3_file_path = "music/test  Emil Storgaard Andersen/Blå Himmel feat Hans Philip - KESI Hans Philip.mp3"
image_url = "https://i.scdn.co/image/ab67616d0000b273e20cd4a6be3a68a75aba28c9"
attach_image_to_mp3(mp3_file_path, image_url)