import os
import shutil
import subprocess
import stat
from pathlib import Path

# --- CONFIGURACIÓN ---
SOURCE_REPO = "https://github.com/JeffSackmann/tennis_slam_pointbypoint.git"
TEMP_DIR = "temp_sackmann_clone"
DATA_DIRS = {
    "matches": "data/raw/matches",
    "points": "data/raw/points"
}

# --- FUNCIÓN PARA CORREGIR EL ERROR DE WINDOWS ---
def remove_readonly(func, path, excinfo):
    """
    Función auxiliar para cambiar permisos de 'Solo Lectura' a 'Escritura'
    y reintentar el borrado. Vital para Windows.
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)

def ensure_directories():
    """Crea las carpetas de destino si no existen."""
    for path in DATA_DIRS.values():
        os.makedirs(path, exist_ok=True)
        print(f"✅ Carpeta asegurada: {path}")

def download_data():
    """Clona el repo, mueve los archivos y limpia."""
    print(f"\n⬇️  Clonando datos desde {SOURCE_REPO}...")
    
    # Si existiera una carpeta temporal vieja corrupta, intentamos borrarla primero
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR, onerror=remove_readonly)

    try:
        subprocess.run(["git", "clone", SOURCE_REPO, TEMP_DIR], check=True)
    except Exception as e:
        print(f"❌ Error clonando: {e}")
        return

    print("\n📦 Moviendo archivos...")
    source_path = Path(TEMP_DIR)
    counts = {"matches": 0, "points": 0}

    for file in source_path.glob("*.csv"):
        if "-matches" in file.name:
            target = Path(DATA_DIRS["matches"]) / file.name
            shutil.move(str(file), str(target))
            counts["matches"] += 1
        elif "-points" in file.name:
            target = Path(DATA_DIRS["points"]) / file.name
            shutil.move(str(file), str(target))
            counts["points"] += 1
    
    print(f"   ↳ {counts['matches']} archivos de partidos procesados.")
    print(f"   ↳ {counts['points']} archivos de puntos procesados.")

    # LIMPIEZA CON EL FIX DE WINDOWS
    print("🧹 Eliminando archivos temporales...")
    shutil.rmtree(TEMP_DIR, onerror=remove_readonly)
    print("✨ ¡Datos cargados correctamente!")

def main():
    print("--- INICIANDO CARGA DE DATOS DE TENIS ---")
    ensure_directories()
    
    # Comprobamos si ya hay datos para no descargar a lo tonto
    if any(os.scandir(DATA_DIRS["matches"])):
        respuesta = input("⚠️  Parece que ya hay datos en data/raw. ¿Quieres borrarlos y descargar de nuevo? (s/n): ")
        if respuesta.lower() != 's':
            print("Operación cancelada.")
            return

    download_data()

if __name__ == "__main__":
    main()