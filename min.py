import os
import string

import requests
import re

if __name__ == "__main__":
    session = requests.Session()
    # counter = 0
    
    spotify_playlist_link = "https://open.spotify.com/playlist/5BoEOUaW7r7eLIoL2ZvcYc?si=a81559963e0d44c5"

    music_folder = os.path.join(os.getcwd(), "music")
    
    pattern = r"https://open\.spotify\.com/playlist/([a-zA-Z0-9]+)\?si=.*"

    match = re.match(pattern, spotify_playlist_link)

    if not match:
        raise ValueError("Invalid Spotify playlist URL.")

    id = match.group(1)
        
    url = f'https://api.spotifydown.com/metadata/playlist/{id}'
    headers = {
        'origin': 'https://spotifydown.com',
        'referer': 'https://spotifydown.com/',
    }
    meta_data = session.get(headers=headers, url=url)
    if meta_data.status_code == 200:
        playlist_name = meta_data.json()['title'] + ' - ' + meta_data.json()['artists']
        print('Playlist Name : ', playlist_name)
        

    folder_path = ''.join(e for e in playlist_name if e.isalnum() or e in [' ', '_'])
    playlist_folder_path = os.path.join(music_folder, folder_path)

    if not os.path.exists(playlist_folder_path):
        os.makedirs(playlist_folder_path)
    
    headers = {
        'origin': 'https://spotifydown.com',
        'referer': 'https://spotifydown.com/',
    }

    playlist_url = f'https://api.spotifydown.com/trackList/playlist/{id}'
    offset_data = {}
    offset = 0
    offset_data['offset'] = offset
    
    while offset is not None:
        response = session.get(url=playlist_url, params=offset_data, headers=headers)
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
                        song_id = song['id']
                        url = f'https://api.spotifydown.com/download/{song_id}'
                        headers = {
                            "Origin": "https://spotifydown.com",
                            "Referer": "https://spotifydown.com/",
                        }

                        response = session.get(url=url, headers=headers)

                        v2catchVar = {
                            'link' : response.json()['link'],
                            'metadata' : None
                        }
                        
                        v2_method    = v2catchVar
                        dl_link     = v2_method['link']
                        song_meta   = song
                        song_meta['file'] = filepath

                    except IndentationError:                        
                        url = f'https://api.spotifydown.com/getId/{yt_id}'
                        headers = {
                            'origin': 'https://spotifydown.com',
                            'referer': 'https://spotifydown.com/',
                        }
                        response = session.get(url=url, headers=headers)
                        data = response.json()
                        yt_id = data['id']

                        if yt_id is not None:
                            url = 'https://corsproxy.io/?https://www.y2mate.com/mates/analyzeV2/ajax'
                            data = {
                                'k_query': f'https://www.youtube.com/watch?v={yt_id}',
                                'k_page': 'home',
                                'hl': 'en',
                                'q_auto': 0,
                            }
                            headers = {
                                'origin': 'https://spotifydown.com',
                                'referer': 'https://spotifydown.com/',
                            }
                            response = session.post(url=url, data=data, headers=headers)
                            data = response.json()
                            
                            try:
                                analyze_yt_id = data['vid']
                                dl_id = data['links']['mp3']['mp3128']['k']
                                analyze_id = dl_id
                                url = 'https://corsproxy.io/?https://www.y2mate.com/mates/convertV2/index'
                                data = {
                                    'vid'   : analyze_yt_id,
                                    'k'     : analyze_id,
                                }
                                headers = {
                                    'origin': 'https://spotifydown.com',
                                    'referer': 'https://spotifydown.com/',
                                }
                                response = session.post(url=url, data=data, headers=headers)
                                dl_dataVar = response.json()
                                
                                dl_data = dl_dataVar
                                dl_link = dl_data['dlink']
                            except Exception as NoLinkError:
                                print('[*] Trying to download...')
    
                                url = 'https://api.spotifydown.com/download/' + song_id
                                headers = {
                                    'origin': 'https://spotifydown.com',
                                    'referer': 'https://spotifydown.com/',
                                }
                                response = session.get(headers=headers, url=url)
                                catchMeVar = response.json()['link']
                                
                                CatchMe = catchMeVar
                                if CatchMe is not None:
                                    dl_link = CatchMe
                        else:
                            print('[*] No data found for : ', song)

                    download_complete = False
                    if dl_link is not None:
                        ## DOWNLOAD
                        link = session.get(dl_link, stream=True)
                        total_size = int(link.headers.get('content-length', 0))
                        block_size = 1024  # 1 Kilobyte
                        downloaded = 0
                        ## Save
                        with open(filepath, "wb") as f:
                            for data in link.iter_content(block_size):
                                f.write(data)
                                downloaded += len(data)
                        download_complete = True
                    else:
                        print('[*] No Download Link Found. Skipping...')
                except IndentationError as error_status:
                    print('[*] Error Status Code : ', error_status)

        if page is not None:
            offset_data['offset'] = page
            response = session.get(url=playlist_url, params=offset_data, headers=headers)
        else:
            print("*"*100)
            print('[*] Download Complete!')
            print("*"*100)
            break
        