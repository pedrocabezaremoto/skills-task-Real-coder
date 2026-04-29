import os
import shutil
import sys
from pypdf import PdfReader
import gdown

# --- CONFIGURACIÓN DE LA TAREA ---
# URL del Drive con las 10 guías (Pendiente de actualizar por el usuario si es diferente)
DRIVE_URL = "https://drive.google.com/drive/folders/1mMlk6G0-Si2DL4tV0V46zNavnsGPHodh?usp=drive_link"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_GUIA_DIR = os.path.join(BASE_DIR, "guia")
CONTEXT_FILE = os.path.join(BASE_DIR, "CONTEXTO_TOTAL.md")
TEMP_DIR = "/tmp/ingestor_task1_temp"

def setup_directories():
    print(f"[*] Preparando entorno en: {TARGET_GUIA_DIR}")
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR)
    
    # Limpiamos carpeta guia para una instalación limpia y organizada
    if os.path.exists(TARGET_GUIA_DIR):
        shutil.rmtree(TARGET_GUIA_DIR)
    os.makedirs(TARGET_GUIA_DIR)

def download_from_drive():
    print(f"[*] Descargando guías desde Google Drive...")
    try:
        gdown.download_folder(url=DRIVE_URL, output=TEMP_DIR, quiet=True)
        return True
    except Exception as e:
        print(f"[!] Error en la descarga: {e}")
        return False

def process_files():
    files_info = []
    print("[*] Procesando archivos y convirtiendo PDFs a Markdown...")
    
    # Listamos y ordenamos archivos para mantener un orden lógico (guia1, guia2...)
    all_files = sorted([f for f in os.listdir(TEMP_DIR) if os.path.isfile(os.path.join(TEMP_DIR, f))])
    
    for i, filename in enumerate(all_files, 1):
        file_path = os.path.join(TEMP_DIR, filename)
        guia_folder_name = f"guia{i}"
        guia_path = os.path.join(TARGET_GUIA_DIR, guia_folder_name)
        os.makedirs(guia_path, exist_ok=True)
        
        # Copiamos el archivo original
        dest_original = os.path.join(guia_path, filename)
        shutil.copy2(file_path, dest_original)
        
        md_content = ""
        if filename.lower().endswith(".pdf"):
            try:
                reader = PdfReader(file_path)
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                md_filename = os.path.splitext(filename)[0] + ".md"
                md_path = os.path.join(guia_path, md_filename)
                
                md_header = f"# Guía {i}: {filename}\n\n"
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(md_header + text)
                
                # Resumen para el CONTEXTO_TOTAL
                preview = text[:200].replace("\n", " ") + "..."
                files_info.append({"id": i, "name": filename, "preview": preview, "folder": guia_folder_name})
                print(f"[+] {guia_folder_name}: {filename} (PDF convertido)")
            except Exception as e:
                print(f"[!] Error procesando PDF {filename}: {e}")
        else:
            files_info.append({"id": i, "name": filename, "preview": "Archivo no PDF", "folder": guia_folder_name})
            print(f"[+] {guia_folder_name}: {filename} (Copiado)")
            
    return files_info

def generate_context_file(files_info):
    print(f"[*] Generando archivo de contexto maestro: {CONTEXT_FILE}")
    with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
        f.write("# 📑 CONTEXTO TOTAL DE LA TAREA\n\n")
        f.write("Este archivo ha sido generado automáticamente para poner en contexto a cualquier agente que trabaje en esta tarea.\n\n")
        f.write("## 🗂️ Estructura de Guías Disponibles\n\n")
        f.write("| ID | Carpeta | Nombre del Archivo | Resumen/Contenido |\n")
        f.write("|----|---------|--------------------|-------------------|\n")
        for info in files_info:
            f.write(f"| {info['id']} | `{info['folder']}` | {info['name']} | {info['preview']} |\n")
        
        f.write("\n---\n")
        f.write("### 🚀 Instrucciones para el Agente\n")
        f.write("1. Lee este archivo primero para entender cuántas guías hay disponibles.\n")
        f.write("2. Cada carpeta `guiaX` contiene el archivo original y una versión `.md` fácil de leer.\n")
        f.write("3. Prioriza el uso de los archivos `.md` para mayor precisión en el análisis.\n")

def main():
    print("=== REAL CODER INGESTOR: TASK 1 ===")
    setup_directories()
    if download_from_drive():
        files_info = process_files()
        generate_context_file(files_info)
        shutil.rmtree(TEMP_DIR)
        print("\n[✔] Tarea 1 preparada profesionalmente.")
        print(f"[✔] Carpetas creadas: {len(files_info)}")
        print(f"[✔] Archivo de contexto listo en: {CONTEXT_FILE}")
    else:
        print("[!] El proceso falló. Verifica el link de Drive.")

if __name__ == "__main__":
    main()
