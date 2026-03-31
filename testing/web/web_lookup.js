const form = document.getElementById("lookup-form");
const resultBox = document.getElementById("result-box");

function normalizeText(value) {
  return String(value ?? "").trim().toLowerCase();
}

function clearResult() {
  resultBox.classList.remove("error");
  resultBox.textContent = "";
}

function showError(message) {
  clearResult();
  resultBox.classList.add("error");
  resultBox.textContent = message;
}

function formatOutputValue(value) {
  if (value === null || value === undefined || value === "") return "(empty)";
  if (typeof value === "object") return JSON.stringify(value, null, 2);
  return String(value);
}

function showValue(value) {
  clearResult();
  resultBox.textContent = formatOutputValue(value);
}

function showList(values) {
  clearResult();
  const list = document.createElement("ul");
  values.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    list.appendChild(li);
  });
  resultBox.appendChild(list);
}

function buildJsonUrl(jsonFileName) {
  const inputName = String(jsonFileName ?? "").trim();
  if (!inputName) throw new Error("JSON file name is required.");
  if (inputName.includes("..")) throw new Error("Invalid file name (contains '..').");
  if (inputName.includes("\\") || inputName.includes("/")) {
    // Only allow a file name, not a path.
    throw new Error("Enter only the file name (no path).");
  }

  // Allow entering the name with or without a .json extension.
  const normalizedName = /\.json$/i.test(inputName) ? inputName : `${inputName}.json`;
  // Encode for safety with spaces/special characters.
  return encodeURIComponent(normalizedName);
}

async function loadJson(jsonFileName) {
  const encodedName = buildJsonUrl(jsonFileName);
  const candidateUrls = [
    `./output/JSON/${encodedName}`,
    `../output/JSON/${encodedName}`,
    `../../output/JSON/${encodedName}`,
    `../../../output/JSON/${encodedName}`,
  ];

  let lastStatus = "unknown";
  for (const url of candidateUrls) {
    const response = await fetch(url);
    if (response.ok) return response.json();
    lastStatus = String(response.status);
  }

  throw new Error(`Could not read the JSON file (${lastStatus})`);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  try {
    const formData = new FormData(form);
    const tableInput = normalizeText(formData.get("table"));
    const parameterInput = normalizeText(formData.get("parameter"));
    const jsonFileName = formData.get("jsonfile");

    showError("Loading JSON...");
    const incidentData = await loadJson(jsonFileName);

    const tables = incidentData.tables || {};
    const tableName = Object.keys(tables).find(
      (name) => normalizeText(name) === tableInput
    );

    if (!tableName) {
      showError("That table does not exist.");
      return;
    }

    const tableData = tables[tableName];

    if (Array.isArray(tableData)) {
      const values = tableData.map((record) => {
        const paramKey = Object.keys(record).find(
          (key) => normalizeText(key) === parameterInput
        );
        const value = paramKey ? String(record[paramKey] ?? "") : "(not found)";
        return value === "" ? "(empty)" : value;
      });

      showList(values);
      return;
    }

    if (typeof tableData === "object" && tableData !== null) {
      const paramKey = Object.keys(tableData).find(
        (key) => normalizeText(key) === parameterInput
      );

      if (!paramKey) {
        showError("That parameter does not exist in this table.");
        return;
      }

      showValue(tableData[paramKey]);
      return;
    }

    showError("Unsupported table format.");
  } catch (error) {
    showError(`${error.message}. Run a local server instead of opening the HTML with file://.`);
  }
});
