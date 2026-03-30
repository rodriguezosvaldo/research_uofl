const form = document.getElementById("lookup-form");
const resultBox = document.getElementById("result-box");

function normalizeIncident(rawIncident) {
  if (!rawIncident) return "";
  return rawIncident.replace(/^Incident\s*#:\s*/i, "").trim();
}

function normalizeText(value) {
  return String(value ?? "").trim().toLowerCase();
}

async function loadData() {
  const response = await fetch(DATA_FILE);
  if (!response.ok) {
    throw new Error(`No se pudo leer el archivo JSON (${response.status})`);
  }
  incidentData = await response.json();
}

function clearResult() {
  resultBox.classList.remove("error");
  resultBox.textContent = "";
}

function showError(message) {
  clearResult();
  resultBox.classList.add("error");
  resultBox.textContent = `Result: ${message}`;
}

function showValue(value) {
  clearResult();
  resultBox.textContent = `Result: ${value === "" ? "(vacío)" : value}`;
}

function showList(values) {
  clearResult();
  const title = document.createElement("div");
  title.textContent = "Result:";
  resultBox.appendChild(title);

  const list = document.createElement("ul");
  values.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    list.appendChild(li);
  });
  resultBox.appendChild(list);
}

function buildJsonUrl(jsonFileName) {
  const name = String(jsonFileName ?? "").trim();
  if (!name) throw new Error("Falta el nombre del archivo JSON.");
  if (name.includes("..")) throw new Error("Nombre de archivo inválido (contiene '..').");
  if (name.includes("\\") || name.includes("/")) {
    // Solo permitimos nombre de archivo, no rutas.
    throw new Error("Ingresa solo el nombre del archivo (sin ruta).");
  }
  if (!/\.json$/i.test(name)) throw new Error("El archivo debe terminar en .json");
  // Encode por seguridad para espacios y caracteres especiales.
  return `./JSON/${encodeURIComponent(name)}`;
}

async function loadJson(jsonFileName) {
  const url = buildJsonUrl(jsonFileName);
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`No se pudo leer el JSON (${response.status})`);
  }
  return response.json();
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  try {
    const formData = new FormData(form);
    const incidentInput = normalizeIncident(formData.get("incident"));
    const tableInput = normalizeText(formData.get("table"));
    const parameterInput = normalizeText(formData.get("parameter"));
    const jsonFileName = formData.get("jsonfile");

    showError("Cargando JSON...");
    const incidentData = await loadJson(jsonFileName);

    const fileIncident = normalizeIncident(incidentData.incident_number);
    if (incidentInput !== fileIncident) {
      showError(
        `Incident # no encontrado. El archivo ${String(jsonFileName).trim()} contiene: ${fileIncident}`
      );
      return;
    }

    const tables = incidentData.tables || {};
    const tableName = Object.keys(tables).find(
      (name) => normalizeText(name) === tableInput
    );

    if (!tableName) {
      showError("No existe esa tabla.");
      return;
    }

    const tableData = tables[tableName];

    if (Array.isArray(tableData)) {
      const values = tableData.map((record, idx) => {
        const paramKey = Object.keys(record).find(
          (key) => normalizeText(key) === parameterInput
        );
        const value = paramKey ? String(record[paramKey] ?? "") : "(no existe)";
        return `Record ${idx + 1}: ${value === "" ? "(vacío)" : value}`;
      });

      showList(values);
      return;
    }

    if (typeof tableData === "object" && tableData !== null) {
      const paramKey = Object.keys(tableData).find(
        (key) => normalizeText(key) === parameterInput
      );

      if (!paramKey) {
        showError("No existe ese parámetro dentro de la tabla.");
        return;
      }

      showValue(String(tableData[paramKey] ?? ""));
      return;
    }

    showError("Formato de tabla no soportado.");
  } catch (error) {
    showError(`${error.message}. Ejecuta un servidor local en lugar de abrir el HTML con file://.`);
  }
});
