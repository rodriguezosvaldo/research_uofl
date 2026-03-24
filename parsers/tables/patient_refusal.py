from ..variables import variables_to_extract
from .common import normalize_label


def parse(table):
    """
    Layout típico: filas con pares (Signed By, nombre) (Signed On, fecha) …
    Solo extraemos el valor asociado a "Signed By".
    """
    target = variables_to_extract["Patient Refusal"][0]  # "Signed By"
    target_norm = normalize_label(target)
    result = {target: ""}

    for row in table[1:]:  # Saltar fila de título "Patient Refusal"
        if not row:
            continue

        for idx in range(0, len(row) - 1, 2):
            key_text = str(row[idx] or "").strip()
            value_text = " ".join(str(row[idx + 1] or "").split())

            if normalize_label(key_text) == target_norm:
                result[target] = value_text
                return result

    return result
