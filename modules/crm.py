"""
Módulo CRM - Gestión de Clientes
Originalmente un programa independiente para gestionar contactos y clientes
"""

import os
import json
from datetime import datetime

MODULE_INFO = {
    "name": "CRM - Gestión de Clientes",
    "description": "Gestiona clientes, contactos y oportunidades de venta",
    "icon": "👥",
    "category": "marketing"
}

def _get_data_file(context):
    """Ruta del archivo de datos"""
    return os.path.join(context["DATA_DIR"], "crm_clientes.json")

def _load_data(context):
    """Carga los datos del archivo JSON"""
    file_path = _get_data_file(context)
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    return {
        "clientes": [],
        "contactos": [],
        "oportunidades": []
    }

def _save_data(context, data):
    """Guarda los datos en el archivo JSON"""
    file_path = _get_data_file(context)
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_data(context):
    """Obtiene todos los datos del módulo CRM"""
    return _load_data(context)

def execute(context):
    """Ejecuta acciones en el módulo CRM"""
    action = context.get("action", "")
    params = context.get("params", {})
    
    data = _load_data(context)
    
    if action == "add_cliente":
        # Añadir un nuevo cliente
        cliente = {
            "id": len(data["clientes"]) + 1,
            "nombre": params.get("nombre", ""),
            "email": params.get("email", ""),
            "telefono": params.get("telefono", ""),
            "empresa": params.get("empresa", ""),
            "fecha_creacion": datetime.now().isoformat(),
            "estado": "activo"
        }
        data["clientes"].append(cliente)
        _save_data(context, data)
        return {"cliente": cliente, "message": "Cliente creado exitosamente"}
    
    elif action == "add_contacto":
        # Añadir un nuevo contacto relacionado con un cliente
        contacto = {
            "id": len(data["contactos"]) + 1,
            "cliente_id": params.get("cliente_id"),
            "fecha": datetime.now().isoformat(),
            "tipo": params.get("tipo", "llamada"),  # llamada, email, reunión
            "notas": params.get("notas", ""),
            "usuario": context.get("session", {}).get("usuario", "Sistema")
        }
        data["contactos"].append(contacto)
        _save_data(context, data)
        return {"contacto": contacto, "message": "Contacto registrado"}
    
    elif action == "add_oportunidad":
        # Añadir una oportunidad de venta
        oportunidad = {
            "id": len(data["oportunidades"]) + 1,
            "cliente_id": params.get("cliente_id"),
            "titulo": params.get("titulo", ""),
            "valor": params.get("valor", 0),
            "probabilidad": params.get("probabilidad", 50),
            "estado": "abierta",  # abierta, en_proceso, ganada, perdida
            "fecha_creacion": datetime.now().isoformat()
        }
        data["oportunidades"].append(oportunidad)
        _save_data(context, data)
        return {"oportunidad": oportunidad, "message": "Oportunidad creada"}
    
    elif action == "update_estado_oportunidad":
        # Actualizar estado de oportunidad
        oportunidad_id = params.get("id")
        nuevo_estado = params.get("estado")
        
        for op in data["oportunidades"]:
            if op["id"] == oportunidad_id:
                op["estado"] = nuevo_estado
                _save_data(context, data)
                return {"oportunidad": op, "message": "Estado actualizado"}
        
        return {"error": "Oportunidad no encontrada"}
    
    else:
        return {"error": f"Acción desconocida: {action}"}

def get_summary(context):
    """Obtiene un resumen para el dashboard"""
    data = _load_data(context)
    
    # Calcular estadísticas
    total_clientes = len(data["clientes"])
    clientes_activos = len([c for c in data["clientes"] if c.get("estado") == "activo"])
    
    total_oportunidades = len(data["oportunidades"])
    oportunidades_abiertas = len([o for o in data["oportunidades"] if o.get("estado") == "abierta"])
    
    valor_oportunidades = sum(o.get("valor", 0) for o in data["oportunidades"] if o.get("estado") in ["abierta", "en_proceso"])
    
    return {
        "total_clientes": total_clientes,
        "clientes_activos": clientes_activos,
        "total_oportunidades": total_oportunidades,
        "oportunidades_abiertas": oportunidades_abiertas,
        "valor_pipeline": valor_oportunidades
    }
