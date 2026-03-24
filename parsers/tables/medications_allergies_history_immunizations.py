from .common import extract_medications_allergies_history_immunizations


def parse(table):
    return extract_medications_allergies_history_immunizations(table)
