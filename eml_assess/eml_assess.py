import os
from typing import Dict, List

from eml_assess.models.eml import EML
import json

from eml_assess.models.reports import EMLReport, ServiceReport
from eml_assess.services.eml_parser import EMLParserService
from eml_assess.services.external import ExternalService
from eml_assess.services.ipinfo import IPInfoService

class EMLAssess():

    def __init__(self,target:str, is_directory:bool=False, recursive:bool=False, config_path=None):
        self.target = target
        self.is_directory = is_directory
        self.recursive = recursive

        if(config_path): 
            self.config = self.parse_config(config_path)
        else:
            self.config = self.parse_config("config.json")


    def parse_config(self,cfg_path) ->Dict:
        """
        Parses the config file
        
        :param cfg_path: Path to the config file
        :return: Dict of config values
        """
        try:
            with open(cfg_path) as f:
                config = json.load(f)
            
            return config
        except Exception as e:
            print("Error loading config file: ", e)
            return {}

    def scan(self) -> EMLReport or List[EMLReport]:
        """
        Scans the target directory or file, giving back a report of the findings

        :return: EMLReport or List[EMLReport]
        """
        if(self.is_directory):
            results = self.scan_directory()
        else:
            results = self.scan_eml()

        return results

    def scan_eml(self,eml_path:str=None) -> EMLReport:
        """
        Scans an EML file, giving back a report of the findings
        
        :param eml_path: Path to the EML file
        :return: EMLReport
        """
        if(eml_path is None):
            eml_path = self.target

        eml = EML(eml_path)

        report= EMLReport(eml)

        # check email with all enabled services
        for service in self.config["services"]:
            # Handle external service types
            if(service["type"]=="external"):
                if(service["target"] =="ip"):
                    for ip in eml.get_ip_addresses():
                        report.add_service_report(self.execute_service(service["type"], ip=ip, service_cfg=service))
                elif(service["target"] == "eml"):
                    report.add_service_report(self.execute_service(service["type"], eml=eml, service_cfg=service))
                else:
                    report.add_service_report(self.execute_service(service["type"], service_cfg=service))
            else:
                # If any other service type, just run it
                report.add_service_report(self.execute_service(service["type"], eml=eml))
        

        #report.add_service_report(self.execute_service("eml_parser", eml=eml)) # parsing must be done first

        # for ip in eml.get_ip_addresses():
        #     print("new ip", ip)
        #     report.add_service_report(self.execute_service("ipinfo_service", ip=ip)) # reports on IOCs should be done last once all IOCs are found
        
        return report            
    
    def execute_service(self, service_type:str, ip:str = None,  eml:EML=None, service_cfg:dict=None)->ServiceReport:    
        """Executes a service, returning a ServiceReport object
        
        :param eml: EML object
        :param service_type: string handle of the service
        :return: ServiceReport object
        """  

        match service_type:
            case "eml_parser":
                if(eml):
                    service = EMLParserService(eml)
                    return service.execute()
                raise Exception("No EML object provided")

            case "ipinfo_service":
                if(ip):
                    service = IPInfoService(ip_address=ip)
                    return service.execute()
                raise Exception("No IP address provided")

            case "external":
                print(service_cfg)
                if(service_cfg):
                    if (ip):
                        service = ExternalService(service_cfg["name"], service_cfg["command"],service_cfg["schedule"], ip=ip )
                    elif(eml):
                        service = ExternalService(service_cfg["name"], service_cfg["command"],service_cfg["schedule"],eml=eml)
                    else:
                        service = ExternalService(service_cfg["name"], service_cfg["command"],service_cfg["schedule"])
                    
                    return service.execute()
                else:
                    raise Exception("No External Service config provided")

            case "header_analysis":
                # perform header analysis
                pass
            case "attachment_analysis":
                pass
            case "sandbox_analysis":
                pass
            case "attachment_ocr":
                pass
                    
        raise Exception(f"Service Type '{service_type}' not found")


    def extract_eml_headers(self, eml:EML) -> Dict:
        """Extracts the headers from an EML file
        
        :param eml: EML object
        :return: Dict of headers"""

        return {}

    def scan_directory(self, target=None, recursive=None) -> List[EMLReport]:
        """Scans a directory, giving back a list of EMLReport objects
        
        :param path: Path to the directory
        :param recursive: Whether to scan subdirectories
        :return: List of EMLReport objects"""

        if recursive is None:
            recursive = self.recursive
        if target is None:
            target=self.target

        eml_files = []
        if(recursive):
            for root, dirs, files in os.walk(target):
                for file in files:
                    if(file.endswith(".eml")):
                        eml_path = os.path.join(root, file)
                        eml_files.append(eml_path)
        else:
            # get all files in directory
            for file in os.listdir(target):
                if(os.path.isfile(os.path.join(target,file))):
                    eml_files.append(os.path.join(target,file))
        
        # scan each file
        reports = []
        for fp in eml_files:
            reports.append(self.scan_eml(fp))
        
        return reports

    