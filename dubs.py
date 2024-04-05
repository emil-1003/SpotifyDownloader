import requests
import re

if __name__ == "__main__":
    # Spotify playlist link
    spotify_playlist_link = input("Type spotify playlist link: ")
    
    pattern = r"https://open\.spotify\.com/playlist/([a-zA-Z0-9]+)\?si=.*"
    match = re.match(pattern, spotify_playlist_link)

    if not match:
        raise ValueError("Invalid Spotify playlist URL.")

    playlist_id = match.group(1)
        

    headers = {
        'origin': 'https://spotifydown.com',
        'referer': 'https://spotifydown.com/',
    }
    
    tracklist_url = f'https://api.spotifydown.com/trackList/playlist/{playlist_id}'
    offset_data = {}
    offset = 0
    offset_data['offset'] = offset
    
    song_titles = []
    song_nr = 1
    
    while offset is not None:
        response = requests.get(url=tracklist_url, params=offset_data, headers=headers)
        track_list = response.json()['trackList']
        page = response.json()['nextOffset']

        for count, song in enumerate(track_list):
            if song['title'] in song_titles:
                print("Slet:", song_nr, "-", song['title'], "allerde på:", song_titles.index(song['title'])+1)
            else:
                song_titles.append(song['title'])
            song_nr += 1
        if page is not None:
            offset_data['offset'] = page
        else:
            break
    