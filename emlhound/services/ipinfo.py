from emlhound.models.reports import ServiceReport
from emlhound.services.service import Service
from datetime import datetime
import requests
import time
import logging

class IPInfoService(Service):
    """Service to get IP information from a given IP address"""
    def __init__(self, ip_address:str, name:str="IPInfo Service"):
        super().__init__("IPInfo")
        self.ip_address = ip_address
        self.results = {}
        self.service_type="ipinfo"


    def execute(self) -> ServiceReport:
        """Executes the service, returning a ServiceReport Object"""

        start= time.time()
        
        try:
            r = requests.get(f"https://ipinfo.io/{self.ip_address}/json")
            self.results = r.json()
            response="success"
        except Exception as e:
            logging.log(msg=e)
            response="failure"
        finally:
            elapsed= time.time() - start
            return ServiceReport(response=response,
                                 service_name=self.name,
                                 timestamp=datetime.now(),
                                 exec_time=elapsed,
                                 results=self.results)


