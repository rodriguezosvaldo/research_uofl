# UofL Research Project

Proyecto para extraer informacion estructurada desde reportes PDF de incidentes, guardarla en JSON y consolidarla en un archivo Excel.

## Requisitos

- Python 3.10+ (recomendado 3.11 o 3.12)
- Dependencias en `requirements.txt`

Instalacion:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Estructura del proyecto

- `pdfs/`: PDFs de entrada
- `output/JSON/`: salida intermedia en JSON (un archivo por PDF)
- `raw_csv/`: salida alternativa en CSV crudo
- `save_JSON_format.py`: procesa todos los PDFs y genera JSONs estructurados
- `save_raw_csv.py`: extrae tablas en formato CSV crudo
- `dataframe.py`: toma los JSONs y genera `output/output.xlsx`
- `parsers/`: logica de parseo por seccion/tablas

## Flujo recomendado

1. Copia los PDFs a `pdfs/`.
2. Genera JSONs estructurados:

   ```bash
   python save_JSON_format.py
   ```

3. Genera Excel final:

   ```bash
   python dataframe.py
   ```

Resultado esperado:

- JSONs en `output/JSON/`
- Excel consolidado en `output/output.xlsx`

## Flujo alterno (CSV crudo)

Si necesitas una exportacion sin estructura semantica:

```bash
python save_raw_csv.py
```

Salida:

- CSVs en `raw_csv/`

## Notas

- El script `save_JSON_format.py` procesa todos los `.pdf` en `pdfs/`.
- Si `dataframe.py` no encuentra JSONs, mostrara un mensaje indicando que primero ejecutes `save_JSON_format.py`.
