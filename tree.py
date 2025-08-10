import os
from datetime import datetime

def listar_contenido(ruta, archivo_salida, prefijo=""):
    # Directorios a omitir para documentación
    omitir = {'.git', '__pycache__', '.env', 'node_modules', '.vscode', '.idea'}
    
    try:
        elementos = os.listdir(ruta)
    except PermissionError:
        archivo_salida.write(f"{prefijo}[Acceso denegado]: {ruta}\n")
        return

    # Filtrar elementos innecesarios
    elementos_filtrados = [e for e in elementos if e not in omitir]
    
    for i, elemento in enumerate(elementos_filtrados):
        path_completo = os.path.join(ruta, elemento)
        es_ultimo = i == len(elementos_filtrados) - 1
        conector = "└── " if es_ultimo else "├── "
        archivo_salida.write(prefijo + conector + elemento + "\n")

        if os.path.isdir(path_completo):
            nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
            listar_contenido(path_completo, archivo_salida, nuevo_prefijo)

# Configuración
ruta_raiz = r"C:\Djangoprojects\punto_venta_abarrotes"
nombre_archivo = "reporte_estructura_proyecto.txt"

# Generar archivo
with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
    archivo.write(f"Archivo local en Windows\n")
    archivo.write(f"Estructura del proyecto: {ruta_raiz}\n")
    archivo.write(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    archivo.write("=" * 50 + "\n\n")
    listar_contenido(ruta_raiz, archivo)

print(f"Estructura guardada en: {nombre_archivo}")

###########################################################################################
###########################################################################################
###########################################################################################


import os
import re
from datetime import datetime

def extraer_modelos(ruta_models):
    """Extrae información de modelos de un archivo models.py"""
    try:
        with open(ruta_models, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()
    except FileNotFoundError:
        return []

    modelos = []
    patron_modelo = r'class\s+(\w+)\s*\([^)]*models\.Model[^)]*\):'
    clases_modelo = re.finditer(patron_modelo, contenido)
    
    for match in clases_modelo:
        nombre_modelo = match.group(1)
        inicio = match.start()
        
        lineas = contenido[inicio:].split('\n')
        contenido_clase = []
        nivel_indentacion = None
        
        for linea in lineas[1:]:
            if linea.strip() == '':
                contenido_clase.append(linea)
                continue
                
            if nivel_indentacion is None and linea.strip():
                nivel_indentacion = len(linea) - len(linea.lstrip())
            
            if linea.strip() and (len(linea) - len(linea.lstrip())) <= (nivel_indentacion or 4) - 4:
                break
                
            contenido_clase.append(linea)
        
        campos = extraer_campos('\n'.join(contenido_clase))
        metodos = extraer_metodos('\n'.join(contenido_clase))
        
        modelos.append({
            'nombre': nombre_modelo,
            'campos': campos,
            'metodos': metodos
        })
    
    return modelos

def extraer_campos(contenido_clase):
    """Extrae campos del modelo"""
    campos = []
    patron_campo = r'^\s*(\w+)\s*=\s*models\.(\w+)\s*\([^)]*\)'
    
    for linea in contenido_clase.split('\n'):
        match = re.search(patron_campo, linea)
        if match:
            nombre_campo = match.group(1)
            tipo_campo = match.group(2)
            args = extraer_argumentos_campo(linea)
            
            campos.append({
                'nombre': nombre_campo,
                'tipo': tipo_campo,
                'argumentos': args
            })
    
    return campos

def extraer_argumentos_campo(linea):
    """Extrae argumentos comunes de un campo"""
    argumentos = []
    patrones = {
        'max_length': r'max_length\s*=\s*(\d+)',
        'default': r'default\s*=\s*([^,)]+)',
        'blank': r'blank\s*=\s*(True|False)',
        'null': r'null\s*=\s*(True|False)',
        'unique': r'unique\s*=\s*(True|False)',
        'auto_now_add': r'auto_now_add\s*=\s*(True|False)',
        'auto_now': r'auto_now\s*=\s*(True|False)',
        'related_name': r'related_name\s*=\s*[\'"]([^\'"]+)[\'"]',
        'on_delete': r'on_delete\s*=\s*models\.(\w+)'
    }
    
    for nombre, patron in patrones.items():
        match = re.search(patron, linea)
        if match:
            argumentos.append(f"{nombre}={match.group(1)}")
    
    return argumentos

def extraer_metodos(contenido_clase):
    """Extrae métodos del modelo"""
    metodos = []
    patron_metodo = r'^\s*def\s+(\w+)\s*\([^)]*\):'
    
    for linea in contenido_clase.split('\n'):
        match = re.search(patron_metodo, linea)
        if match:
            nombre_metodo = match.group(1)
            if not nombre_metodo.startswith('_') or nombre_metodo in ['__str__', '__unicode__']:
                metodos.append(nombre_metodo)
    
    return metodos

def extraer_admin(ruta_admin):
    """Extrae información de admin.py"""
    try:
        with open(ruta_admin, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()
    except FileNotFoundError:
        return []

    registros = []
    
    # Buscar registros admin.site.register
    patron_register = r'admin\.site\.register\s*\(\s*(\w+)(?:\s*,\s*(\w+))?\s*\)'
    matches = re.finditer(patron_register, contenido)
    
    for match in matches:
        modelo = match.group(1)
        admin_class = match.group(2) if match.group(2) else "ModelAdmin por defecto"
        registros.append({'modelo': modelo, 'admin_class': admin_class})
    
    # Buscar clases ModelAdmin
    patron_admin_class = r'class\s+(\w+)\s*\([^)]*ModelAdmin[^)]*\):'
    admin_classes = re.finditer(patron_admin_class, contenido)
    
    configs = []
    for match in admin_classes:
        nombre_clase = match.group(1)
        # Extraer configuraciones básicas
        configs.append({'nombre': nombre_clase})
    
    return {'registros': registros, 'admin_classes': configs}

def extraer_forms(ruta_forms):
    """Extrae información de forms.py"""
    try:
        with open(ruta_forms, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()
    except FileNotFoundError:
        return []

    formularios = []
    patron_form = r'class\s+(\w+)\s*\([^)]*forms\.\w+[^)]*\):'
    matches = re.finditer(patron_form, contenido)
    
    for match in matches:
        nombre_form = match.group(1)
        formularios.append({'nombre': nombre_form})
    
    return formularios

def extraer_views(ruta_views):
    """Extrae información de views.py"""
    try:
        with open(ruta_views, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()
    except FileNotFoundError:
        return []

    vistas = []
    
    # Vistas basadas en función
    patron_def = r'def\s+(\w+)\s*\([^)]*request[^)]*\):'
    funciones = re.finditer(patron_def, contenido)
    
    for match in funciones:
        nombre_vista = match.group(1)
        vistas.append({'nombre': nombre_vista, 'tipo': 'función'})
    
    # Vistas basadas en clase
    patron_class = r'class\s+(\w+)\s*\([^)]*View[^)]*\):'
    clases = re.finditer(patron_class, contenido)
    
    for match in clases:
        nombre_vista = match.group(1)
        vistas.append({'nombre': nombre_vista, 'tipo': 'clase'})
    
    return vistas

def extraer_urls(ruta_urls):
    """Extrae información de urls.py"""
    try:
        with open(ruta_urls, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()
    except FileNotFoundError:
        return []

    urls = []
    patron_url = r'path\s*\(\s*[\'"]([^\'"]+)[\'"]'
    matches = re.finditer(patron_url, contenido)
    
    for match in matches:
        patron_url = match.group(1)
        urls.append({'patron': patron_url})
    
    return urls

def extraer_settings(ruta_settings):
    """Extrae configuraciones importantes de settings.py"""
    try:
        with open(ruta_settings, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()
    except FileNotFoundError:
        return {}

    configuraciones = {}
    
    # Configuraciones a extraer
    patrones = {
        'DEBUG': r'DEBUG\s*=\s*(True|False)',
        'SECRET_KEY': r'SECRET_KEY\s*=\s*[\'"]([^\'"]*)[\'"]',
        'ALLOWED_HOSTS': r'ALLOWED_HOSTS\s*=\s*(\[[^\]]*\])',
        'DATABASES': r'DATABASES\s*=\s*\{[^}]*[\'"]ENGINE[\'"]:\s*[\'"]([^\'"]*)[\'"]',
        'STATIC_URL': r'STATIC_URL\s*=\s*[\'"]([^\'"]*)[\'"]',
        'MEDIA_URL': r'MEDIA_URL\s*=\s*[\'"]([^\'"]*)[\'"]',
        'STATIC_ROOT': r'STATIC_ROOT\s*=\s*[\'"]?([^\'"]*)[\'"]?',
        'MEDIA_ROOT': r'MEDIA_ROOT\s*=\s*[\'"]?([^\'"]*)[\'"]?',
    }
    
    for nombre, patron in patrones.items():
        match = re.search(patron, contenido)
        if match:
            configuraciones[nombre] = match.group(1)
    
    # Extraer INSTALLED_APPS
    patron_apps = r'INSTALLED_APPS\s*=\s*\[(.*?)\]'
    match = re.search(patron_apps, contenido, re.DOTALL)
    if match:
        apps_content = match.group(1)
        apps = re.findall(r'[\'"]([^\'"]+)[\'"]', apps_content)
        configuraciones['INSTALLED_APPS'] = apps
    
    # Extraer MIDDLEWARE
    patron_middleware = r'MIDDLEWARE\s*=\s*\[(.*?)\]'
    match = re.search(patron_middleware, contenido, re.DOTALL)
    if match:
        middleware_content = match.group(1)
        middleware = re.findall(r'[\'"]([^\'"]+)[\'"]', middleware_content)
        configuraciones['MIDDLEWARE'] = middleware
    
    return configuraciones

def escribir_seccion_modelos(archivo, app_nombre, ruta_models):
    """Escribe la sección de modelos"""
    modelos = extraer_modelos(ruta_models)
    
    if not modelos:
        archivo.write("Sin modelos definidos\n\n")
        return
    
    for modelo in modelos:
        archivo.write(f"\n=== MODELO: {modelo['nombre']} ===\n")
        
        if modelo['campos']:
            archivo.write("CAMPOS:\n")
            for campo in modelo['campos']:
                args_str = ", ".join(campo['argumentos']) if campo['argumentos'] else ""
                if args_str:
                    archivo.write(f"  - {campo['nombre']} ({campo['tipo']}, {args_str})\n")
                else:
                    archivo.write(f"  - {campo['nombre']} ({campo['tipo']})\n")
        else:
            archivo.write("Sin campos definidos\n")
        
        if modelo['metodos']:
            archivo.write("MÉTODOS:\n")
            for metodo in modelo['metodos']:
                archivo.write(f"  - {metodo}()\n")
        
        archivo.write("\n")

def escribir_seccion_admin(archivo, app_nombre, ruta_admin):
    """Escribe la sección de admin"""
    admin_info = extraer_admin(ruta_admin)
    
    if not admin_info['registros']:
        archivo.write("Sin registros de admin\n\n")
        return
    
    archivo.write("REGISTROS:\n")
    for registro in admin_info['registros']:
        archivo.write(f"  - {registro['modelo']} → {registro['admin_class']}\n")
    
    if admin_info['admin_classes']:
        archivo.write("CLASES ADMIN:\n")
        for admin_class in admin_info['admin_classes']:
            archivo.write(f"  - {admin_class['nombre']}\n")
    
    archivo.write("\n")

def escribir_seccion_forms(archivo, app_nombre, ruta_forms):
    """Escribe la sección de forms"""
    formularios = extraer_forms(ruta_forms)
    
    if not formularios:
        archivo.write("Sin formularios definidos\n\n")
        return
    
    archivo.write("FORMULARIOS:\n")
    for form in formularios:
        archivo.write(f"  - {form['nombre']}\n")
    archivo.write("\n")

def escribir_seccion_views(archivo, app_nombre, ruta_views):
    """Escribe la sección de views"""
    vistas = extraer_views(ruta_views)
    
    if not vistas:
        archivo.write("Sin vistas definidas\n\n")
        return
    
    archivo.write("VISTAS:\n")
    for vista in vistas:
        archivo.write(f"  - {vista['nombre']} ({vista['tipo']})\n")
    archivo.write("\n")

def escribir_seccion_urls(archivo, app_nombre, ruta_urls):
    """Escribe la sección de urls"""
    urls = extraer_urls(ruta_urls)
    
    if not urls:
        archivo.write("Sin URLs definidas\n\n")
        return
    
    archivo.write("PATRONES URL:\n")
    for url in urls:
        archivo.write(f"  - {url['patron']}\n")
    archivo.write("\n")

def escribir_seccion_settings(archivo, ruta_settings):
    """Escribe la sección de configuraciones"""
    settings = extraer_settings(ruta_settings)
    
    if not settings:
        archivo.write("Archivo settings.py no encontrado\n\n")
        return
    
    archivo.write("CONFIGURACIONES PRINCIPALES:\n")
    
    # Configuraciones básicas
    for config in ['DEBUG', 'DATABASES', 'STATIC_URL', 'MEDIA_URL']:
        if config in settings:
            archivo.write(f"  - {config}: {settings[config]}\n")
    
    # INSTALLED_APPS
    if 'INSTALLED_APPS' in settings:
        archivo.write("  - INSTALLED_APPS:\n")
        for app in settings['INSTALLED_APPS']:
            archivo.write(f"    * {app}\n")
    
    # MIDDLEWARE
    if 'MIDDLEWARE' in settings:
        archivo.write("  - MIDDLEWARE:\n")
        for middleware in settings['MIDDLEWARE']:
            archivo.write(f"    * {middleware}\n")
    
    archivo.write("\n")

def generar_reporte_django(ruta_proyecto, tipo='all'):
    """Genera reporte completo de proyecto Django"""
    
    # Buscar apps en el proyecto
    apps = []
    for item in os.listdir(ruta_proyecto):
        ruta_app = os.path.join(ruta_proyecto, item)
        if os.path.isdir(ruta_app) and not item.startswith('.'):
            # Verificar si es una app Django
            archivos_django = ['models.py', 'admin.py', 'views.py', 'apps.py']
            if any(os.path.exists(os.path.join(ruta_app, archivo)) for archivo in archivos_django):
                apps.append(item)
    
    # Generar archivo de reporte
    nombre_archivo = "reporte_django.txt"
    
    with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
        archivo.write(f"REPORTE PROYECTO DJANGO\n")
        archivo.write(f"Ruta: {ruta_proyecto}\n")
        archivo.write(f"Tipo: {tipo}\n")
        archivo.write(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        archivo.write("=" * 60 + "\n\n")
        
        for app_nombre in apps:
            archivo.write(f"APP: {app_nombre.upper()}\n")
            archivo.write("=" * 40 + "\n\n")
            
            ruta_app = os.path.join(ruta_proyecto, app_nombre)
            
            # Escribir secciones según el tipo solicitado
            if tipo in ['models', 'all']:
                ruta_models = os.path.join(ruta_app, 'models.py')
                if os.path.exists(ruta_models):
                    archivo.write("MODELOS:\n")
                    archivo.write("-" * 20 + "\n")
                    escribir_seccion_modelos(archivo, app_nombre, ruta_models)
            
            if tipo in ['admin', 'all']:
                ruta_admin = os.path.join(ruta_app, 'admin.py')
                if os.path.exists(ruta_admin):
                    archivo.write("ADMIN:\n")
                    archivo.write("-" * 20 + "\n")
                    escribir_seccion_admin(archivo, app_nombre, ruta_admin)
            
            if tipo in ['forms', 'all']:
                ruta_forms = os.path.join(ruta_app, 'forms.py')
                if os.path.exists(ruta_forms):
                    archivo.write("FORMS:\n")
                    archivo.write("-" * 20 + "\n")
                    escribir_seccion_forms(archivo, app_nombre, ruta_forms)
            
            if tipo in ['views', 'all']:
                ruta_views = os.path.join(ruta_app, 'views.py')
                if os.path.exists(ruta_views):
                    archivo.write("VIEWS:\n")
                    archivo.write("-" * 20 + "\n")
                    escribir_seccion_views(archivo, app_nombre, ruta_views)
            
            if tipo in ['urls', 'all']:
                ruta_urls = os.path.join(ruta_app, 'urls.py')
                if os.path.exists(ruta_urls):
                    archivo.write("URLS:\n")
                    archivo.write("-" * 20 + "\n")
                    escribir_seccion_urls(archivo, app_nombre, ruta_urls)
            
            archivo.write("\n")
        
        # Agregar sección de configuraciones al final
        if tipo in ['settings', 'all']:
            archivo.write("CONFIGURACIONES DEL PROYECTO\n")
            archivo.write("=" * 40 + "\n\n")
            
            # Buscar settings.py en el directorio principal del proyecto
            for item in os.listdir(ruta_proyecto):
                ruta_settings_dir = os.path.join(ruta_proyecto, item)
                if os.path.isdir(ruta_settings_dir):
                    ruta_settings = os.path.join(ruta_settings_dir, 'settings.py')
                    if os.path.exists(ruta_settings):
                        escribir_seccion_settings(archivo, ruta_settings)
                        break
    
    print(f"Reporte Django guardado en: {nombre_archivo}")

# Configuración
ruta_proyecto = r"C:\Djangoprojects\punto_venta_abarrotes"

# Opciones disponibles:
# - 'all': Todo (models, admin, forms, views, urls, settings)
# - 'models': Solo modelos
# - 'admin': Solo admin
# - 'forms': Solo formularios  
# - 'views': Solo vistas
# - 'urls': Solo URLs
# - 'settings': Solo configuraciones

# Generar reporte completo
generar_reporte_django(ruta_proyecto, tipo='all')