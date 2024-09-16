import json
import pandas as pd

# Cargar el archivo CSV
file_path = 'corridos_con_letras.csv'  # Ruta de tu archivo CSV
corridos_data = pd.read_csv(file_path)

# Filtrar las filas con valores nulos o vacíos en 'Significado' o 'Letra'
removed_songs = corridos_data[corridos_data['Significado'].isna() | corridos_data['Letra'].isna()]

# Imprimir las canciones que fueron eliminadas
if not removed_songs.empty:
    print("Canciones eliminadas por falta de 'Significado' o 'Letra':")
    for index, row in removed_songs.iterrows():
        print(f"- {row['Título']}")
else:
    print("No se eliminaron canciones.")

# Eliminar filas con valores nulos o vacíos en las columnas 'Significado' o 'Letra'
corridos_data = corridos_data.dropna(subset=['Significado', 'Letra'])

# Crear una lista para almacenar el formato de JSON
dataset = []

# Recorrer cada fila del CSV para crear el formato JSON
for index, row in corridos_data.iterrows():
    prompt = row['Significado']
    completion = row['Letra']
    
    # Formato esperado para el fine-tuning
    entry = {
        "prompt": prompt,
        "completion": completion
    }
    
    dataset.append(entry)

# Guardar el archivo JSON
output_file = 'corridos_dataset.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(dataset, f, ensure_ascii=False, indent=4)

print(f"Archivo JSON guardado en: {output_file}")

# Total de canciones con letras y significado
print(f"Total de canciones con letras y significado: {len(dataset)}")
