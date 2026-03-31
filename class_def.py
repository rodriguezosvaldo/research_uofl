from dataclasses import dataclass, field

@dataclass
class Incident:
    incident_number: str
    incident_date: str
    tables: dict = field(default_factory=dict)
    
    def add_table(self, table_name: str, data: dict):
        self.tables[table_name] = data



        
    
    
