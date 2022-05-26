from typing import Dict
from eml_assess.models.eml import EML
from eml_assess.services.service import Service
import subprocess
import time
from datetime import datetime
from eml_assess.models.reports import ServiceReport
import json 

class ExternalService(Service):
    """Generic Service for Running External System Commands"""
    def __init__(self, name:str,command:str, schedule:str, ip:str=None, eml:EML=None):
        super().__init__(name)
        self.command=command
        self.service_type="external"
        self.schedule=schedule
        self.eml=eml
        self.ip=ip

        self.command =self._parse_command()

    def _parse_command(self):
        """Parses the command string to replace variables with values from the EML
        
        :return: str
        """
        if(self.ip):
            return self.command.format(ip=self.ip)
        if(self.eml):
            return self.command.format(**self.eml.to_dict())
        
        # for commands that need no input/context of an email return the command
        return self.command


    def execute(self) -> ServiceReport:
        """Runs the service using a subprocess shell call, returning output in a ServiceReport Object
        
        :return: ServiceReport
        """

        start=time.time()
        # handle service execution
        try:
            output = subprocess.check_output(self.command.split(" ")).decode('utf-8')
            results= json.loads(output)

        except Exception as e:
            print(e)

        elapsed = time.time() - start

        return ServiceReport( response = "success",
                              service_name = self.name, 
                              timestamp = datetime.now(),
                              exec_time = elapsed,
                              results = results)


