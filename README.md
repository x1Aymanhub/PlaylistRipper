# 🎵 **PlaylistRipper** - Téléchargeur de Playlists Musicales

## 📖 Concept

Ce projet permet de **télécharger automatiquement des playlists musicales** depuis Spotify et YouTube, puis de les **convertir en MP3** pour les écouter hors ligne.

## 🎯 Comment ça marche ?

1. **Spotify** : Le script récupère la liste des chansons d'une playlist via l'API Spotify
2. **YouTube** : Il recherche chaque chanson sur YouTube et la télécharge
3. **Conversion** : Tous les fichiers sont automatiquement convertis en MP3 de bonne qualité
4. **Organisation** : Les fichiers sont rangés dans un dossier `music/`

## 🚀 Utilisation rapide

### Installation
```bash
pip install -r requirements.txt
```

### Télécharger une playlist Spotify
```bash
python dl_spotify_playlist.py
```

### Télécharger une playlist YouTube  
```bash
python dl_playlist.py
```
