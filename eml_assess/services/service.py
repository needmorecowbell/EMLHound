from datetime import datetime
import time
from eml_assess.models.eml import EML
from eml_assess.models.reports import ServiceReport

class Service():
    """Base Service Class"""
    def __init__(self, name:str="Unnamed Service"):
        self.name=name
        self.service_type="base_service"

    def execute(self) -> ServiceReport:
        """Runs the service, returning a ServiceReport Object
        
        :return: ServiceReport
        """

        results = {}

        start = time.time()
        # handle service execution

        # results = self.get_report_findings()

        # end when results have been obtained
        elapsed = time.time() - start


        return ServiceReport( response = "success",
                              service_name = self.name,
                              timestamp = datetime.now(),
                              exec_time = elapsed,
                              results = results)
        