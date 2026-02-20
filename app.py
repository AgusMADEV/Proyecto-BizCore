"""
Jocarsa Suite - Sistema de Gestión Empresarial Integrado
=========================================================

Este proyecto integra varios módulos independientes del catálogo Jocarsa
en una suite empresarial unificada que es más que la suma de sus partes.

Módulos integrados:
- CRM (Gestión de clientes)
- Proyectos (Gestión de tareas y proyectos)
- Formularios (Creación de formularios dinámicos)
- Informes (Generación de reportes)

La integración permite compartir datos entre módulos y ofrecer una
experiencia unificada de gestión empresarial.
"""

from flask import Flask, request, jsonify, render_template, session
import os
import json
import webbrowser
from threading import Timer
from datetime import datetime
from modules import load_backend_modules

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "jocarsa_suite_2026_secret_key"

# Configuración
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")

# Aseguramos que existe el directorio de datos
os.makedirs(DATA_DIR, exist_ok=True)

# Cargar módulos backend de forma dinámica
BACKEND_MODULES = load_backend_modules()

@app.route("/")
def index():
    """Página principal - Dashboard integrado"""
    return render_template("index.html")

@app.route("/api/modules")
def api_modules():
    """Devuelve la lista de módulos disponibles"""
    modules = []
    for mod_type, mod_data in BACKEND_MODULES.items():
        module_info = {
            "type": mod_type,
            "name": mod_data["name"],
            "description": mod_data["description"],
            "icon": mod_data.get("icon", "📦"),
            "category": mod_data.get("category", "general")
        }
        modules.append(module_info)
    
    return jsonify({"modules": modules})

@app.route("/api/module/<module_name>", methods=["GET", "POST"])
def api_module(module_name):
    """Endpoint para interactuar con un módulo específico"""
    
    if module_name not in BACKEND_MODULES:
        return jsonify({"error": "Módulo no encontrado"}), 404
    
    module = BACKEND_MODULES[module_name]
    
    if request.method == "GET":
        # Obtener datos del módulo
        try:
            data = module["get_data"]({
                "DATA_DIR": DATA_DIR,
                "session": dict(session)
            })
            return jsonify({"ok": True, "data": data})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500
    
    elif request.method == "POST":
        # Ejecutar acción en el módulo
        try:
            payload = request.get_json() or {}
            action = payload.get("action", "")
            params = payload.get("params", {})
            
            result = module["execute"]({
                "action": action,
                "params": params,
                "DATA_DIR": DATA_DIR,
                "session": dict(session)
            })
            
            return jsonify({"ok": True, "result": result})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/dashboard")
def api_dashboard():
    """Obtiene datos consolidados de todos los módulos para el dashboard"""
    dashboard_data = {
        "timestamp": datetime.now().isoformat(),
        "modules_summary": []
    }
    
    for mod_type, module in BACKEND_MODULES.items():
        try:
            summary = module.get("get_summary", lambda x: {})({
                "DATA_DIR": DATA_DIR,
                "session": dict(session)
            })
            
            dashboard_data["modules_summary"].append({
                "module": mod_type,
                "name": module["name"],
                "summary": summary
            })
        except Exception as e:
            dashboard_data["modules_summary"].append({
                "module": mod_type,
                "name": module["name"],
                "error": str(e)
            })
    
    return jsonify(dashboard_data)

def open_browser():
    """Abre el navegador automáticamente"""
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    print("=" * 60)
    print(" Jocarsa Suite - Sistema de Gestión Empresarial Integrado")
    print("=" * 60)
    print(f"\n📦 Módulos cargados: {len(BACKEND_MODULES)}")
    for mod_name, mod_data in BACKEND_MODULES.items():
        print(f"  {mod_data.get('icon', '📦')} {mod_data['name']}")
    print(f"\n🌐 Abriendo navegador en http://127.0.0.1:5000/")
    print("=" * 60)
    
    Timer(1.0, open_browser).start()
    app.run(debug=True, port=5000)
