#!/usr/bin/env python3
"""
Sistema de Checkpoints para Building Manager Pro
Permite crear, listar y restaurar puntos de restauración funcionales
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class CheckpointManager:
    """Gestor de checkpoints usando Git"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.checkpoints_file = self.project_root / ".checkpoints.json"
        self._load_checkpoints()
    
    def _load_checkpoints(self):
        """Carga la lista de checkpoints desde el archivo"""
        if self.checkpoints_file.exists():
            try:
                with open(self.checkpoints_file, 'r', encoding='utf-8') as f:
                    self.checkpoints = json.load(f)
            except:
                self.checkpoints = []
        else:
            self.checkpoints = []
    
    def _save_checkpoints(self):
        """Guarda la lista de checkpoints"""
        with open(self.checkpoints_file, 'w', encoding='utf-8') as f:
            json.dump(self.checkpoints, f, ensure_ascii=False, indent=2)
    
    def _run_git_command(self, command: List[str]) -> tuple[bool, str]:
        """Ejecuta un comando git y retorna (éxito, salida)"""
        try:
            result = subprocess.run(
                ['git'] + command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            return result.returncode == 0, result.stdout.strip()
        except Exception as e:
            return False, str(e)
    
    def _get_current_branch(self) -> Optional[str]:
        """Obtiene la rama actual de git"""
        success, output = self._run_git_command(['branch', '--show-current'])
        return output if success else None
    
    def _get_current_commit(self) -> Optional[str]:
        """Obtiene el commit actual"""
        success, output = self._run_git_command(['rev-parse', 'HEAD'])
        return output if success else None
    
    def _has_uncommitted_changes(self) -> bool:
        """Verifica si hay cambios sin commitear"""
        success, output = self._run_git_command(['status', '--porcelain'])
        return bool(output.strip()) if success else False
    
    def create_checkpoint(self, name: str, description: str = "", auto_commit: bool = False) -> bool:
        """Crea un nuevo checkpoint"""
        print(f"\n[CHECKPOINT] Creando checkpoint: {name}")
        
        # Verificar que estamos en un repositorio git
        success, _ = self._run_git_command(['rev-parse', '--git-dir'])
        if not success:
            print("[ERROR] No se encontro un repositorio git. Inicializa git primero.")
            return False
        
        # Verificar cambios sin commitear
        if self._has_uncommitted_changes():
            print("[ADVERTENCIA] Hay cambios sin commitear.")
            if auto_commit:
                commit_msg = f"Checkpoint: {name}"
                print(f"[INFO] Haciendo commit automatico: {commit_msg}")
            else:
                try:
                    response = input("¿Deseas hacer commit de estos cambios antes del checkpoint? (s/n): ")
                    if response.lower() == 's':
                        commit_msg = input("Mensaje del commit: ").strip()
                        if not commit_msg:
                            commit_msg = f"Checkpoint: {name}"
                    else:
                        print("[ADVERTENCIA] Continuando sin commitear cambios...")
                        commit_msg = None
                except (EOFError, KeyboardInterrupt):
                    print("[INFO] Modo no interactivo. Haciendo commit automatico...")
                    commit_msg = f"Checkpoint: {name}"
            
            if commit_msg:
                
                success, output = self._run_git_command(['add', '.'])
                if not success:
                    print(f"[ERROR] Error al agregar archivos: {output}")
                    return False
                
                success, output = self._run_git_command(['commit', '-m', commit_msg])
                if not success:
                    print(f"[ERROR] Error al hacer commit: {output}")
                    return False
                print("[OK] Cambios commiteados")
        
        # Obtener información actual
        branch = self._get_current_branch()
        commit = self._get_current_commit()
        
        if not commit:
            print("[ERROR] No se pudo obtener el commit actual")
            return False
        
        # Crear tag para el checkpoint
        tag_name = f"checkpoint-{name.lower().replace(' ', '-')}"
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        full_tag = f"{tag_name}-{timestamp}"
        
        success, output = self._run_git_command(['tag', '-a', full_tag, '-m', f"{name}: {description}"])
        if not success:
            print(f"[ERROR] Error al crear tag: {output}")
            return False
        
        # Guardar información del checkpoint
        checkpoint_info = {
            "name": name,
            "description": description,
            "tag": full_tag,
            "branch": branch,
            "commit": commit,
            "timestamp": datetime.now().isoformat(),
            "created_by": "checkpoint_manager"
        }
        
        self.checkpoints.append(checkpoint_info)
        self._save_checkpoints()
        
        print(f"[OK] Checkpoint creado exitosamente: {full_tag}")
        print(f"   Rama: {branch}")
        print(f"   Commit: {commit[:8]}")
        return True
    
    def list_checkpoints(self):
        """Lista todos los checkpoints disponibles"""
        if not self.checkpoints:
            print("\n[INFO] No hay checkpoints guardados")
            return
        
        print("\n[LISTA] Checkpoints disponibles:")
        print("=" * 80)
        
        for i, cp in enumerate(self.checkpoints, 1):
            print(f"\n{i}. {cp['name']}")
            print(f"   Tag: {cp['tag']}")
            if cp.get('description'):
                print(f"   Descripción: {cp['description']}")
            print(f"   Fecha: {cp['timestamp']}")
            print(f"   Rama: {cp.get('branch', 'N/A')}")
            print(f"   Commit: {cp['commit'][:8]}")
    
    def restore_checkpoint(self, checkpoint_name_or_index: str) -> bool:
        """Restaura un checkpoint"""
        # Buscar checkpoint
        checkpoint = None
        
        # Intentar como índice
        try:
            index = int(checkpoint_name_or_index) - 1
            if 0 <= index < len(self.checkpoints):
                checkpoint = self.checkpoints[index]
        except ValueError:
            pass
        
        # Si no es índice, buscar por nombre o tag
        if not checkpoint:
            for cp in self.checkpoints:
                if (cp['name'].lower() == checkpoint_name_or_index.lower() or 
                    cp['tag'].lower() == checkpoint_name_or_index.lower()):
                    checkpoint = cp
                    break
        
        if not checkpoint:
            print(f"❌ Checkpoint no encontrado: {checkpoint_name_or_index}")
            return False
        
        print(f"\n🔄 Restaurando checkpoint: {checkpoint['name']}")
        print(f"   Tag: {checkpoint['tag']}")
        print(f"   Commit: {checkpoint['commit']}")
        
        # Advertencia
        if self._has_uncommitted_changes():
            print("\n⚠️  ADVERTENCIA: Tienes cambios sin commitear.")
            response = input("¿Deseas continuar? Se perderán los cambios no guardados (s/n): ")
            if response.lower() != 's':
                print("❌ Restauración cancelada")
                return False
        
        # Hacer checkout del tag
        success, output = self._run_git_command(['checkout', checkpoint['tag']])
        if not success:
            print(f"❌ Error al restaurar checkpoint: {output}")
            return False
        
        print(f"✅ Checkpoint restaurado exitosamente: {checkpoint['name']}")
        print(f"   Estás ahora en el commit: {checkpoint['commit'][:8]}")
        print(f"\n💡 Tip: Si quieres trabajar desde aquí, crea una nueva rama:")
        print(f"   git checkout -b restore-{checkpoint['name'].lower().replace(' ', '-')}")
        
        return True
    
    def delete_checkpoint(self, checkpoint_name_or_index: str) -> bool:
        """Elimina un checkpoint (solo del registro, no el tag de git)"""
        checkpoint = None
        
        try:
            index = int(checkpoint_name_or_index) - 1
            if 0 <= index < len(self.checkpoints):
                checkpoint = self.checkpoints[index]
        except ValueError:
            for cp in self.checkpoints:
                if (cp['name'].lower() == checkpoint_name_or_index.lower() or 
                    cp['tag'].lower() == checkpoint_name_or_index.lower()):
                    checkpoint = cp
                    break
        
        if not checkpoint:
            print(f"[ERROR] Checkpoint no encontrado: {checkpoint_name_or_index}")
            return False
        
        response = input(f"¿Eliminar checkpoint '{checkpoint['name']}' del registro? (s/n): ")
        if response.lower() != 's':
            return False
        
        self.checkpoints.remove(checkpoint)
        self._save_checkpoints()
        
        print(f"[OK] Checkpoint eliminado del registro: {checkpoint['name']}")
        print(f"[INFO] El tag de git '{checkpoint['tag']}' aun existe. Eliminalo manualmente si lo deseas:")
        print(f"   git tag -d {checkpoint['tag']}")
        
        return True


def main():
    """Función principal del script"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Sistema de Checkpoints para Building Manager Pro',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python checkpoint.py create "Versión estable" "Versión funcional completa"
  python checkpoint.py list
  python checkpoint.py restore 1
  python checkpoint.py restore "Versión estable"
  python checkpoint.py delete 1
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comando a ejecutar')
    
    # Comando create
    create_parser = subparsers.add_parser('create', help='Crear un nuevo checkpoint')
    create_parser.add_argument('name', help='Nombre del checkpoint')
    create_parser.add_argument('-d', '--description', default='', help='Descripción del checkpoint')
    create_parser.add_argument('--auto-commit', action='store_true', help='Hacer commit automático de cambios sin commitear')
    
    # Comando list
    subparsers.add_parser('list', help='Listar todos los checkpoints')
    
    # Comando restore
    restore_parser = subparsers.add_parser('restore', help='Restaurar un checkpoint')
    restore_parser.add_argument('checkpoint', help='Nombre o índice del checkpoint a restaurar')
    
    # Comando delete
    delete_parser = subparsers.add_parser('delete', help='Eliminar un checkpoint del registro')
    delete_parser.add_argument('checkpoint', help='Nombre o índice del checkpoint a eliminar')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = CheckpointManager()
    
    if args.command == 'create':
        manager.create_checkpoint(args.name, args.description, args.auto_commit)
    elif args.command == 'list':
        manager.list_checkpoints()
    elif args.command == 'restore':
        manager.restore_checkpoint(args.checkpoint)
    elif args.command == 'delete':
        manager.delete_checkpoint(args.checkpoint)


if __name__ == '__main__':
    main()
