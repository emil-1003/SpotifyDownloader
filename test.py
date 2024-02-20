import os
import re
import requests
import string

def get_playlist_name(url, headers):
    meta_data = requests.get(headers=headers, url=url)
    playlist_name = ""
    if meta_data.status_code == 200:
        playlist_name = meta_data.json()['title'] + ' - ' + meta_data.json()['artists']
        print('Playlist Name : ', playlist_name)
    return playlist_name

def create_folder_path(playlist_name, music_folder):
    folder_path = ''.join(e for e in playlist_name if e.isalnum() or e in [' ', '_'])
    playlist_folder_path = os.path.join(music_folder, folder_path)
    
    if not os.path.exists(playlist_folder_path):
        os.makedirs(playlist_folder_path)
    return playlist_folder_path

def download_song(song, playlist_folder_path, headers):
    try:
        song_id = song['id']
        download_link = get_download_link(song_id, headers)
        
        if download_link is not None:
            filename = build_filename(song)
            filepath = os.path.join(playlist_folder_path, filename)
            
            download_song_file(download_link, filepath)
            
            song['file'] = filepath
        else:
            print('[*] No Download Link Found. Skipping...')
    except IndentationError as error_status:
        print('[*] Error Status Code : ', error_status)

def get_download_link(song_id, headers):
    url = f'https://api.spotifydown.com/download/{song_id}'
    response = requests.get(url=url, headers=headers)
    return response.json().get('link')

def build_filename(song):
    title = song['title'].translate(str.maketrans('', '', string.punctuation))
    artists = song['artists'].translate(str.maketrans('', '', string.punctuation))
    return f"{title} - {artists}.mp3"

def download_song_file(download_link, filepath):
    link = requests.get(download_link, stream=True)
    total_size = int(link.headers.get('content-length', 0))
    block_size = 1024  # 1 Kilobyte
    downloaded = 0

    with open(filepath, "wb") as f:
        for data in link.iter_content(block_size):
            f.write(data)
            downloaded += len(data)

if __name__ == "__main__":
    # Link til spotify playliste
    spotify_playlist_link = input("Spotify Playlist Link: ")
    
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
    
    headers = {
        'origin': 'https://spotifydown.com',
        'referer': 'https://spotifydown.com/',
    }
    
    url = f'https://api.spotifydown.com/metadata/playlist/{id}'
    playlist_name = get_playlist_name(url, headers)
    playlist_folder_path = create_folder_path(playlist_name, music_folder)
    
    playlist_url = f'https://api.spotifydown.com/trackList/playlist/{id}'
    offset_data = {'offset': 0}
    
    response = requests.get(url=playlist_url, params=offset_data, headers=headers)
    t_data = response.json()['trackList']
    page = response.json()['nextOffset']
    
    print("*" * 100)
    for count, song in enumerate(t_data):
        print("[*] Downloading : ", song['title'], "-", song['artists'])
        download_song(song, playlist_folder_path, headers)
    
    if page is not None:
        offset_data['offset'] = page
        response = requests.get(url=playlist_url, params=offset_data, headers=headers)
    else:
        print("*"*100)
        print('[*] Download Complete!')
        print("*"*100)