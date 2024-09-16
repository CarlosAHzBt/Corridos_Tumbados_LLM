import requests
from bs4 import BeautifulSoup
import csv
import time
import unidecode
import itertools

# URL de la página de corridos tumbados (primer sitio)
base_url_letras = "https://www.letras.com/mais-acessadas/musicas/corridos/"

# Función para obtener los nombres de las canciones y los artistas desde la página de corridos tumbados
def get_song_and_artist(num_songs):
    response = requests.get(base_url_letras)
    soup = BeautifulSoup(response.content, 'html.parser')

    songs_list = soup.find('ol', class_='top-list_mus')  # Selecciona la lista de canciones
    
    songs = []
    if songs_list:
        for song in songs_list.find_all('a', href=True):
            title = song.find('b').get_text().strip()  # Título de la canción
            artist = song.find('span').get_text().strip()  # Artista
            song_url = "https://www.letras.com" + song['href']  # Enlace a la canción
            songs.append({'title': title, 'artist': artist, 'song_url': song_url})
            if len(songs) >= num_songs:
                break

    return songs

# Función para eliminar acentos y convertir el texto al formato adecuado
def clean_text(text):
    text = unidecode.unidecode(text)  # Eliminar acentos
    text = text.replace("(", "").replace(")", "")  # Eliminar paréntesis
    text = text.replace(" ", "-").replace(",", "").replace("--", "-").replace("---", "-").lower()  # Eliminar comas y guiones dobles/triples
    return text

# Nueva función para formatear correctamente los enlaces en función de las colaboraciones
def format_for_collaboration(artist, title, collaborators=None):
    artist = clean_text(artist)
    title = clean_text(title)

    if collaborators:  # Si hay colaboradores
        collab_list = collaborators.split(" y ")
        if len(collab_list) == 1:  # Un solo colaborador
            collab_text = clean_text(collab_list[0])
            return f"{artist}-and-{collab_text}-{title}-lyrics"
        else:  # Dos o más colaboradores
            collab_text = "-".join([clean_text(c.strip()) for c in collab_list[:-1]]) + "-and-" + clean_text(collab_list[-1].strip())
            return f"{artist}-{collab_text}-{title}-lyrics"
    else:  # Si no hay colaboradores
        return f"{artist}-{title}-lyrics"

# Función para generar permutaciones solo para los colaboradores
def generate_collaborator_combinations(artist, collaborators, title):
    collab_list = collaborators.split(" y ")
    permutations = list(itertools.permutations(collab_list))
    
    combinations = []
    for perm in permutations:
        if len(perm) == 2:
            combination = f"{clean_text(artist)}-and-{clean_text(perm[0].strip())}-and-{clean_text(perm[1].strip())}-{clean_text(title)}-lyrics"
        else:
            combination = f"{clean_text(artist)}-" + "-".join([clean_text(c.strip()) for c in perm[:-1]]) + f"-and-{clean_text(perm[-1].strip())}-{clean_text(title)}-lyrics"
        combinations.append(f"https://genius.com/{combination}")
    
    return combinations

# Función para limpiar y ajustar nombres de artistas y títulos para generar los enlaces
def format_for_genius(artist, title):
    if "(part." in title:  # Verificar si hay colaboración
        title, collaboration = title.split("(part.")
        collaboration = collaboration.replace(")", "").strip()
        return format_for_collaboration(artist, title.strip(), collaboration)
    else:
        return format_for_collaboration(artist, title)

# Función para buscar en Genius usando el título y artista
def search_in_genius(song_title, artist_name):
    genius_url = f"https://genius.com/{format_for_genius(artist_name, song_title)}"
    print(f"Enlace previsto para {song_title} de {artist_name}: {genius_url}")
    return genius_url

