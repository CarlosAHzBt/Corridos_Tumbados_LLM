# Corridos Tumbados LLM

## Descripción del Proyecto

Este proyecto realiza el **fine-tuning** del modelo **Llama 3.1** (8B parámetros) para generar letras de corridos tumbados. El modelo recibe como input el significado de la canción y genera como output la letra completa basada en dicho significado.

El proceso incluye **web scraping** de sitios de letras de canciones para recolectar tanto la letra como el significado de los corridos tumbados. Después, los datos son procesados y utilizados para entrenar el modelo, empleando la librería **UNsLOTH**.

## Estructura del Proyecto

- **ScrapCorridosGenius.py**: Script que realiza scraping en sitios de letras de canciones (*letras.com* y *Genius*) para obtener el título, el artista, la letra y el significado de corridos tumbados. Estos datos se almacenan en un archivo CSV.
- **DataProcesses.py**: Procesa el archivo CSV generado durante el scraping para eliminar entradas con datos incompletos y convertir la información en un archivo JSON que se utilizará en el fine-tuning del modelo.
- **EntrenamientoDelModelo.ipynb**: Notebook donde se lleva a cabo el proceso de fine-tuning utilizando UNsLOTH para ajustar Llama 3.1 a las letras de corridos tumbados.
- **adapter_config.json**: Configuración de adaptadores LoRA utilizados durante el fine-tuning.
- **corridos_con_letras.csv**: Dataset con las letras de las canciones y sus significados, extraídos durante el proceso de scraping.
- **corridos_dataset.json**: Versión procesada del dataset, lista para ser utilizada en el fine-tuning.
- **requirements.txt**: Dependencias necesarias para correr los scripts del proyecto.

## Instalación

### Clona el repositorio:

```bash
git clone https://github.com/usuario/Corridos_Tumbados_LLM.git
cd Corridos_Tumbados_LLM
```

### Instala las dependencias:

```bash
pip install -r requirements.txt
```

### Web Scraping
Para recolectar las letras y significados de los corridos tumbados, ejecuta el script ScrapCorridosGenius.py:

```bash
python ScrapCorridosGenius.py
```


Este script realizará el scraping en páginas de letras de canciones, como letras.com y Genius, para obtener tanto las letras como los significados de las canciones y guardarlos en un archivo CSV (corridos_con_letras.csv).

### Procesamiento de Datos
Después de realizar el scraping, utiliza el script DataProcesses.py para procesar los datos y prepararlos para el fine-tuning del modelo:

```bash
python DataProcesses.py
```

Este script eliminará las entradas incompletas y creará un archivo JSON (`corridos_dataset.json`) con el formato necesario para el entrenamiento.

## Fine-Tuning del Modelo

El fine-tuning se realiza en el archivo `EntrenamientoDelModelo.ipynb`, donde se emplea UNsLOTH para ajustar Llama 3.1 a los datos de corridos tumbados.

1. Abre el notebook `EntrenamientoDelModelo.ipynb`.
2. Asegúrate de seguir los pasos para la instalación de UNsLOTH.
3. Ejecuta las celdas del notebook para entrenar el modelo.

## Inferencia con el Modelo Fine-Tuneado

Para hacer inferencias utilizando el modelo entrenado, puedes cargar el modelo desde un archivo guardado. El siguiente ejemplo muestra cómo realizar inferencias:

### Cargar el Modelo Fine-Tuneado

Si ya tienes el modelo entrenado y guardado, puedes cargarlo de la siguiente manera:
Puedes descargar el modelo completo que yo entrene desde este enlace : https://drive.google.com/file/d/1ZdQjVX-U2OwAPPa1WNDryeHuivDCoQ3K/view?usp=sharing
```bash
from transformers import AutoTokenizer
from unsloth import FastLanguageModel

# Cargar el modelo y el tokenizador
model = FastLanguageModel.from_pretrained("ruta_a_tu_modelo", load_in_4bit=True)
tokenizer = AutoTokenizer.from_pretrained("ruta_a_tu_modelo")

# Asegúrate de que el modelo esté en modo de inferencia
FastLanguageModel.for_inference(model)

```

#### Realizar una Inferencia
Una vez cargado el modelo, puedes generar una letra a partir del significado de una canción:

```bash
# Formato del prompt
prompt = """El siguiente texto describe el significado de una canción. Genera la letra del corrido tumbado según el significado.

Significado:
{}

Letra:
"""

# Definir el significado
significado = """
Este corrido habla sobre la vida difícil de un joven que decide tomar el camino del narcotráfico para ayudar a su familia.
"""

# Formatear el prompt
input_text = prompt.format(significado)

# Tokenizar el input
inputs = tokenizer([input_text], return_tensors="pt").to("cuda")

# Generar la letra de la canción
output = model.generate(**inputs, max_new_tokens=512)
letra_generada = tokenizer.decode(output[0], skip_special_tokens=True)

print("Letra generada:")
print(letra_generada)


```


#### Guardar el Modelo Fine-Tuneado
Después de entrenar el modelo, puedes guardarlo usando LoRA adapters o fusionando todos los pesos del modelo:
```bash
# Guardar solo los adaptadores LoRA
model.save_pretrained("lora_model")

# O guardar el modelo completo fusionando los adaptadores
model.save_pretrained_merged("complete_model", save_method="merged_16bit")

```
Para más detalles sobre el uso de UNsLOTH y el proceso de entrenamiento, consulta el archivo EntrenamientoDelModelo.ipynb.


## Créditos
CarlosAHZBt - Desarrollador principal del proyecto
Herramientas: UNsLOTH, Hugging Face Transformers
