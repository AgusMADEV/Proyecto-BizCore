"""
Sistema de carga dinámica de módulos para Jocarsa Suite
Busca y carga automáticamente todos los módulos desde la carpeta modules/
"""

import importlib.util
import os
from typing import Dict, Any

def _import_module_from_path(module_name: str, file_path: str):
    """Importa un módulo Python desde una ruta específica"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if not spec or not spec.loader:
        return None
    
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def load_backend_modules() -> Dict[str, Dict[str, Any]]:
    """
    Escanea la carpeta modules/ y carga todos los módulos que cumplan
    con la interfaz esperada:
    
    - MODULE_INFO: dict con {name, description, icon, category}
    - get_data(context): función para obtener datos del módulo
    - execute(context): función para ejecutar acciones
    - get_summary(context): función opcional para el dashboard
    
    Returns:
        dict: {module_type: {MODULE_INFO, get_data, execute, get_summary}}
    """
    
    registry: Dict[str, Dict[str, Any]] = {}
    base_dir = os.path.dirname(__file__)
    
    for filename in os.listdir(base_dir):
        # Solo archivos Python (excepto __init__.py y archivos privados)
        if not filename.endswith(".py"):
            continue
        if filename.startswith("__") or filename.startswith("_"):
            continue
        
        path = os.path.join(base_dir, filename)
        mod_name = f"modules.{filename[:-3]}"
        
        try:
            mod = _import_module_from_path(mod_name, path)
            
            # Validar que el módulo tiene la estructura correcta
            module_info = getattr(mod, "MODULE_INFO", None)
            get_data = getattr(mod, "get_data", None)
            execute = getattr(mod, "execute", None)
            
            if not isinstance(module_info, dict):
                print(f"⚠️  Módulo {filename}: no tiene MODULE_INFO válido")
                continue
            
            if not callable(get_data):
                print(f"⚠️  Módulo {filename}: no tiene función get_data()")
                continue
            
            if not callable(execute):
                print(f"⚠️  Módulo {filename}: no tiene función execute()")
                continue
            
            # Función opcional para el dashboard
            get_summary = getattr(mod, "get_summary", None)
            
            # Registrar el módulo
            module_type = filename[:-3]  # nombre del archivo sin .py
            registry[module_type] = {
                "name": module_info.get("name", module_type),
                "description": module_info.get("description", "Sin descripción"),
                "icon": module_info.get("icon", "📦"),
                "category": module_info.get("category", "general"),
                "get_data": get_data,
                "execute": execute,
                "get_summary": get_summary if callable(get_summary) else lambda x: {}
            }
            
            print(f"✅ Módulo cargado: {module_info.get('name', module_type)}")
            
        except Exception as e:
            print(f"❌ Error cargando {filename}: {e}")
    
    return registry
