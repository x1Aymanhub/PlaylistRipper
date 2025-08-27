import os
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
import subprocess
import glob

# Import de la configuration sécurisée
from config import (
    SPOTIFY_CLIENT_ID, 
    SPOTIFY_CLIENT_SECRET, 
    SPOTIFY_PLAYLIST_URL, 
    MUSIC_FOLDER,
    FFMPEG_PATH
)

# Configuration Spotify API
CLIENT_ID = SPOTIFY_CLIENT_ID
CLIENT_SECRET = SPOTIFY_CLIENT_SECRET
playlist_url = SPOTIFY_PLAYLIST_URL
music_folder = MUSIC_FOLDER

# Initialisation de l'API Spotify
def init_spotify():
    try:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=CLIENT_ID, 
            client_secret=CLIENT_SECRET
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        return sp
    except Exception as e:
        print(f"Erreur lors de l'initialisation de Spotify: {e}")
        return None

# Extraction de l'ID de playlist depuis l'URL
def extract_playlist_id(url):
    pattern = r'playlist/([a-zA-Z0-9]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        print("Impossible d'extraire l'ID de playlist de l'URL")
        return None

# Récupération des informations de la playlist
def get_playlist_tracks(sp, playlist_id):
    try:
        results = sp.playlist_tracks(playlist_id)
        tracks = []
        
        for item in results['items']:
            track = item['track']
            if track:
                artist = track['artists'][0]['name']
                title = track['name']
                tracks.append(f"{artist} - {title}")
        
        return tracks
    except Exception as e:
        print(f"Erreur lors de la récupération des pistes: {e}")
        return []

# Recherche YouTube et téléchargement
def download_track(track_name, music_folder):
    # Chemin vers FFmpeg
    ffmpeg_path = r"C:\Users\PC\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1.1-full_build\bin"
    
    ydl_opts = {
        # Chemin vers FFmpeg
        'ffmpeg_location': ffmpeg_path,
        # Forcer seulement les formats audio (pas de vidéo)
        'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio[ext=mp3]/bestaudio',
        'outtmpl': os.path.join(music_folder, '%(title)s.%(ext)s'),
        'extractaudio': True,
        'audioformat': 'mp3',
        'ignoreerrors': True,
        'quiet': False,
        # Rejeter les formats vidéo
        'rejecttitle': '.*video.*',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }
        ],
        # Forcer la conversion en MP3
        'postprocessor_args': [
            '-acodec', 'libmp3lame',
            '-ab', '192k',
            '-ar', '44100'
        ]
    }
    
    # Recherche sur YouTube
    search_query = f"{track_name} audio"
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Recherche de la vidéo
            search_results = ydl.extract_info(f"ytsearch1:{search_query}", download=False)
            if search_results and 'entries' in search_results and search_results['entries']:
                # Essayer plusieurs résultats pour trouver un format audio
                for entry in search_results['entries'][:3]:  # Vérifier les 3 premiers résultats
                    video_url = entry['webpage_url']
                    title = entry.get('title', '').lower()
                    
                    # Éviter les vidéos avec des mots-clés vidéo
                    if any(word in title for word in ['official video', 'music video', 'clip', 'video']):
                        continue
                    
                    # Vérifier la durée (éviter les vidéos trop longues)
                    duration = entry.get('duration', 0)
                    if duration > 600:  # Plus de 10 minutes
                        continue
                    
                    print(f"Téléchargement de: {track_name}")
                    print(f"Format détecté: {entry.get('ext', 'unknown')}")
                    ydl.download([video_url])
                    return True
                
                print(f"Aucun format audio approprié trouvé pour: {track_name}")
                return False
            else:
                print(f"Aucun résultat trouvé pour: {track_name}")
                return False
    except Exception as e:
        print(f"Erreur lors du téléchargement de {track_name}: {e}")
        return False

# Vérification du format avant téléchargement
def check_audio_format(video_url):
    """Vérifie si la vidéo contient de l'audio et évite les formats vidéo purs"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Vérifier si c'est principalement audio
            if info.get('duration', 0) > 600:  # Plus de 10 minutes = probablement vidéo
                return False
                
            # Vérifier le titre pour éviter les vidéos
            title = info.get('title', '').lower()
            if any(word in title for word in ['video', 'clip', 'official video', 'music video']):
                return False
                
            return True
            
    except Exception as e:
        print(f"Erreur lors de la vérification du format: {e}")
        return False

# Conversion des fichiers non-MP3 en MP3
def convert_to_mp3(music_folder):
    print("Vérification et conversion des fichiers en MP3...")
    
    # Chemin vers FFmpeg
    ffmpeg_path = r"C:\Users\PC\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe"
    
    # Chercher tous les fichiers audio non-MP3
    audio_extensions = ['*.mp4', '*.webm', '*.m4a', '*.ogg', '*.wav', '*.flac']
    files_to_convert = []
    
    for ext in audio_extensions:
        files_to_convert.extend(glob.glob(os.path.join(music_folder, ext)))
    
    for audio_file in files_to_convert:
        mp3_file = os.path.splitext(audio_file)[0] + '.mp3'
        
        # Ne pas convertir si le MP3 existe déjà
        if os.path.exists(mp3_file):
            print(f"MP3 existe déjà pour: {os.path.basename(audio_file)}")
            continue
            
        try:
            print(f"Conversion de {os.path.basename(audio_file)} en MP3...")
            cmd = [
                ffmpeg_path, '-i', audio_file, 
                '-acodec', 'libmp3lame', 
                '-ab', '192k', 
                '-ar', '44100',
                '-y', mp3_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ Converti: {os.path.basename(mp3_file)}")
                # Supprimer le fichier original
                os.remove(audio_file)
                print(f"✓ Supprimé: {os.path.basename(audio_file)}")
            else:
                print(f"Erreur lors de la conversion de {audio_file}: {result.stderr}")
                
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de la conversion de {audio_file}: {e}")
        except Exception as e:
            print(f"Erreur lors de la conversion de {audio_file}: {e}")

# Fonction principale
def main():
    print("Initialisation de l'API Spotify...")
    sp = init_spotify()
    if not sp:
        print("Impossible d'initialiser l'API Spotify. Vérifiez vos CLIENT_ID et CLIENT_SECRET.")
        return
    
    print("Extraction de l'ID de playlist...")
    playlist_id = extract_playlist_id(playlist_url)
    if not playlist_id:
        print("URL de playlist invalide.")
        return
    
    print("Récupération des pistes de la playlist...")
    tracks = get_playlist_tracks(sp, playlist_id)
    
    if not tracks:
        print("Aucune piste trouvée dans la playlist.")
        return
    
    print(f"Trouvé {len(tracks)} pistes dans la playlist.")
    
    # Création du dossier music s'il n'existe pas
    if not os.path.exists(music_folder):
        os.makedirs(music_folder)
        print(f"Dossier {music_folder} créé.")
    
    # Téléchargement de chaque piste
    successful_downloads = 0
    for i, track in enumerate(tracks, 1):
        print(f"\n[{i}/{len(tracks)}] Traitement de: {track}")
        if download_track(track, music_folder):
            successful_downloads += 1
    
    print(f"\nTéléchargement terminé! {successful_downloads}/{len(tracks)} pistes téléchargées avec succès.")
    
    # Conversion des fichiers non-MP3 en MP3
    convert_to_mp3(music_folder)
    
    print("\n✅ Tous les fichiers ont été convertis en MP3!")

if __name__ == "__main__":
    main()
