import os
import string

import requests
import re
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC

class MusicScraper():
    def __init__(self):
        super(MusicScraper, self).__init__()
        self.counter = 0
        self.session = requests.Session()

    def scrape_playlist(self, spotify_playlist_link, music_folder):
            id = self.return_spot_id(spotify_playlist_link)
            playlist_name = self.get_playlist_metadata(id)
            print('Playlist Name : ', playlist_name)
            
            # Create Folder for Playlist
            if not os.path.exists(music_folder):
                os.makedirs(music_folder)
            try:
                folder_path = ''.join(e for e in playlist_name if e.isalnum() or e in [' ', '_'])
                playlist_folder_path = os.path.join(music_folder, folder_path)
            except:
                playlist_folder_path = music_folder

            if not os.path.exists(playlist_folder_path):
                os.makedirs(playlist_folder_path)

            headers = {
                'authority': 'api.spotifydown.com',
                'method': 'GET',
                'path': f'/trackList/playlist/{id}',
                'scheme': 'https',
                'accept': '*/*',
                'dnt': '1',
                'origin': 'https://spotifydown.com',
                'referer': 'https://spotifydown.com/',
                'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            }

            playlist_url = f'https://api.spotifydown.com/trackList/playlist/{id}'
            offset_data = {}
            offset = 0
            offset_data['offset'] = offset

            while offset is not None:
                response = self.session.get(url=playlist_url, params=offset_data, headers=headers)
                if response.status_code == 200:
                    t_data = response.json()['trackList']
                    page = response.json()['nextOffset']
                    print("*"*100)
                    for count, song in enumerate(t_data):
                        print("[*] Downloading : ", song['title'], "-", song['artists'])
                        filename = song['title'].translate(str.maketrans('', '', string.punctuation)) + ' - ' + song['artists'].translate(str.maketrans('', '', string.punctuation)) + '.mp3'
                        filepath = os.path.join(playlist_folder_path, filename)
                        try:
                            try:
                                v2_method    = self.v2catch(song['id'])
                                dl_link     = v2_method['link']
                                song_meta   = song
                                song_meta['file'] = filepath

                            except IndentationError:
                                yt_id = self.get_id(song['id'])

                                if yt_id is not None:
                                    data = self.generate_analyze_id(yt_id['id'])
                                    try:
                                        dl_id = data['links']['mp3']['mp3128']['k']
                                        dl_data = self.generate_conversion_id(data['vid'], dl_id)
                                        dl_link = dl_data['dlink']
                                    except Exception as NoLinkError:
                                        CatchMe = self.error_catch(song['id'])
                                        if CatchMe is not None:
                                            dl_link = CatchMe
                                else:
                                    print('[*] No data found for : ', song)

                            download_complete = False
                            if dl_link is not None:
                                ## DOWNLOAD
                                link = self.session.get(dl_link, stream=True)
                                total_size = int(link.headers.get('content-length', 0))
                                block_size = 1024  # 1 Kilobyte
                                downloaded = 0
                                ## Save
                                with open(filepath, "wb") as f:
                                    for data in link.iter_content(block_size):
                                        f.write(data)
                                        downloaded += len(data)
                                download_complete = True
                                #Increment the counter
                                self.increment_counter()

                            else:
                                print('[*] No Download Link Found. Skipping...')
                            if (dl_link is not None)&(download_complete == True):
                                # songTag = WritingMetaTags(tags=song_meta, filename=filepath)
                                # song_meta_add = songTag.WritingMetaTags()
                                print("hej")
                        except IndentationError as error_status:
                            print('[*] Error Status Code : ', error_status)

                if page is not None:
                    offset_data['offset'] = page
                    response = self.session.get(url=playlist_url, params=offset_data, headers=headers)
                else:
                    print("*"*100)
                    print('[*] Download Complete!')
                    print("*"*100)
                    break

    def return_spot_id(self, link):
        # Define the regular expression pattern for the Spotify playlist URL
        pattern = r"https://open\.spotify\.com/playlist/([a-zA-Z0-9]+)\?si=.*"

        # Try to match the pattern in the input text
        match = re.match(pattern, link)

        if not match:
            raise ValueError("Invalid Spotify playlist URL.")
        # Extract the playlist ID from the matched pattern
        extracted_id = match.group(1)

        return extracted_id

    def get_playlist_metadata(self, playlist_id):
        url = f'https://api.spotifydown.com/metadata/playlist/{playlist_id}'
        headers = {
            'authority': 'api.spotifydown.com',
            'method': 'GET',
            'path': f'/metadata/playlist/{playlist_id}',
            'scheme': 'https',
            'origin': 'https://spotifydown.com',
            'referer': 'https://spotifydown.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        }
        meta_data = self.session.get(headers=headers, url=url)
        if meta_data.status_code == 200:
            return meta_data.json()['title'] + ' - ' + meta_data.json()['artists']
        return None

    def v2catch(self, song_id):
        url = f'https://api.spotifydown.com/download/{song_id}'
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

        x = self.session.get(url=url, headers=headers)

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

    def get_id(self, yt_id):
        url = f'https://api.spotifydown.com/getId/{yt_id}'
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
        response = self.session.get(url=url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data['id']
        return None

    def generate_analyze_id(self, yt_id):
        url = 'https://corsproxy.io/?https://www.y2mate.com/mates/analyzeV2/ajax'
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
        response = self.session.post(url=url, data=data, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None

    def generate_conversion_id(self, analyze_yt_id, analyze_id):
        url = 'https://corsproxy.io/?https://www.y2mate.com/mates/convertV2/index'
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
        response = self.session.post(url=url, data=data, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None

    def error_catch(self, song_id):
        print('[*] Trying to download...')
        
        url = 'https://api.spotifydown.com/download/' + song_id
        headers = {
            'authority': 'api.spotifydown.com',
            'method': 'GET',
            'path': f'/download/{song_id}',
            'scheme': 'https',
            'origin': 'https://spotifydown.com',
            'referer': 'https://spotifydown.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        }
        x = self.session.get(headers=headers, url=url)
        if x.status_code == 200:
            return x.json()['link']
        return None

    def increment_counter(self):
            self.counter += 1

class WritingMetaTags():
    def __init__(self, tags, filename):
        super().__init__()
        self.tags = tags
        self.filename = filename
        self.picturedata = None
        self.url = None

    def set_pic(self):
        if self.tags['cover'] is None:
            pass
        else:
            try:
                response = requests.get(self.tags['cover']+"?size=1", stream=True)
                if response.status_code == 200 :
                    audio = ID3(self.filename)
                    audio['APIC'] = APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3,
                        desc=u'Cover',
                        data=response.content
                    )
                    audio.save()

            except Exception as e:
                print(f"Error adding cover: {e}")

    def WritingMetaTags(self):
        try:
            audio = EasyID3(self.filename)
            audio['title'] = self.tags['title']
            audio['artist'] = self.tags['artists']
            audio['album'] = self.tags['album']
            audio['date'] = self.tags['releaseDate']
            audio.save()
            self.set_pic()

        except Exception as e:
            print(f'Error {e}')

if __name__ == "__main__":
    spotify_playlist_link = "https://open.spotify.com/playlist/5BoEOUaW7r7eLIoL2ZvcYc?si=a81559963e0d44c5"

    if spotify_playlist_link is not None:
        music_folder = os.path.join(os.getcwd(), "music")  # Change this path to your desired music folder

        scraper = MusicScraper()
        # ID = scraper.return_spot_id(spotify_playlist_link)
        scraper.scrape_playlist(spotify_playlist_link, music_folder)
    else:
        print("[*] ERROR OCCURRED. MISSING PLAYLIST LINK !")