from datetime import datetime
import time
from emlhound.config import Config
from emlhound.models.eml import EML
from emlhound.models.reports import EMLReport, ServiceReport
from emlhound.vaultman import VaultMan
class Service():
    """Base Service Class"""
    def __init__(self, config:Config=None, vman:VaultMan=None, name:str="Unnamed Service"):
        self.name=name
        self.config = config
        self.vman = vman
        self.service_type="base_service"

    def enrich(self, report:EMLReport, service_report:ServiceReport )-> EMLReport:
        """Enriches the base EML report with additional information gained from Service Reports
        
        :param report: EMLReport
        :param service_report: ServiceReport
        :return: EMLReport"""
        return report

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
                              service_type = self.service_type,
                              timestamp = datetime.now(),
                              exec_time = elapsed,
                              results = results)
        