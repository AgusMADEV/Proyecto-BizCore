/**
 * Jocarsa Suite - JavaScript principal
 * Gestiona la interacción con los módulos y el dashboard
 */

// Estado de la aplicación
const state = {
    modules: [],
    currentModule: null,
    dashboardData: null
};

// Inicializar aplicación
document.addEventListener("DOMContentLoaded", () => {
    console.log("Jocarsa Suite - Inicializando...");
    
    loadModules();
    loadDashboard();
    
    // Event listener para el botón dashboard
    document.getElementById("btn-dashboard").addEventListener("click", () => {
        showDashboard();
    });
});

/**
 * Carga la lista de módulos disponibles
 */
async function loadModules() {
    try {
        const response = await fetch("/api/modules");
        const data = await response.json();
        
        state.modules = data.modules;
        renderModules();
        
        console.log(`✅ ${state.modules.length} módulos cargados`);
    } catch (error) {
        console.error("Error cargando módulos:", error);
        showError("No se pudieron cargar los módulos");
    }
}

/**
 * Renderiza la lista de módulos en el sidebar
 */
function renderModules() {
    const container = document.getElementById("modules-list");
    
    if (state.modules.length === 0) {
        container.innerHTML = '<div class="loading">No hay módulos disponibles</div>';
        return;
    }
    
    // Agrupar módulos por categoría
    const modulesByCategory = {};
    state.modules.forEach(mod => {
        const category = mod.category || 'general';
        if (!modulesByCategory[category]) {
            modulesByCategory[category] = [];
        }
        modulesByCategory[category].push(mod);
    });
    
    // Renderizar módulos
    let html = '';
    
    for (const [category, modules] of Object.entries(modulesByCategory)) {
        modules.forEach(mod => {
            html += `
                <div class="module-card" data-module="${mod.type}" onclick="selectModule('${mod.type}')">
                    <h3>${mod.icon} ${mod.name}</h3>
                    <p>${mod.description}</p>
                    <div class="module-category">${category}</div>
                </div>
            `;
        });
    }
    
    container.innerHTML = html;
}

/**
 * Selecciona un módulo
 */
async function selectModule(moduleType) {
    console.log(`Seleccionando módulo: ${moduleType}`);
    
    state.currentModule = moduleType;
    
    // Actualizar UI
    document.querySelectorAll('.module-card').forEach(card => {
        card.classList.remove('active');
    });
    
    const selectedCard = document.querySelector(`[data-module="${moduleType}"]`);
    if (selectedCard) {
        selectedCard.classList.add('active');
    }
    
    // Ocultar dashboard, mostrar módulo
    document.getElementById("dashboard-section").classList.remove("active");
    document.getElementById("module-section").classList.add("active");
    
    // Cargar datos del módulo
    await loadModuleData(moduleType);
}

/**
 * Carga los datos de un módulo específico
 */
async function loadModuleData(moduleType) {
    const container = document.getElementById("module-content");
    container.innerHTML = '<div class="loading">Cargando datos del módulo...</div>';
    
    try {
        const response = await fetch(`/api/module/${moduleType}`);
        const result = await response.json();
        
        if (result.ok) {
            renderModuleContent(moduleType, result.data);
        } else {
            showError(result.error || "Error cargando módulo");
        }
    } catch (error) {
        console.error("Error:", error);
        showError("Error de conexión con el servidor");
    }
}

/**
 * Renderiza el contenido de un módulo
 */
function renderModuleContent(moduleType, data) {
    const container = document.getElementById("module-content");
    const module = state.modules.find(m => m.type === moduleType);
    
    let html = `
        <div class="module-content-card">
            <h3>${module.icon} ${module.name}</h3>
            <p>${module.description}</p>
        </div>
    `;
    
    // Renderizar según el tipo de módulo
    if (moduleType === 'crm') {
        html += renderCRMContent(data);
    } else if (moduleType === 'proyectos') {
        html += renderProyectosContent(data);
    } else if (moduleType === 'formularios') {
        html += renderFormulariosContent(data);
    } else if (moduleType === 'informes') {
        html += renderInformesContent(data);
    } else {
        html += `<div class="module-content-card">
            <pre>${JSON.stringify(data, null, 2)}</pre>
        </div>`;
    }
    
    container.innerHTML = html;
}

/**
 * Renderiza el contenido del módulo CRM
 */
