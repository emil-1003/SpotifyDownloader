import os
import re
import requests
import string
import eyed3
from io import BytesIO
import time
import threading

class MusicScraper():
    def __init__(self):
        self.session = requests.Session()

    def scrape_playlist(self, spotify_playlist_link, music_folder):   
        headers = {
            'origin': 'https://spotifydown.com',
            'referer': 'https://spotifydown.com/',
        }
        
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
                # for count, song in enumerate(track_list):
                #     print("[*] Downloading : ", song['title'], "-", song['artists'])
                #     self.download_song(song, playlist_folder_path)
                    
                threads = []
                for song in track_list:
                    print("[*] Downloading : ", song['title'], "-", song['artists'])
                    thread = threading.Thread(target=self.download_song, args=(song, playlist_folder_path))
                    threads.append(thread)
                    thread.start()

                # Wait for all threads to finish
                for thread in threads:
                    thread.join()
                    
            if page is not None:
                offset_data['offset'] = page
                # TODO: ved ikke helt hvorfor den er her:
                response = self.session.get(url=tracklist_url, params=offset_data, headers=headers)
            else:
                print("*"*100)
                print('[*] Download Complete!')
                print("*"*100)
                break

    def get_ID(self, yt_id):
        # The 'get_ID' function from your scraper code
        LINK = f'https://api.spotifydown.com/getId/{yt_id}'
        headers = {
            'authority': 'api.spotifydown.com',
            'method': 'GET',
            'path': f'/getId/{id}',
            'origin': 'https://spotifydown.com',
            'referer': 'https://spotifydown.com/',
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-fetch-mode': 'cors',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }
        response = self.session.get(url=LINK, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data['id']
        return None

    def generate_Analyze_id(self, yt_id):
        # The 'generate_Analyze_id' function from your scraper code
        DL = 'https://corsproxy.io/?https://www.y2mate.com/mates/analyzeV2/ajax'
        data = {
            'k_query': f'https://www.youtube.com/watch?v={yt_id}',
            'k_page': 'home',
            'hl': 'en',
            'q_auto': 0,
        }
        headers = {
            'authority': 'corsproxy.io',
            'method': 'POST',
            'path': '/?https://www.y2mate.com/mates/analyzeV2/ajax',
            'origin': 'https://spotifydown.com',
            'referer': 'https://spotifydown.com/',
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-fetch-mode': 'cors',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }
        RES = self.session.post(url=DL, data=data, headers=headers)
        if RES.status_code == 200:
            return RES.json()
        return None

    def generate_Conversion_id(self, analyze_yt_id, analyze_id):
        # The 'generate_Conversion_id' function from your scraper code
        DL = 'https://corsproxy.io/?https://www.y2mate.com/mates/convertV2/index'
        data = {
            'vid'   : analyze_yt_id,
            'k'     : analyze_id,
        }
        headers = {
            'authority': 'corsproxy.io',
            'method': 'POST',
            'path': '/?https://www.y2mate.com/mates/analyzeV2/ajax',
            'origin': 'https://spotifydown.com',
            'referer': 'https://spotifydown.com/',
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-fetch-mode': 'cors',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }
        RES = self.session.post(url=DL, data=data, headers=headers)
        if RES.status_code == 200:
            return RES.json()
        return None

    def get_playlist_name(self, Playlist_ID, headers):
        URL = f'https://api.spotifydown.com/metadata/playlist/{Playlist_ID}'
        meta_data = self.session.get(headers=headers, url=URL)
        playlist_name = meta_data.json()['title'] + ' - ' + meta_data.json()['artists']
        print('Playlist Name : ', playlist_name)
        return playlist_name

    def errorcatch(self, SONG_ID):
        # The 'errorcatch' function from your scraper code
        print('[*] Trying to download...')
        headers = {
            'authority': 'api.spotifydown.com',
            'method': 'GET',
            'path': f'/download/{SONG_ID}',
            'scheme': 'https',
            'origin': 'https://spotifydown.com',
            'referer': 'https://spotifydown.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        }
        x = self.session.get(headers=headers, url='https://api.spotifydown.com/download/' + SONG_ID)
        if x.status_code == 200:
            return x.json()['link']
        return None

    def V2catch(self, SONG_ID):
        headers = {
            "authority": "api.spotifydown.com",
            "method": "POST",
            "path": '/download/68GdZAAowWDac3SkdNWOwo',
            "scheme": "https",
            "Accept": "*/*",

            'Sec-Ch-Ua':'"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
            "Dnt": '1',
            "Origin": "https://spotifydown.com",
            "Referer": "https://spotifydown.com/",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
        }

        x = self.session.get(url = f'https://api.spotifydown.com/download/{SONG_ID}', headers=headers)

        if x.status_code == 200:

            try:
                return {
                    'link' : x.json()['link'],
                    'metadata' : None
                }
            except:
                return {
                    'link' : None,
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

    def download_song(self, song, playlist_folder_path):
        filename = song['title'].translate(str.maketrans('', '', string.punctuation)) + ' - ' + song['artists'].translate(str.maketrans('', '', string.punctuation)) + '.mp3'
        filepath = os.path.join(playlist_folder_path, filename)
        try:
            ########### Måske gør dette så alle sange bliver downloaded ###########
            try:
                V2METHOD    = self.V2catch(song['id'])
                download_link     = V2METHOD['link']
                SONG_META   = song
                SONG_META['file'] = filepath

            except IndentationError:
                print("okay")
                yt_id = self.get_ID(song['id'])

                if yt_id is not None:
                    data = self.generate_Analyze_id(yt_id['id'])
                    try:
                        DL_ID = data['links']['mp3']['mp3128']['k']
                        DL_DATA = self.generate_Conversion_id(data['vid'], DL_ID)
                        download_link = DL_DATA['dlink']
                    except Exception as NoLinkError:
                        CatchMe = self.errorcatch(song['id'])
                        if CatchMe is not None:
                            download_link = CatchMe
                else:
                    print('[*] No data found for : ', song)
            ######################################################################

            if download_link is not None:
                self.download_song_file(download_link, filepath)

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

if __name__ == "__main__":
    # Spotify playlist link
    spotify_playlist_link = "https://open.spotify.com/playlist/6jaDySLGoGfQVIz8J8vR8b?si=a20986c81831462b"

    if spotify_playlist_link:
        # Path to music folder
        music_folder = os.path.join(os.getcwd(), "music")  # Change this path to your desired music folder

        scraper = MusicScraper()
        scraper.scrape_playlist(spotify_playlist_link, music_folder)
    else:
        print("[*] ERROR OCCURRED. MISSING PLAYLIST LINK!")