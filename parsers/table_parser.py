from .tables.assessments import parse as parse_assessments
from .tables.consumables import parse as parse_consumables
from .tables.ecg import parse as parse_ecg
from .tables.flow_chart import parse as parse_flow_chart
from .tables.incident_details import parse as parse_incident_details
from .tables.insurance_details import parse as parse_insurance_details
from .tables.medications_allergies_history_immunizations import parse as parse_medications_allergies_history_immunizations
from .tables.mileage import parse as parse_mileage
from .tables.narrative import parse as parse_narrative
from .tables.patient_information import parse as parse_patient_information
from .tables.patient_refusal import parse as parse_patient_refusal
from .tables.patient_transport_details import parse as parse_patient_transport_details
from .tables.specialty_patient_advanced_airway import parse as parse_specialty_patient_advanced_airway
from .tables.specialty_patient_cdc_2011_trauma_criteria import parse as parse_specialty_patient_cdc_2011_trauma_criteria
from .tables.specialty_patient_cpr import parse as parse_specialty_patient_cpr
from .tables.specialty_patient_motor_vehicle_collision import parse as parse_specialty_patient_motor_vehicle_collision
from .tables.specialty_patient_spinal_immobilization import parse as parse_specialty_patient_spinal_immobilization
from .tables.specialty_patient_trauma_criteria import parse as parse_specialty_patient_trauma_criteria
from .tables.transfer_details import parse as parse_transfer_details
from .tables.vital_signs import parse as parse_vital_signs
from .tables.vitals_calculations import parse as parse_vitals_calculations


def table_to_dict(table_name, table):
    # Converts a table into a dictionary using a parser file per table.
    parser_by_table = {
        "Patient Information": parse_patient_information,
        "Medications/Allergies/History/Immunizations": parse_medications_allergies_history_immunizations,
        "Specialty Patient - CPR": parse_specialty_patient_cpr,
        "Incident Details": parse_incident_details,
        "Insurance Details": parse_insurance_details,
        "Mileage": parse_mileage,
        "Specialty Patient - Motor Vehicle Collision": parse_specialty_patient_motor_vehicle_collision,
        "Specialty Patient - Trauma Criteria": parse_specialty_patient_trauma_criteria,
        "Specialty Patient - CDC 2011 Trauma Criteria": parse_specialty_patient_cdc_2011_trauma_criteria,
        "Transfer Details": parse_transfer_details,
        "Patient Transport Details": parse_patient_transport_details,
        "Patient Refusal": parse_patient_refusal,
        "Vital Signs": parse_vital_signs,
        "Vitals Calculations": parse_vitals_calculations,
        "Flow Chart": parse_flow_chart,
        "ECG": parse_ecg,
        "Specialty Patient - Advanced Airway": parse_specialty_patient_advanced_airway,
        "Specialty Patient - Spinal Immobilization": parse_specialty_patient_spinal_immobilization,
        "Assessments": parse_assessments,
        "Narrative": parse_narrative,
        "Consumables": parse_consumables,
    }

    parser = parser_by_table.get(table_name)
    if not parser:
        return {table_name: {}}

    return {table_name: parser(table)}

