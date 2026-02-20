"""
Módulo de Informes y Análisis
Originalmente un programa independiente para generar reportes
"""

import os
import json
from datetime import datetime
from collections import defaultdict

MODULE_INFO = {
    "name": "Informes y Análisis",
    "description": "Genera informes y analíticas consolidadas de todos los módulos",
    "icon": "📊",
    "category": "gestión"
}

def _get_data_file(context):
    """Ruta del archivo de datos"""
    return os.path.join(context["DATA_DIR"], "informes.json")

def _load_data(context):
    """Carga los datos del archivo JSON"""
    file_path = _get_data_file(context)
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    return {
        "informes_generados": []
    }

def _save_data(context, data):
    """Guarda los datos en el archivo JSON"""
    file_path = _get_data_file(context)
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _load_other_module_data(context, module_name):
    """Carga datos de otros módulos para análisis cruzado"""
    file_path = os.path.join(context["DATA_DIR"], f"{module_name}.json")
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    return {}

def get_data(context):
    """Obtiene todos los datos del módulo de informes"""
    return _load_data(context)

def execute(context):
    """Ejecuta acciones en el módulo de informes"""
    action = context.get("action", "")
    params = context.get("params", {})
    
    data = _load_data(context)
    
    if action == "generar_informe":
        # Generar un nuevo informe
        tipo = params.get("tipo", "general")
        
        # Cargar datos de todos los módulos
        crm_data = _load_other_module_data(context, "crm_clientes")
        proyectos_data = _load_other_module_data(context, "proyectos")
        formularios_data = _load_other_module_data(context, "formularios")
        
        # Generar informe según el tipo
        informe_contenido = {}
        
        if tipo == "general":
            informe_contenido = {
                "tipo": "Informe General",
                "clientes_totales": len(crm_data.get("clientes", [])),
                "proyectos_totales": len(proyectos_data.get("proyectos", [])),
                "formularios_activos": len([f for f in formularios_data.get("formularios", []) if f.get("activo")]),
                "oportunidades_abiertas": len([o for o in crm_data.get("oportunidades", []) if o.get("estado") in ["abierta", "en_proceso"]]),
            }
        
        elif tipo == "ventas":
            oportunidades = crm_data.get("oportunidades", [])
            total_pipeline = sum(o.get("valor", 0) for o in oportunidades if o.get("estado") in ["abierta", "en_proceso"])
            ganadas = [o for o in oportunidades if o.get("estado") == "ganada"]
            total_ganado = sum(o.get("valor", 0) for o in ganadas)
            
            informe_contenido = {
                "tipo": "Informe de Ventas",
                "total_oportunidades": len(oportunidades),
                "valor_pipeline": total_pipeline,
                "oportunidades_ganadas": len(ganadas),
                "valor_ganado": total_ganado,
                "tasa_conversion": (len(ganadas) / len(oportunidades) * 100) if oportunidades else 0
            }
        
        elif tipo == "proyectos":
            proyectos = proyectos_data.get("proyectos", [])
            tareas = proyectos_data.get("tareas", [])
            
            # Análisis por estado
            estados_proyectos = defaultdict(int)
            for p in proyectos:
                estados_proyectos[p.get("estado", "sin_estado")] += 1
            
            # Análisis de tareas
            total_horas_estimadas = sum(t.get("tiempo_estimado", 0) for t in tareas)
            total_horas_reales = sum(t.get("tiempo_real", 0) for t in tareas)
            
            informe_contenido = {
                "tipo": "Informe de Proyectos",
                "total_proyectos": len(proyectos),
                "estados": dict(estados_proyectos),
                "total_tareas": len(tareas),
                "horas_estimadas": total_horas_estimadas,
                "horas_reales": total_horas_reales,
                "desviacion_tiempo": total_horas_reales - total_horas_estimadas
            }
        
        elif tipo == "integracion":
            # Informe de integración entre módulos
            clientes = crm_data.get("clientes", [])
            proyectos = proyectos_data.get("proyectos", [])
            formularios = formularios_data.get("formularios", [])
            
            # Clientes con proyectos
            clientes_con_proyectos = len(set(p.get("cliente_id") for p in proyectos if p.get("cliente_id")))
            
            # Formularios vinculados
            formularios_vinculados_crm = len([f for f in formularios if f.get("cliente_id")])
            formularios_vinculados_proyectos = len([f for f in formularios if f.get("proyecto_id")])
            
            informe_contenido = {
                "tipo": "Informe de Integración",
                "clientes_totales": len(clientes),
                "clientes_con_proyectos": clientes_con_proyectos,
                "proyectos_totales": len(proyectos),
                "formularios_vinculados_crm": formularios_vinculados_crm,
                "formularios_vinculados_proyectos": formularios_vinculados_proyectos,
                "tasa_integracion_clientes": (clientes_con_proyectos / len(clientes) * 100) if clientes else 0
            }
        
        # Guardar el informe generado
        informe = {
            "id": len(data["informes_generados"]) + 1,
            "tipo": tipo,
            "fecha_generacion": datetime.now().isoformat(),
            "contenido": informe_contenido,
            "generado_por": context.get("session", {}).get("usuario", "Sistema")
        }
        
        data["informes_generados"].append(informe)
        _save_data(context, data)
        
        return {"informe": informe, "message": "Informe generado exitosamente"}
    
    elif action == "get_informes":
        # Obtener historial de informes
        return {"informes": data["informes_generados"]}
    
    else:
        return {"error": f"Acción desconocida: {action}"}

def get_summary(context):
    """Obtiene un resumen para el dashboard"""
    data = _load_data(context)
    
    total_informes = len(data["informes_generados"])
    
    # Tipo de informe más generado
    tipos_count = defaultdict(int)
    for informe in data["informes_generados"]:
        tipos_count[informe.get("tipo", "general")] += 1
    
    tipo_popular = max(tipos_count.items(), key=lambda x: x[1])[0] if tipos_count else "Ninguno"
    
    return {
        "total_informes": total_informes,
        "tipo_popular": tipo_popular,
        "ultimo_informe": data["informes_generados"][-1].get("tipo") if data["informes_generados"] else "Ninguno"
    }
