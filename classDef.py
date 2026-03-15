from dataclasses import dataclass, field

# Classes' types:
# Type 1: Classes representing tables with the form: <key>: <value> (e.g. Patient Information (last:Doe))
# Type 2: Classes representing tables registering different records in time (e.g. Tables: Vital Signs, Vitals Calculations, Flow Chart, etc.)
# Type 3: Class representing the Assessments tables

# Type 1 classes:
@dataclass
class PatientInformation:
    last: str
    first: str
    middle: str
    name_suffix: str
    sex: str
    gender: str
    dob: str
    age: str
    weight: str
    height: str
    pedi_color: str
    ssn: str
    advance_directives: str
    resident_status: str
    patient_resides_in_service_area: str
    temporary_residence_type: str
    address: str
    address_2: str
    city: str
    state: str
    zip_code: str
    country: str
    tel: str
    physician: str
    phys_tel: str
    ethnicity: str
    race: str

@dataclass
class ClinicalImpression:
    primary_impression: str = ""
    secondary_impression: str = ""
    protocols_used: str = ""
    local_protocol_provided: str = ""
    care_level: str = ""
    anatomic_position: str = ""
    onset_time: str = ""
    last_known_well: str = ""
    chief_complaint: str = ""
    duration: str = ""
    duration_units: str = ""
    secondary_complaint: str = ""
    secondary_duration: str = ""
    secondary_duration_units: str = ""
    patient_level_of_distress: str = ""
    signs_symptoms: str = ""
    injury: str = ""
    additional_injury: str = ""
    mechanism_of_injury: str = ""
    medical_trauma: str = ""
    barriers_of_care: str = ""
    alcohol_drugs: str = ""
    pregnancy: str = ""
    initial_patient_acuity: str = ""
    final_patient_acuity: str = ""
    patient_activity: str = ""

@dataclass
class MedicationsAllergiesHistoryImmunizations:
    medications: str = ""
    allergies: str = ""
    history: str = ""
    immunizations: str = ""
    last_oral_intake: str = ""

@dataclass
class Narrative:
    narrative: str = ""

@dataclass
class SpecialtyPatientAdvancedAirway:
    airway: str = ""
    indications: str = ""
    monitoring_devices: str = ""
    rescue_devices: str = ""
    reasons_failed_intubation: str = ""

@dataclass
class SpecialtyPatientCPR:
    cardiac_arrest: str = ""
    cardiac_arrest_etiology: str = ""
    estimated_time_of_arrest: str = ""
    est_time_collapse_to_911: str = ""
    est_time_collapse_to_cpr: str = ""
    arrest_witnessed_by: str = ""
    cpr_initiated_by: str = ""
    time_1st_cpr: str = ""
    cpr_feedback: str = ""
    itd_used: str = ""
    applied_aed: str = ""
    applied_by: str = ""
    defibrillated: str = ""
    cpr_type: str = ""
    prearrival_cpr_instructions: str = ""
    first_defibrillated_by: str = ""
    time_of_first_defib: str = ""
    initial_ecg_rhythm: str = ""
    rhythm_at_destination: str = ""
    hypothermia: str = ""
    end_of_event: str = ""
    rosc: str = ""
    rosc_time: str = ""
    rosc_occurred: str = ""
    resuscitation_discontinued: str = ""
    discontinued_reason: str = ""
    resuscitation: str = ""
    in_field_pronouncement_expired: str = ""
    in_field_pronouncement_time: str = ""
    in_field_pronouncement_date: str = ""
    in_field_pronouncement_physician: str = ""

@dataclass
class IncidentDetails:
    location_type: str = ""
    location: str = ""
    address: str = ""
    address_2: str = ""
    mile_marker: str = ""
    city: str = ""
    county: str = ""
    state: str = ""
    zip: str = ""
    country: str = ""
    medic_unit: str = ""
    medic_vehicle: str = ""
    run_type: str = ""
    response_mode: str = ""
    response_mode_descriptors: str = ""
    shift: str = ""
    zone: str = ""
    level_of_service: str = ""
    emd_complaint: str = ""
    emd_card_number: str = ""
    dispatch_priority: str = ""

