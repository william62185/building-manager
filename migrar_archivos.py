import sqlite3
import os


def migrar_archivos():
    """Migración manual para agregar columnas de archivos"""
    try:
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        print("🔄 Agregando columnas para archivos adjuntos...")

        # Verificar columnas existentes
        cursor.execute("PRAGMA table_info(inquilinos)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        print(f"Columnas existentes: {existing_columns}")

        # Columnas para archivos adjuntos
        file_columns = [
            ("archivo_identificacion", "TEXT"),
            ("archivo_contrato", "TEXT"),
            ("fecha_archivo_id", "TEXT"),
            ("fecha_archivo_contrato", "TEXT")
        ]

        # Agregar columnas faltantes
        for col_name, col_type in file_columns:
            if col_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE inquilinos ADD COLUMN {col_name} {col_type}")
                    print(f"✅ Columna agregada: {col_name}")
                except Exception as e:
                    print(f"❌ Error agregando {col_name}: {e}")
            else:
                print(f"⚠️  {col_name} ya existe")

        conn.commit()
        conn.close()
        print("🎉 Migración completada!")

    except Exception as e:
        print(f"❌ Error en migración: {e}")


if __name__ == "__main__":
    migrar_archivos()