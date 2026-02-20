"""
Módulo de Formularios Dinámicos
Originalmente un programa independiente para crear formularios online
"""

import os
import json
from datetime import datetime

MODULE_INFO = {
    "name": "Formularios Online",
    "description": "Crea y gestiona formularios dinámicos para recopilar información",
    "icon": "📝",
    "category": "oficina"
}

def _get_data_file(context):
    """Ruta del archivo de datos"""
    return os.path.join(context["DATA_DIR"], "formularios.json")

def _load_data(context):
    """Carga los datos del archivo JSON"""
    file_path = _get_data_file(context)
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    return {
        "formularios": [],
        "respuestas": []
    }

def _save_data(context, data):
    """Guarda los datos en el archivo JSON"""
    file_path = _get_data_file(context)
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_data(context):
    """Obtiene todos los datos del módulo de formularios"""
    return _load_data(context)

def execute(context):
    """Ejecuta acciones en el módulo de formularios"""
    action = context.get("action", "")
    params = context.get("params", {})
    
    data = _load_data(context)
    
    if action == "create_formulario":
        # Crear un nuevo formulario
        formulario = {
            "id": len(data["formularios"]) + 1,
            "titulo": params.get("titulo", ""),
            "descripcion": params.get("descripcion", ""),
            "campos": params.get("campos", []),
            # Los campos son: {name, label, type, required, options}
            "activo": True,
            "cliente_id": params.get("cliente_id"),  # Vinculación opcional con CRM
            "proyecto_id": params.get("proyecto_id"),  # Vinculación opcional con Proyectos
            "fecha_creacion": datetime.now().isoformat(),
            "respuestas_count": 0
        }
        data["formularios"].append(formulario)
        _save_data(context, data)
        return {"formulario": formulario, "message": "Formulario creado"}
    
    elif action == "submit_respuesta":
        # Enviar respuesta a un formulario
        respuesta = {
            "id": len(data["respuestas"]) + 1,
            "formulario_id": params.get("formulario_id"),
            "respuestas": params.get("respuestas", {}),  # {campo: valor}
            "fecha": datetime.now().isoformat(),
            "ip": params.get("ip", ""),
            "usuario": params.get("usuario", "Anónimo")
        }
        data["respuestas"].append(respuesta)
        
        # Actualizar contador de respuestas
        for form in data["formularios"]:
            if form["id"] == respuesta["formulario_id"]:
                form["respuestas_count"] = form.get("respuestas_count", 0) + 1
                break
        
        _save_data(context, data)
        return {"respuesta": respuesta, "message": "Respuesta guardada"}
    
    elif action == "get_respuestas":
        # Obtener respuestas de un formulario específico
        formulario_id = params.get("formulario_id")
        respuestas = [r for r in data["respuestas"] if r.get("formulario_id") == formulario_id]
        return {"respuestas": respuestas}
    
    elif action == "toggle_formulario":
        # Activar/desactivar formulario
        formulario_id = params.get("id")
        
        for form in data["formularios"]:
            if form["id"] == formulario_id:
                form["activo"] = not form.get("activo", True)
                _save_data(context, data)
                return {"formulario": form, "message": "Estado actualizado"}
        
        return {"error": "Formulario no encontrado"}
    
    else:
        return {"error": f"Acción desconocida: {action}"}

def get_summary(context):
    """Obtiene un resumen para el dashboard"""
    data = _load_data(context)
    
    total_formularios = len(data["formularios"])
    formularios_activos = len([f for f in data["formularios"] if f.get("activo", False)])
    total_respuestas = len(data["respuestas"])
    
    # Formulario más popular
    formulario_popular = None
    max_respuestas = 0
    
    for form in data["formularios"]:
        count = form.get("respuestas_count", 0)
        if count > max_respuestas:
            max_respuestas = count
            formulario_popular = form.get("titulo", "")
    
    return {
        "total_formularios": total_formularios,
        "formularios_activos": formularios_activos,
        "total_respuestas": total_respuestas,
        "formulario_popular": formulario_popular or "Ninguno",
        "respuestas_popular": max_respuestas
    }