# Función para extraer la letra de una canción desde Genius
def get_lyrics_from_genius(song_url):
    response = requests.get(song_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        lyrics_div = soup.find('div', class_='Lyrics__Container-sc-1ynbvzw-1')  # Selector para la letra
        if lyrics_div:
            return lyrics_div.get_text(separator='\n').strip()
    return None

# Función para obtener el significado de la canción desde Letras.com (si existe)
def get_meaning_from_letras(song_url):
    meaning_url = song_url + "significado.html"
    print(f"Enlace de significado: {meaning_url}")
    response = requests.get(meaning_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        meaning_div = soup.find('div', class_='lyric-meaning')
        if meaning_div:
            return meaning_div.get_text(separator='\n').strip()
    return None

# Función para hacer scraping de las canciones en la página de corridos y buscar las letras y significados en Genius y Letras.com
def scrape_corridos_and_search_lyrics(num_songs):
    songs = get_song_and_artist(num_songs)
    canciones_con_letras = []
    canciones_fallidas = []  # Para almacenar las canciones con múltiples colaboradores donde falló la búsqueda

    for idx, song in enumerate(songs):
        print(f"Procesando canción {idx + 1}/{len(songs)}: {song['title']} - {song['artist']}")
        genius_url = search_in_genius(song['title'], song['artist'])  # Buscar el enlace en Genius
        letra = get_lyrics_from_genius(genius_url)  # Obtener la letra desde Genius
        significado = get_meaning_from_letras(song['song_url'])  # Obtener el significado desde Letras.com
        
        if letra:
            canciones_con_letras.append({
                'titulo': song['title'],
                'artista': song['artist'],
                'letra': letra,
                'significado': significado if significado else 'No disponible',
                'genius_url': genius_url
            })
        else:
            print(f"Letra no encontrada para: {song['title']} - {song['artist']}")
            if "(part." in song['title']:  # Si tiene colaboradores
                collaboration = song['title'].split("(part.")[1].replace(")", "").strip()
                if " y " in collaboration:  # Si tiene más de 1 colaborador
                    canciones_fallidas.append(song)

        time.sleep(1)  # Añadir un delay entre requests para no sobrecargar el servidor
    
    # Reintentar con las combinaciones de colaboradores
    for song in canciones_fallidas:
        title, collaboration = song['title'].split("(part.")
        collaboration = collaboration.replace(")", "").strip()
        genius_urls = generate_collaborator_combinations(song['artist'], collaboration, title)
        
        for genius_url in genius_urls:
            letra = get_lyrics_from_genius(genius_url)
            if letra:
                canciones_con_letras.append({
                    'titulo': song['title'],
                    'artista': song['artist'],
                    'letra': letra,
                    'significado': 'No disponible',  # No repetimos el significado, pero puedes agregarlo si lo prefieres
                    'genius_url': genius_url
                })
                print(f"Letra encontrada en segundo intento para: {song['title']} - {song['artist']}")
                break
            time.sleep(1)

    return canciones_con_letras

# Función para guardar los resultados en un archivo CSV
def guardar_canciones_csv(canciones, nombre_archivo='corridos_con_letras.csv'):
    with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as archivo:
        escritor_csv = csv.writer(archivo)
        escritor_csv.writerow(['Título', 'Artista', 'Letra', 'Significado', 'Genius URL'])  # Escribir las cabeceras
        for cancion in canciones:
            escritor_csv.writerow([cancion['titulo'], cancion['artista'], cancion['letra'], cancion['significado'], cancion['genius_url']])

# Ejemplo de uso
num_corridos = 1000  # Número de corridos a descargar
canciones_con_letras = scrape_corridos_and_search_lyrics(num_corridos)
guardar_canciones_csv(canciones_con_letras)
print(f"Se han guardado {len(canciones_con_letras)} corridos en corridos_con_letras.csv")


# Imprimir en consola todas las canciones que no se pudieron encontrar
print("Canciones no encontradas:")
for cancion in canciones_con_letras:
    if not cancion['letra']:
        print(f"{cancion['titulo']} - {cancion['artista']}")
