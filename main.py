import os
import re
import requests
import string
import eyed3
from io import BytesIO
import time
from concurrent.futures import ThreadPoolExecutor

class MusicScraper():
    def __init__(self):
        self.session = requests.Session()

    def scrape_playlist(self, spotify_playlist_link, music_folder, headers):           
        playlist_id = self.get_playlist_id(spotify_playlist_link)
        
        playlist_name = self.get_playlist_name(playlist_id, headers)
            
        playlist_folder_path = self.create_folder_path(playlist_name, music_folder)

        tracklist_url = f'https://api.spotifydown.com/trackList/playlist/{playlist_id}'
        offset_data = {}
        offset = 0
        offset_data['offset'] = offset

        while offset is not None:
            response = self.session.get(url=tracklist_url, params=offset_data, headers=headers)
            if response.status_code == 200:
                track_list = response.json()['trackList']
                page = response.json()['nextOffset']
                
                print("*"*100)
                with ThreadPoolExecutor() as executor:
                    for count, song in enumerate(track_list):
                        print("[*] Downloading : ", song['title'], "-", song['artists'])
                        executor.submit(self.download_song, song, playlist_folder_path, headers)
                        
                # Wait for all threads to finish
                executor.shutdown()
            if page is not None:
                offset_data['offset'] = page
                # TODO: ved ikke helt hvorfor den er her:
                response = self.session.get(url=tracklist_url, params=offset_data, headers=headers)
            else:
                print("*"*100)
                print('[*] Download Complete!')
                print("*"*100)
                break

    def get_playlist_name(self, Playlist_ID, headers):
        URL = f'https://api.spotifydown.com/metadata/playlist/{Playlist_ID}'
        meta_data = self.session.get(headers=headers, url=URL)
        playlist_name = meta_data.json()['title'] + ' - ' + meta_data.json()['artists']
        print('Playlist Name : ', playlist_name)
        return playlist_name

    def V2catch(self, SONG_ID, headers):
        x = self.session.get(url = f'https://api.spotifydown.com/download/{SONG_ID}', headers=headers)

        if x.status_code == 200:

            return {
                'link' : x.json()['link'],
                'metadata' : None
            }

        return None

    def get_playlist_id(self, link):
        # Define the regular expression pattern for the Spotify playlist URL
        pattern = r"https://open\.spotify\.com/playlist/([a-zA-Z0-9]+)\?si=.*"

        # Try to match the pattern in the input text
        match = re.match(pattern, link)

        if not match:
            raise ValueError("Invalid Spotify playlist URL.")
        # Extract the playlist ID from the matched pattern
        playlist_id = match.group(1)

        return playlist_id
        
    def create_folder_path(self, playlist_name, music_folder):
        folder_path = ''.join(e for e in playlist_name if e.isalnum() or e in [' ', '_'])
        playlist_folder_path = os.path.join(music_folder, folder_path)

        if not os.path.exists(playlist_folder_path):
            os.makedirs(playlist_folder_path)
        
        return playlist_folder_path

    def download_song(self, song, playlist_folder_path, headers):
        filename = song['title'].translate(str.maketrans('', '', string.punctuation)) + ' - ' + song['artists'].translate(str.maketrans('', '', string.punctuation)) + '.mp3'
        filepath = os.path.join(playlist_folder_path, filename)
        cover = song['cover']
        try:
            V2METHOD    = self.V2catch(song['id'], headers)
            download_link     = V2METHOD['link']

            if download_link is not None:
                self.download_song_file(download_link, filepath)
                self.attach_image_to_mp3(filepath, cover)

            else:
                print('[*] No Download Link Found. Skipping...')
        except IndentationError as error_status:
            print('[*] Error Status Code : ', error_status)
    
    def download_song_file(self, download_link, filepath):
        ## DOWNLOAD
        link = self.session.get(download_link, stream=True)
        block_size = 1024  # 1 Kilobyte
        downloaded = 0
        
        ## Save
        with open(filepath, "wb") as f:
            for data in link.iter_content(block_size):
                f.write(data)
                downloaded += len(data)

    def attach_image_to_mp3(self, mp3_file_path, image_url):
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

if __name__ == "__main__":
    headers = {
        'origin': 'https://spotifydown.com',
        'referer': 'https://spotifydown.com/',
    }

    # Spotify playlist link
    spotify_playlist_link = input("Type spotify playlist link: ")

    if spotify_playlist_link:
        # Path to music folder
        music_folder = os.path.join(os.getcwd(), "music")  # Change this path to your desired music folder

        scraper = MusicScraper()
        scraper.scrape_playlist(spotify_playlist_link, music_folder, headers)
    else:
        print("[*] ERROR OCCURRED. MISSING PLAYLIST LINK!")