import os
import re
import requests
import string

# Hvis dette ikke virker skift requests ud med session:
# session = requests.Session()

def get_playlist_name(url, headers):    
    # Get request for at få playlist name and author
    meta_data = requests.get(headers=headers, url=url)
    playlist_name = ""
    if meta_data.status_code == 200:
        playlist_name = meta_data.json()['title'] + ' - ' + meta_data.json()['artists']
        print('Playlist Name : ', playlist_name)
    return playlist_name

if __name__ == "__main__":
    # Link til spotify playliste
    spotify_playlist_link = "https://open.spotify.com/playlist/5BoEOUaW7r7eLIoL2ZvcYc?si=a81559963e0d44c5"
    
    # Path til musik folder
    music_folder = os.path.join(os.getcwd(), "music")
    
    # Pattern som bruges til at hente id fra url
    pattern = r"https://open\.spotify\.com/playlist/([a-zA-Z0-9]+)\?si=.*"

    # Check om id er i url
    match = re.match(pattern, spotify_playlist_link)

    # Smid fejl hvis der ikke er id
    if not match:
        raise ValueError("Invalid Spotify playlist URL.")
    
    # Gem id
    id = match.group(1)
    
    url = f'https://api.spotifydown.com/metadata/playlist/{id}'
    headers = {
        'origin': 'https://spotifydown.com',
        'referer': 'https://spotifydown.com/',
    }
    playlist_name = get_playlist_name(url, headers)
    
    folder_path = ''.join(e for e in playlist_name if e.isalnum() or e in [' ', '_'])
    
    # Get path to playlist folder
    playlist_folder_path = os.path.join(music_folder, folder_path)

    # Create dirs if not exists
    if not os.path.exists(playlist_folder_path):
        os.makedirs(playlist_folder_path)
        
    playlist_url = f'https://api.spotifydown.com/trackList/playlist/{id}'
    
    offset_data = {}
    offset = 0
    offset_data['offset'] = offset
    
    response = requests.get(url=playlist_url, params=offset_data, headers=headers)
    t_data = response.json()['trackList']
    page = response.json()['nextOffset']

    print("*"*100)
    for count, song in enumerate(t_data):
        print("[*] Downloading : ", song['title'], "-", song['artists'])
        # Build mp3 filename
        filename = song['title'].translate(str.maketrans('', '', string.punctuation)) + ' - ' + song['artists'].translate(str.maketrans('', '', string.punctuation)) + '.mp3'
        
        # Path to the mp3 file
        filepath = os.path.join(playlist_folder_path, filename)
        
        try:
            # Get id of song
            song_id = song['id']
            print(song_id)
            
            # Url to download song
            url = f'https://api.spotifydown.com/download/{song_id}'
            
            response = requests.get(url=url, headers=headers)
            
            # TODO:
            v2catchVar = {
                'link' : response.json()['link'],
                'metadata' : None
            }
            
            v2_method = v2catchVar
            dl_link = v2_method['link']
            song_meta = song
            song_meta['file'] = filepath
            
            if dl_link is not None:
                ## DOWNLOAD
                link = requests.get(dl_link, stream=True)
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
        response = requests.get(url=playlist_url, params=offset_data, headers=headers)
    else:
        print("*"*100)
        print('[*] Download Complete!')
        print("*"*100)