from datetime import datetime
from typing import Dict, List
from eml_assess.models.eml import EML
import uuid
import json
import logging

class Report():
    """Report

    This is the base class for all reports. Provides a unique identifier and timestamp.
    """
    def __init__(self, timestamp:datetime=datetime.now()):
        self.report_id = uuid.uuid4()
        self.timestamp = timestamp

    def get_report_id(self)->uuid.UUID:
        """
        Returns the report ID

        :return: uuid.UUID
        """
        return self.report_id
    
    def get_timestamp(self)->datetime:
        """
        Returns the timestamp

        :return: datetime
        """
        return self.timestamp
    
    def __str__(self)->str:
        return f"Generic Report [{self.report_id}] <{self.timestamp.isoformat()}>"

    def to_dict(self,path:str)->Dict:
        return {
            "report_id":str(self.report_id),
            "timestamp": self.timestamp
        }
    def to_file(self, path:str)->None:
        """
        Writes the report to a file.

        :param path: str
        :return: None
        """

        def json_serial(obj):
            if isinstance(obj, datetime):
                serial = obj.isoformat()
                return serial

        # dump to json file
        try:
            with open(path, 'w') as f:
                json.dump(self.to_dict(), f, default=json_serial,indent=4)
        except Exception as e:
            logging.log(msg=f"Error writing report to file: {e}", level=logging.ERROR)

class ServiceReport(Report):
    """ServiceReport

    Report for a Service result. Includes the response, service name, timestamp, execution time, and results from the Service that was run.
    """

    def __init__(self,response:str,service_name:str,service_type:str, timestamp:datetime, exec_time:float, results:Dict):
        super().__init__(timestamp)
        self.response=response
        self.service_name=service_name
        self.service_type=service_type
        self.exec_time=exec_time
        self.results=results

    def __str__(self):
        return f"""Service [{self.service_name}] Report #{self.report_id}: {self.response} at {self.timestamp} with {self.exec_time} seconds."""

    def to_dict(self):
        return {
            "response":self.response,
            "service_name":self.service_name,
            "service_type":self.service_type,
            "report_id":str(self.report_id),
            "timestamp":self.timestamp,
            "exec_time":self.exec_time,
            "results":self.results
        }

class EMLReport(Report):
    """EMLReport
    
    Report for an EML. Contains a list of ServiceReports associated with the EML being run against.
    """

    def __init__(self, eml:EML, service_reports:List[ServiceReport]=[], timestamp:datetime=datetime.now()):
        super().__init__(timestamp)
        self.eml=eml
        self.service_reports=service_reports

    def add_service_report(self,service_report:ServiceReport)->None:
        self.service_reports.append(service_report)

    def __str__(self):
        return f"""EML Report #{self.report_id}: {self.timestamp} with {len(self.service_reports)} child service reports."""

    def to_dict(self):
        return {
            "eml":self.eml.to_dict(),
            "service_reports": [sr.to_dict() for sr in self.service_reports],
            "timestamp": self.timestamp,
            "report_id": str(self.report_id)
        }
    
