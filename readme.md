
# AINamer: Renombrador Inteligente de Archivos

## Descripción
AINamer es una herramienta de Python que utiliza inteligencia artificial para renombrar archivos de manera inteligente basándose en su contenido. Soporta una variedad de tipos de archivo, incluyendo documentos de texto, hojas de cálculo, PDFs e imágenes.

## Características
- Renombra archivos basándose en su contenido usando IA.
- Soporta múltiples tipos de archivo (txt, docx, xlsx, csv, pdf, jpg, png).
- Utiliza modelos de visión compatible cpm Ollama para analizar imágenes.
- Procesamiento en paralelo para mayor eficiencia.
- Barra de progreso visual durante el procesamiento.
- Configuración personalizable mediante archivo YAML.

## Requisitos
- Python 3.10+
- Ollama
- Dependencias de Python (ver `requirements.txt`)

## Instalación
1. Clona el repositorio:

2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Asegúrate de tener Ollama instalado y el modelo Llava disponible.

## Configuración
Crea un archivo `config.yaml` en el directorio del proyecto con el siguiente contenido:

```yaml
ai_model: "llama3:8b"
ai_vision_model: "llava-phi3:latest"
```


## Modelos recomendados
```
ai_model: "llama3:8b"
ai_vision_model: "llava-llama3:latest"
```


Ajusta el número de `max_workers` según las capacidades de tu sistema.

## Uso
Ejecuta el script desde la línea de comandos, especificando la carpeta que deseas procesar:

```
python ainamer.py /ruta/a/tu/carpeta
```

## Cómo funciona
1. El script recorre todos los archivos en la carpeta especificada.
2. Para cada archivo:
   - Lee su contenido (texto para documentos, descripción AI para imágenes).
   - Genera una descripción corta basada en el contenido.
   - Crea un nuevo nombre de archivo usando la descripción y un hash único.
   - Renombra el archivo.
3. Muestra una barra de progreso durante el proceso.

## Limitaciones
- El rendimiento puede variar dependiendo del tamaño y número de archivos.
- La calidad de los nombres generados depende de la precisión del modelo AI.

## Contribuir
Las contribuciones son bienvenidas. Por favor, abre un issue para discutir cambios mayores antes de enviar un pull request.

