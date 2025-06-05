import os
import shutil
from datetime import datetime

def list_backups():
    """Lista todos los respaldos disponibles."""
    if not os.path.exists('backups'):
        print('No hay respaldos disponibles.')
        return []
    
    backups = []
    for d in os.listdir('backups'):
        backup_path = os.path.join('backups', d)
        if os.path.isdir(backup_path):
            backups.append(d)
    
    if not backups:
        print('No hay respaldos disponibles.')
    else:
        print('\nRespaldos disponibles:')
        for i, backup in enumerate(backups, 1):
            print(f'{i}. {backup}')
    
    return backups

def restore_backup(backup_name):
    """Restaura un respaldo específico."""
    src = os.path.join('backups', backup_name, 'building_manager')
    dst = 'building_manager'
    
    if not os.path.exists(src):
        print(f'El respaldo {backup_name} no existe.')
        return False
    
    # Crear respaldo del código actual antes de restaurar
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    current_backup = os.path.join('backups', f'pre_restore_{timestamp}')
    if os.path.exists(dst):
        shutil.copytree(dst, os.path.join(current_backup, 'building_manager'))
        print(f'Respaldo del código actual creado en: {current_backup}')
        shutil.rmtree(dst)
    
    # Restaurar el respaldo seleccionado
    shutil.copytree(src, dst)
    print(f'Respaldo {backup_name} restaurado correctamente.')
    return True

if __name__ == '__main__':
    backups = list_backups()
    if backups:
        try:
            choice = int(input('\nSeleccione el número del respaldo a restaurar (0 para cancelar): '))
            if 0 < choice <= len(backups):
                restore_backup(backups[choice - 1])
            elif choice == 0:
                print('Operación cancelada.')
            else:
                print('Opción inválida.')
        except ValueError:
            print('Por favor, ingrese un número válido.') 