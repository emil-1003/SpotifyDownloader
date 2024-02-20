import os
import re
import requests
import string
import eyed3
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import time

class MusicScraper:
    def __init__(self):
        self.session = requests.Session()
    
    def scrape_playlist(self, spotify_playlist_link, music_folder):
        # Pattern used to extract id from the URL
        pattern = r"https://open\.spotify\.com/playlist/([a-zA-Z0-9]+)\?si=.*"
        match = re.match(pattern, spotify_playlist_link)

        if not match:
            raise ValueError("Invalid Spotify playlist URL.")

        playlist_id = match.group(1)
        
        headers = {
            'origin': 'https://spotifydown.com',
            'referer': 'https://spotifydown.com/',
        }
        
        playlist_url = f'https://api.spotifydown.com/metadata/playlist/{playlist_id}'
        playlist_name = self.get_playlist_name(playlist_url, headers)
        playlist_folder_path = self.create_folder_path(playlist_name, music_folder)
        
        tracklist_url = f'https://api.spotifydown.com/trackList/playlist/{playlist_id}'
        offset_data = {}
        offset = 0
        offset_data['offset'] = offset
        
        while offset is not None:
            response = self.session.get(url=tracklist_url, params=offset_data, headers=headers)
            track_list = response.json()['trackList']
            page = response.json()['nextOffset']

            print("*" * 100)
            for count, song in enumerate(track_list):
                print(count, song['title'])

            if page is not None:
                offset_data['offset'] = page
                response = self.session.get(url=playlist_url, params=offset_data, headers=headers)
            else:
                print("*" * 100)
                print('[*] Download Complete!')
                print("*" * 100)

    def get_playlist_name(self, url, headers):
        meta_data = self.session.get(url=url, headers=headers)
        playlist_name = meta_data.json()['title'] + ' - ' + meta_data.json()['artists']
        print('Playlist Name:', playlist_name)
        return playlist_name
        
    def create_folder_path(self, playlist_name, music_folder):
        folder_path = ''.join(e for e in playlist_name if e.isalnum() or e in [' ', '_'])
        playlist_folder_path = os.path.join(music_folder, folder_path)

        if not os.path.exists(playlist_folder_path):
            os.makedirs(playlist_folder_path)
        return playlist_folder_path

    def download_song(self, song, playlist_folder_path, headers, max_retries=10, retry_delay=1):
        song_id = song['id']

        for retry_count in range(max_retries):
            download_link, iamge_url = self.get_download_link(song_id, headers)

            if download_link:
                filename = self.build_filename(song)
                filepath = os.path.join(playlist_folder_path, filename)

                self.download_song_file(download_link, filepath)

                # Check if mp3 success else run from line 69 again

                song['file'] = filepath

                # Check if song was downloaded successfully
                if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
                    print(f"Song {filename} downloaded successfully.")
                    song['file'] = filepath
                    break
                else:
                    print(f"Failed to download {filename}. Retrying... ({retry_count + 1}/{max_retries})")
                    time.sleep(retry_delay)
        else:
            print(f"Max retries reached. Could not download {filename}.")

        self.attach_img_to_mp3(iamge_url, filepath)

    def get_download_link(self, song_id, headers):
        url = f'https://api.spotifydown.com/download/{song_id}'
        response = self.session.get(url=url, headers=headers)

        image_url = response.json().get('metadata').get('cover')
        
        return response.json().get('link'), image_url

    def build_filename(self, song):
        title = song['title'].translate(str.maketrans('', '', string.punctuation))
        artists = song['artists'].translate(str.maketrans('', '', string.punctuation))
        return f"{title} - {artists}.mp3"

    def download_song_file(self, download_link, filepath):
        link = self.session.get(download_link, stream=True)
        block_size = 1024  # 1 Kilobyte
        downloaded = 0

        with open(filepath, "wb") as f:
            for data in link.iter_content(block_size):
                f.write(data)
                downloaded += len(data)

    def attach_img_to_mp3(self, image_url, mp3_file_path):
        # Open the MP3 file
        audiofile = eyed3.load(mp3_file_path)
        if audiofile is None:
            print(f"Failed to load MP3 file: {mp3_file_path}")
            return False
        
        response = requests.get(image_url)
        # Attach the downloaded image to the MP3 file
        audiofile.tag.images.set(3, response.content, 'image/jpeg', u"Description")

        # Save the changes
        audiofile.tag.save()

if __name__ == "__main__":
    # Spotify playlist link
    spotify_playlist_link = input("Spotify Playlist Link: ")

    if spotify_playlist_link:
        # Path to music folder
        music_folder = os.path.join(os.getcwd(), "music")  # Change this path to your desired music folder

        scraper = MusicScraper()
        scraper.scrape_playlist(spotify_playlist_link, music_folder)
    else:
        print("[*] ERROR OCCURRED. MISSING PLAYLIST LINK!")