"""
Primer intento de hacer todo con AI
2024-07-13
"""
import os
from ollama import Client
import docx
import openpyxl
import csv
import PyPDF2
import hashlib
import logging
import argparse
from tqdm import tqdm
import yaml
import re
from typing import Union

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Cargar configuración
def load_config():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

config = load_config()

client = Client()


def read_docx(file_path):
    doc = docx.Document(file_path)
    return " ".join([paragraph.text for paragraph in doc.paragraphs])
def get_image_description(file_path):
    try:
        res = client.chat(
            model=config['ai_vision_model'],
            messages=[
                {
                    'role': 'user',
                    'content': '''
                        Describe esta imagen en español, 
                        Si hay una persona, describela en máximo 3 palabras.
                        No uses más de 3 palabras
                        Si la imagen tiene un texto, solo responde con el texto.
                    ''',
                    'images': [file_path]
                }
            ]
        )
        return res['message']['content']
    except Exception as e:
        logging.error(f"Error al procesar la imagen {file_path} con Ollama: {str(e)}")
        return "Error al procesar la imagen"


def read_xlsx(file_path):
    workbook = openpyxl.load_workbook(file_path, read_only=True)
    sheet = workbook.active
    return " ".join([str(cell.value) for row in sheet.iter_rows() for cell in row if cell.value])

def read_csv(file_path):
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        return " ".join([" ".join(row) for row in reader])

def read_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + " "
    return text

def read_text(file_path):
    with open(file_path, 'r', errors='ignore') as file:
        return file.read()

def get_file_content(file_path: str) -> Union[str, bytes]:
    """
    Returns the content of a file based on its extension.

    :param file_path: The path to the file.
    :return: The content of the file as a string or bytes object.
    """
    _, ext = os.path.splitext(file_path)

    readers = {
        '.jpg': get_image_description,
        '.jpeg': get_image_description,
        '.png': get_image_description,
        '.gif': get_image_description,
        '.bmp': get_image_description,
        '.txt': read_text,
        '.docx': read_docx,
        '.xlsx': read_xlsx,
        '.csv': read_csv,
        '.pdf': read_pdf,
    }

    try:
        return readers[ext](file_path)
    except KeyError as e:
        logging.error(f"Archivo no soportado: {str(e)}")
        return f"Archivo no soportado: {ext}"

def sanitize_filename(filename, max_length=255):
    invalid_chars = r'[<>:"/\\|?*\']'
    filename = re.sub(invalid_chars, '', filename)
 
    filename = filename.strip().replace(' ', '_').replace('"', '')
    
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        name = name[:max_length - len(ext) - 1]
        filename = name + ext
    
    return filename

def generate_short_description(content, max_length=30):
    prompt = f"""Genera un nombre de archivo
utiliza {max_length} como largo máximo
solo crea un nombre en español
utiliza solo los elementos clave
si es posible máximo 3 palabras
responde solo con el nombre del archivo, sin texto adicional, sin extensión
            {content[:500]}"""
    response = client.chat(model=config['ai_model'], messages=[{"role": "user", "content": prompt}])
    description = response['message']['content'].strip()
    
    if len(description) > max_length:
        description = description[:max_length]
    
    return description

def generate_unique_filename(folder_path, base_name, extension):

    base_name = sanitize_filename(base_name)

    hash_object = hashlib.md5(base_name.encode())
    short_hash = hash_object.hexdigest()[:6]
    
    new_filename = f"{base_name}_{short_hash}{extension}"
    counter = 1
    while os.path.exists(os.path.join(folder_path, new_filename)):
        new_filename = f"{base_name}_{short_hash}_{counter}{extension}"
        counter += 1
    
    return new_filename

def process_file(args):
    folder_path, filename = args
    file_path = os.path.join(folder_path, filename)
    
    if os.path.isfile(file_path):
        content = get_file_content(file_path)
        description = generate_short_description(content)
        _, extension = os.path.splitext(filename)
        new_filename = generate_unique_filename(folder_path, description, extension)
        new_file_path = os.path.join(folder_path, new_filename)
        
        try:
            os.rename(file_path, new_file_path)
            logging.info(f"Renombrado: {filename} -> {new_filename}")
            return True
        except OSError as e:
            logging.error(f"Error al renombrar {filename}: {e}")
            return False
    return False

def rename_and_sort_files(folder_path):
    files = [(folder_path, filename) for filename in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, filename))]
    
    for file_info in tqdm(files, desc="Procesando archivos"):
        process_file(file_info)

def get_image_description(file_path):
    try:
        res = client.chat(
            model=config['ai_vision_model'],
            messages=[
                {
                    'role': 'user',
                    'content': '''
Describe la imagen, utiliza máximo 3 palabras.
Si hay una persona, describela en tres palabras.
Si hay texto, indica que dice el texto.
''',
                    'images': [file_path]
                }
            ]
        )
        return res['message']['content']
    except Exception as e:
        logging.error(f"Error al procesar la imagen {file_path} con Ollama: {str(e)}")
        return "Error al procesar la imagen"

def main():
    parser = argparse.ArgumentParser(description="Renombra y ordena archivos en una carpeta.")
    parser.add_argument("folder", help="Ruta de la carpeta a procesar")
    args = parser.parse_args()

    rename_and_sort_files(args.folder)

if __name__ == "__main__":
    main()