function renderCRMContent(data) {
    const clientes = data.clientes || [];
    const oportunidades = data.oportunidades || [];
    
    let html = `
        <div class="module-content-card">
            <h3>👥 Clientes (${clientes.length})</h3>
            <button class="btn" onclick="addCliente()">➕ Nuevo Cliente</button>
            <div style="margin-top: 1rem;">
    `;
    
    if (clientes.length === 0) {
        html += '<p>No hay clientes registrados. Crea el primero para comenzar.</p>';
    } else {
        clientes.forEach(cliente => {
            html += `
                <div style="padding: 1rem; border-bottom: 1px solid #e2e8f0;">
                    <strong>${cliente.nombre}</strong> - ${cliente.empresa}<br>
                    <small>📧 ${cliente.email} | 📱 ${cliente.telefono}</small>
                </div>
            `;
        });
    }
    
    html += `
            </div>
        </div>
        
        <div class="module-content-card">
            <h3>💼 Oportunidades de Venta (${oportunidades.length})</h3>
            <button class="btn" onclick="addOportunidad()">➕ Nueva Oportunidad</button>
            <div style="margin-top: 1rem;">
    `;
    
    if (oportunidades.length === 0) {
        html += '<p>No hay oportunidades registradas.</p>';
    } else {
        oportunidades.forEach(op => {
            const estadoColor = {
                'abierta': '#10b981',
                'en_proceso': '#f59e0b',
                'ganada': '#2563eb',
                'perdida': '#ef4444'
            }[op.estado] || '#64748b';
            
            html += `
                <div style="padding: 1rem; border-bottom: 1px solid #e2e8f0;">
                    <strong>${op.titulo}</strong> - ${op.valor}€<br>
                    <small>Probabilidad: ${op.probabilidad}%</small>
                    <span style="background: ${estadoColor}; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; margin-left: 0.5rem;">${op.estado}</span>
                </div>
            `;
        });
    }
    
    html += '</div></div>';
    
    return html;
}

/**
 * Renderiza el contenido del módulo de Proyectos
 */
function renderProyectosContent(data) {
    const proyectos = data.proyectos || [];
    const tareas = data.tareas || [];
    
    let html = `
        <div class="module-content-card">
            <h3>📋 Proyectos (${proyectos.length})</h3>
            <button class="btn" onclick="addProyecto()">➕ Nuevo Proyecto</button>
            <div style="margin-top: 1rem;">
    `;
    
    if (proyectos.length === 0) {
        html += '<p>No hay proyectos. Crea el primero para comenzar.</p>';
    } else {
        proyectos.forEach(proyecto => {
            const tareasProyecto = tareas.filter(t => t.proyecto_id === proyecto.id).length;
            html += `
                <div style="padding: 1rem; border-bottom: 1px solid #e2e8f0;">
                    <strong>${proyecto.nombre}</strong><br>
                    <small>${proyecto.descripcion}</small><br>
                    <small>📊 Estado: ${proyecto.estado} | 📋 Tareas: ${tareasProyecto}</small>
                </div>
            `;
        });
    }
    
    html += `</div></div>`;
    
    return html;
}

/**
 * Renderiza el contenido del módulo de Formularios
 */
function renderFormulariosContent(data) {
    const formularios = data.formularios || [];
    
    let html = `
        <div class="module-content-card">
            <h3>📝 Formularios (${formularios.length})</h3>
            <button class="btn" onclick="createFormulario()">➕ Nuevo Formulario</button>
            <div style="margin-top: 1rem;">
    `;
    
    if (formularios.length === 0) {
        html += '<p>No hay formularios creados.</p>';
    } else {
        formularios.forEach(form => {
            html += `
                <div style="padding: 1rem; border-bottom: 1px solid #e2e8f0;">
                    <strong>${form.titulo}</strong><br>
                    <small>${form.descripcion}</small><br>
                    <small>📊 Respuestas: ${form.respuestas_count || 0} | Estado: ${form.activo ? '✅ Activo' : '❌ Inactivo'}</small>
                </div>
            `;
        });
    }
    
    html += `</div></div>`;
    
    return html;
}

/**
 * Renderiza el contenido del módulo de Informes
 */
function renderInformesContent(data) {
    const informes = data.informes_generados || [];
    
    let html = `
        <div class="module-content-card">
            <h3>📊 Informes Generados (${informes.length})</h3>
            <div style="display: flex; gap: 1rem; margin: 1rem 0;">
                <button class="btn" onclick="generarInforme('general')">📄 Informe General</button>
                <button class="btn" onclick="generarInforme('ventas')">💰 Informe de Ventas</button>
                <button class="btn" onclick="generarInforme('proyectos')">📋 Informe de Proyectos</button>
                <button class="btn" onclick="generarInforme('integracion')">🔗 Informe de Integración</button>
            </div>
            <div style="margin-top: 1rem;">
    `;
    
    if (informes.length === 0) {
        html += '<p>No hay informes generados. Genera el primero con los botones de arriba.</p>';
    } else {
        informes.slice().reverse().forEach(informe => {
            html += `
                <div style="padding: 1rem; border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 1rem;">
                    <strong>${informe.contenido.tipo}</strong><br>
                    <small>📅 ${new Date(informe.fecha_generacion).toLocaleString('es-ES')}</small>
                    <pre style="background: #f8fafc; padding: 1rem; margin-top: 0.5rem; border-radius: 4px; font-size: 0.85rem;">${JSON.stringify(informe.contenido, null, 2)}</pre>
                </div>
            `;
        });
    }
    
    html += `</div></div>`;
    
    return html;
}

