import sqlite3
import datetime


def migrar_base_datos():
    """
    Script para agregar nuevos campos a la tabla inquilinos
    """
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        print("🔄 Iniciando migración de base de datos...")
        print("=" * 50)

        # Lista de nuevas columnas a agregar
        nuevas_columnas = [
            ("identificacion", "TEXT"),
            ("email", "TEXT"),
            ("celular", "TEXT"),
            ("profesion", "TEXT"),
            ("fecha_ingreso", "TEXT"),
            ("deposito", "REAL DEFAULT 0"),
            ("estado", "TEXT DEFAULT 'Activo'"),
            ("contacto_emergencia", "TEXT"),
            ("telefono_emergencia", "TEXT"),
            ("relacion_emergencia", "TEXT"),
            ("notas", "TEXT")
        ]

        # Verificar qué columnas ya existen
        cursor.execute("PRAGMA table_info(inquilinos)")
        columnas_existentes = [columna[1] for columna in cursor.fetchall()]

        print("📋 Columnas existentes:")
        for col in columnas_existentes:
            print(f"   ✅ {col}")

        print("\n🆕 Agregando nuevas columnas:")

        # Agregar cada columna nueva
        for nombre_columna, tipo_columna in nuevas_columnas:
            if nombre_columna not in columnas_existentes:
                try:
                    query = f"ALTER TABLE inquilinos ADD COLUMN {nombre_columna} {tipo_columna}"
                    cursor.execute(query)
                    print(f"   ✅ Agregada: {nombre_columna} ({tipo_columna})")
                except sqlite3.Error as e:
                    print(f"   ❌ Error agregando {nombre_columna}: {e}")
            else:
                print(f"   ⚠️  {nombre_columna} ya existe, omitiendo...")

        # Confirmar cambios
        conn.commit()

        # Verificar estructura final
        print("\n📊 Estructura final de la tabla inquilinos:")
        cursor.execute("PRAGMA table_info(inquilinos)")
        todas_columnas = cursor.fetchall()

        for i, (cid, nombre, tipo, notnull, default, pk) in enumerate(todas_columnas, 1):
            estado = "🆕" if nombre in [col[0] for col in nuevas_columnas] else "📋"
            print(f"   {estado} {i:2d}. {nombre:20} ({tipo})")

        print(f"\n✅ Migración completada exitosamente!")
        print(f"📊 Total de columnas: {len(todas_columnas)}")

        # Crear respaldo después de la migración
        fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_respaldo = f"edificio_backup_migracion_{fecha}.db"

        import shutil
        shutil.copy2('edificio.db', nombre_respaldo)
        print(f"💾 Respaldo creado: {nombre_respaldo}")

        conn.close()

    except sqlite3.Error as e:
        print(f"❌ Error de SQLite: {e}")
    except Exception as e:
        print(f"❌ Error general: {e}")

    print("\n" + "=" * 50)
    print("🎯 Migración terminada. ¡Listo para actualizar el código!")


def verificar_migracion():
    """
    Verifica que la migración se haya realizado correctamente
    """
    try:
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        # Contar inquilinos existentes
        cursor.execute("SELECT COUNT(*) FROM inquilinos")
        total_inquilinos = cursor.fetchone()[0]

        # Verificar si hay datos en los nuevos campos (deberían estar vacíos/null)
        print(f"\n🔍 Verificación post-migración:")
        print(f"📊 Total de inquilinos existentes: {total_inquilinos}")

        if total_inquilinos > 0:
            print("📋 Los inquilinos existentes tendrán valores vacíos en los nuevos campos.")
            print("💡 Puedes editarlos desde la aplicación para completar la información.")

            # Mostrar ejemplo de inquilino existente
            cursor.execute("SELECT id, nombre, apartamento FROM inquilinos LIMIT 1")
            ejemplo = cursor.fetchone()
            if ejemplo:
                print(f"📝 Ejemplo - ID: {ejemplo[0]}, Nombre: {ejemplo[1]}, Apto: {ejemplo[2]}")

        conn.close()

    except Exception as e:
        print(f"❌ Error en verificación: {e}")


if __name__ == "__main__":
    print("🏗️  MIGRACIÓN DE BASE DE DATOS - INQUILINOS")
    print("=" * 50)
    print("Este script agregará campos adicionales a la tabla inquilinos:")
    print("• Identificación, Email, Celular")
    print("• Profesión, Fecha de ingreso, Depósito")
    print("• Estado, Contacto emergencia")
    print("• Notas")
    print("=" * 50)

    respuesta = input("¿Continuar con la migración? (s/n): ").lower().strip()

    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        migrar_base_datos()
        verificar_migracion()
    else:
        print("❌ Migración cancelada.")