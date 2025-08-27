import os
import yt_dlp

# URL de ta playlist YouTube
playlist_url = "https://youtube.com/playlist?list=PLw3rdIbrQffFiziI7puVGcFMpuNhc5nVJ&si=riW6eDP0gc9vAH0C"

# Dossier de destination (dossier "music" local)
music_folder = "music"

# Options de téléchargement
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': os.path.join(music_folder, '%(title)s.%(ext)s'),
    'extractaudio': True,
    'audioformat': 'mp3',
    'noplaylist': False,
    'ignoreerrors': True,
    'quiet': False,
    'postprocessors': [
        {  
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }
    ]
}

# Téléchargement
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([playlist_url])