@dataclass
class DestinationDetails:
    disposition: str = ""
    unit_disposition: str = ""
    patient_evaluation_care_disposition: str = ""
    crew_disposition: str = ""
    transport_disposition: str = ""
    transport_mode: str = ""
    reason_for_refusal_or_release: str = ""
    transport_mode_descriptors: str = ""
    transport_due_to: str = ""
    transported_to: str = ""
    requested_by: str = ""
    transferred_to: str = ""
    transferred_unit: str = ""
    destination: str = ""
    department: str = ""
    address: str = ""
    address_2: str = ""
    city: str = ""
    county: str = ""
    state: str = ""
    zip: str = ""
    country: str = ""
    zone: str = ""
    condition_at_destination: str = ""
    state_wristband: str = ""
    destination_record: str = ""
    trauma_registry_id: str = ""
    stemi_registry_id: str = ""
    stroke_registry_id: str = ""

@dataclass
class IncidentTimes:
    psap_call: str = ""
    dispatch_notified: str = ""
    call_received: str = ""
    dispatched: str = ""
    end_route: str = ""
    staged: str = ""
    resp_on_scene: str = ""
    on_scene: str = ""
    at_patient: str = ""
    care_transferred: str = ""
    depart_scene: str = ""
    at_destination: str = ""
    pt_transferred: str = ""
    call_closed: str = ""
    in_district: str = ""
    at_landing_area: str = ""

@dataclass
class InsuranceDetails:
    insured_name: str = ""
    relationship: str = ""
    insured_ssn: str = ""
    insured_dob: str = ""
    address1: str = ""
    address2: str = ""
    address3: str = ""
    city: str = ""
    state: str = ""
    zip: str = ""
    country: str = ""
    primary_payer: str = ""
    medicare: str = ""
    medicaid: str = ""
    primary_insurance: str = ""
    policy_number: str = ""
    primary_insurance_group_name: str = ""
    group_number: str = ""
    secondary_ins: str = ""
    secondary_policy_number: str = ""
    secondary_insurance_group_name: str = ""
    group_number: str = ""
    dispatch_nature: str = ""
    response_urgency: str = ""
    job_related_injury: str = ""
    employer: str = ""
    contact: str = ""
    phone: str = ""
    mileage_to_closest_hospital: str = ""

@dataclass
class Mileage:
    scene: str = ""
    destination: str = ""
    loaded_miles: str = ""
    start: str = ""
    end: str = ""
    total_miles: str = ""

@dataclass
class Delays:
    dispatch_delays: str = ""
    response_delays: str = ""
    scene_delays: str = ""
    turn_around_delays: str = ""

@dataclass
class Additional:
    additional_agencies: str = ""

# Type 2 classes:
@dataclass
class VitalSigns:
    time: str = ""
    avpu: str = ""
    side: str = ""
    pos: str = ""
    bp: str = ""
    pulse: str = ""
    rr: str = ""
    spo2: str = ""
    etco2: str = ""
    co: str = ""
    bg: str = ""
    temp: str = ""
    pain: str = ""

@dataclass
class VitalsCalculations:
    time: str = ""
    gcs_qualifiers: str = ""
    rass: str = ""
    bars: str = ""
    rts: str = ""
    pts: str = ""
    map: str = ""
    shock_index: str = ""

@dataclass
class FlowChart:
    time: str = ""
    treatment: str = ""
    description: str = ""
    provider: str = ""

# Type 3 class:
@dataclass
class Assessments:
    time: str = ""
    category: str = ""
    category_comments: str = ""
    subcategory: str = ""
    subcategory_comments: str = ""
    subcategory_comments_status: str = "" # "X" or "✓"

@dataclass
class Incident:
    incident_number: str = ""
    incident_date: str = ""
    # Type 1 - single record per section
    patient_information: PatientInformation | None = None
    clinical_impression: ClinicalImpression | None = None
    medications_allergies_history_immunizations: MedicationsAllergiesHistoryImmunizations | None = None
    narrative: Narrative | None = None
    specialty_patient_advanced_airway: SpecialtyPatientAdvancedAirway | None = None
    specialty_patient_cpr: SpecialtyPatientCPR | None = None
    incident_details: IncidentDetails | None = None
    destination_details: DestinationDetails | None = None
    incident_times: IncidentTimes | None = None
    insurance_details: InsuranceDetails | None = None
    mileage: Mileage | None = None
    delays: Delays | None = None
    additional: Additional | None = None
    # Type 2 - lists of time-based records
    vital_signs: list[VitalSigns] = field(default_factory=list)
    vitals_calculations: list[VitalsCalculations] = field(default_factory=list)
    flow_chart: list[FlowChart] = field(default_factory=list)
    # Type 3 - assessments list
    assessments: list[Assessments] = field(default_factory=list)




        
    
    
