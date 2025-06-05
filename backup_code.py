import os
import shutil
from datetime import datetime

def create_backup():
    """Crea un respaldo del código en el directorio backups."""
    # Crear directorio de respaldos si no existe
    if not os.path.exists('backups'):
        os.makedirs('backups')
    
    # Obtener fecha y hora actual para el nombre del directorio
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    backup_dir = os.path.join('backups', timestamp)
    
    # Crear directorio de respaldo
    os.makedirs(backup_dir)
    
    # Copiar directorio building_manager
    src = 'building_manager'
    dst = os.path.join(backup_dir, 'building_manager')
    shutil.copytree(src, dst)
    
    print(f'Respaldo creado en: {backup_dir}')

if __name__ == '__main__':
    create_backup() 