/**
 * Carga los datos del dashboard
 */
async function loadDashboard() {
    try {
        const response = await fetch("/api/dashboard");
        const data = await response.json();
        
        state.dashboardData = data;
        renderDashboard();
        
        console.log("✅ Dashboard cargado");
    } catch (error) {
        console.error("Error cargando dashboard:", error);
    }
}

/**
 * Renderiza el dashboard
 */
function renderDashboard() {
    const container = document.getElementById("dashboard-cards");
    
    if (!state.dashboardData || !state.dashboardData.modules_summary) {
        container.innerHTML = '<div class="loading">No hay datos disponibles</div>';
        return;
    }
    
    let html = '';
    
    state.dashboardData.modules_summary.forEach(modSummary => {
        const module = state.modules.find(m => m.type === modSummary.module);
        if (!module) return;
        
        html += `
            <div class="dashboard-card">
                <h3>${module.icon} ${module.name}</h3>
        `;
        
        // Renderizar estadísticas del módulo
        const summary = modSummary.summary;
        for (const [key, value] of Object.entries(summary)) {
            const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            html += `
                <div class="dashboard-stat">
                    <span class="label">${label}</span>
                    <span class="value">${value}</span>
                </div>
            `;
        }
        
        html += '</div>';
    });
    
    container.innerHTML = html;
}

/**
 * Muestra el dashboard
 */
function showDashboard() {
    document.getElementById("module-section").classList.remove("active");
    document.getElementById("dashboard-section").classList.add("active");
    
    // Desactivar módulo seleccionado
    document.querySelectorAll('.module-card').forEach(card => {
        card.classList.remove('active');
    });
    
    state.currentModule = null;
    
    // Recargar datos del dashboard
    loadDashboard();
}

/**
 * Muestra un error
 */
function showError(message) {
    alert("❌ Error: " + message);
}

// ===== Funciones de acciones de módulos =====

function addCliente() {
    const nombre = prompt("Nombre del cliente:");
    if (!nombre) return;
    
    const email = prompt("Email:");
    const telefono = prompt("Teléfono:");
    const empresa = prompt("Empresa:");
    
    executeModuleAction('crm', 'add_cliente', {
        nombre, email, telefono, empresa
    });
}

function addOportunidad() {
    const titulo = prompt("Título de la oportunidad:");
    if (!titulo) return;
    
    const valor = parseFloat(prompt("Valor estimado (€):") || "0");
    const probabilidad = parseInt(prompt("Probabilidad (0-100):") || "50");
    
    executeModuleAction('crm', 'add_oportunidad', {
        titulo, valor, probabilidad, cliente_id: 1
    });
}

function addProyecto() {
    const nombre = prompt("Nombre del proyecto:");
    if (!nombre) return;
    
    const descripcion = prompt("Descripción:");
    
    executeModuleAction('proyectos', 'add_proyecto', {
        nombre, descripcion
    });
}

function createFormulario() {
    const titulo = prompt("Título del formulario:");
    if (!titulo) return;
    
    const descripcion = prompt("Descripción:");
    
    executeModuleAction('formularios', 'create_formulario', {
        titulo, descripcion,
        campos: [
            {name: "nombre", label: "Nombre", type: "text", required: true},
            {name: "email", label: "Email", type: "email", required: true},
            {name: "comentario", label: "Comentario", type: "textarea", required: false}
        ]
    });
}

async function generarInforme(tipo) {
    await executeModuleAction('informes', 'generar_informe', { tipo });
}

/**
 * Ejecuta una acción en un módulo
 */
async function executeModuleAction(moduleType, action, params) {
    try {
        const response = await fetch(`/api/module/${moduleType}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action, params })
        });
        
        const result = await response.json();
        
        if (result.ok) {
            console.log("✅ Acción ejecutada:", result.result);
            alert("✅ " + (result.result.message || "Acción completada"));
            
            // Recargar datos del módulo actual
            if (state.currentModule === moduleType) {
                loadModuleData(moduleType);
            }
            
            // Recargar dashboard
            loadDashboard();
        } else {
            showError(result.error);
        }
    } catch (error) {
        console.error("Error ejecutando acción:", error);
        showError("Error de conexión");
    }
}
