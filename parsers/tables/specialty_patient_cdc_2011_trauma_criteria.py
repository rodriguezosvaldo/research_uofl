from ..variables import variables_to_extract
from .common import extract_type_1_by_variables


def parse(table):
    return extract_type_1_by_variables(table, variables_to_extract["Specialty Patient - CDC 2011 Trauma Criteria"])
