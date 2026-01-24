# 📌 Guía de Uso del Sistema de Checkpoints

## 🎯 ¿Qué son los Checkpoints?

Los checkpoints son **puntos de restauración funcionales** que te permiten volver a un estado conocido y funcional del proyecto en cualquier momento. Son especialmente útiles cuando:

- Restauras desde git y faltan archivos
- Haces cambios experimentales que no funcionan
- Necesitas volver a una versión estable rápidamente
- Colaboras con otros y necesitas estados conocidos

## 🚀 Comandos Principales

### 1. Crear un Checkpoint

```bash
python checkpoint.py create "Nombre del Checkpoint" -d "Descripción opcional"
```

**Ejemplos:**
```bash
# Checkpoint básico
python checkpoint.py create "Versión Estable"

# Checkpoint con descripción
python checkpoint.py create "Configuración Completa" -d "Todos los servicios funcionando"

# Checkpoint después de una feature
python checkpoint.py create "Feature Reportes" -d "Reportes de ocupación e inquilinos implementados"
```

**¿Cuándo crear checkpoints?**
- ✅ Después de completar una funcionalidad importante
- ✅ Antes de hacer cambios experimentales
- ✅ Cuando todo funciona correctamente
- ✅ Antes de restaurar desde git
- ✅ Después de resolver errores complejos

### 2. Listar Checkpoints Disponibles

```bash
python checkpoint.py list
```

Muestra todos los checkpoints guardados con:
- Nombre y descripción
- Fecha de creación
- Rama y commit asociado
- Tag de git

### 3. Restaurar un Checkpoint

```bash
# Por índice (número de la lista)
python checkpoint.py restore 1

# Por nombre
python checkpoint.py restore "Versión Estable"

# Por tag
python checkpoint.py restore "checkpoint-version-estable-20250124-120000"
```

**⚠️ Advertencia:** Restaurar un checkpoint te moverá a ese commit. Si tienes cambios sin commitear, se te preguntará si quieres guardarlos primero.

**Después de restaurar:**
```bash
# Crear una nueva rama para trabajar desde el checkpoint
git checkout -b restore-desde-checkpoint
```

### 4. Eliminar un Checkpoint del Registro

```bash
python checkpoint.py delete 1
# o
python checkpoint.py delete "Nombre del Checkpoint"
```

Esto solo elimina el checkpoint del registro (`.checkpoints.json`), pero **NO elimina el tag de git**. Si quieres eliminar el tag también:

```bash
git tag -d nombre-del-tag
```

## 🔍 Validar Integridad del Proyecto

Antes de crear un checkpoint o después de restaurar, valida que todo esté correcto:

```bash
python validate_integrity.py
```

Este script verifica:
- ✅ Que existan todos los archivos críticos
- ✅ Que los imports funcionen correctamente
- ✅ Que los servicios tengan sus instancias globales
- ✅ Que las vistas tengan las variables necesarias
- ✅ Que la estructura de directorios sea correcta

## 📋 Flujo de Trabajo Recomendado

### Escenario 1: Antes de hacer cambios experimentales

```bash
# 1. Validar que todo funciona
python validate_integrity.py

# 2. Crear checkpoint
python checkpoint.py create "Antes de cambios experimentales"

# 3. Hacer tus cambios...

# 4. Si algo sale mal, restaurar
python checkpoint.py restore "Antes de cambios experimentales"
```

### Escenario 2: Después de restaurar desde git

```bash
# 1. Restaurar desde git (como hiciste antes)
git reset --hard HEAD

# 2. Validar qué falta
python validate_integrity.py

# 3. Restaurar desde un checkpoint funcional
python checkpoint.py restore "Versión Estable"

# 4. Crear nueva rama para trabajar
git checkout -b restore-$(date +%Y%m%d)
```

### Escenario 3: Después de completar una feature

```bash
# 1. Validar integridad
python validate_integrity.py

# 2. Hacer commit de los cambios
git add .
git commit -m "Feature: Nueva funcionalidad X"

# 3. Crear checkpoint
python checkpoint.py create "Feature X Completa" -d "Funcionalidad X implementada y probada"
```

## 🎯 Mejores Prácticas

### ✅ HACER:
- Crear checkpoints después de completar funcionalidades
- Validar integridad antes de crear checkpoints
- Usar nombres descriptivos para los checkpoints
- Crear checkpoints antes de cambios grandes
- Documentar en la descripción qué incluye el checkpoint

### ❌ NO HACER:
- Crear checkpoints de código que no funciona
- Usar nombres genéricos como "test" o "backup"
- Olvidar validar antes de crear
- Crear demasiados checkpoints (mantén solo los importantes)

## 🔧 Solución de Problemas

### Error: "No se encontró un repositorio git"
**Solución:** Asegúrate de estar en un repositorio git inicializado:
```bash
git init
git add .
git commit -m "Initial commit"
```

### Error: "Checkpoint no encontrado"
**Solución:** Lista los checkpoints disponibles:
```bash
python checkpoint.py list
```

### Error al restaurar: "Cambios sin commitear"
**Solución:** Tienes dos opciones:
1. Hacer commit de los cambios primero
2. Crear una rama con los cambios antes de restaurar

### El checkpoint se creó pero no aparece en la lista
**Solución:** Verifica que `.checkpoints.json` existe y tiene permisos de escritura.

## 📚 Archivos del Sistema

- `checkpoint.py` - Script principal de gestión de checkpoints
- `validate_integrity.py` - Script de validación de integridad
- `.checkpoints.json` - Registro de checkpoints (se guarda en git)
- `PROJECT_MANIFEST.md` - Documentación de la estructura del proyecto

## 💡 Tips Adicionales

1. **Nombres descriptivos:** Usa nombres que indiquen claramente qué incluye el checkpoint
   - ✅ "Configuración Completa Restaurada"
   - ❌ "backup1"

2. **Checkpoints regulares:** Crea checkpoints al menos una vez por día de trabajo productivo

3. **Limpieza:** Elimina checkpoints antiguos que ya no necesites (pero mantén los tags de git por si acaso)

4. **Documentación:** Usa las descripciones para documentar qué cambios incluye cada checkpoint

---

**¿Preguntas?** Revisa `PROJECT_MANIFEST.md` para más detalles sobre la estructura del proyecto.
