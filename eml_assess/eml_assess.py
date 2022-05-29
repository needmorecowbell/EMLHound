import os
from typing import Dict, List
from eml_assess.models.eml import EML
import json
from eml_assess.models.reports import EMLReport, ServiceReport
from eml_assess.services.eml_parser import EMLParserService
from eml_assess.config import Config
from eml_assess.services.external import ExternalService
from eml_assess.services.ipinfo import IPInfoService
from eml_assess.sources.local import LocalSource
from eml_assess.vaultman import VaultMan
import logging
class EMLAssess():

    def __init__(self, vman_path:str=None, config_path=None):
        self.sources = []
        self.operators= []

        if(config_path): 
            self.config = Config(config_path)
            self.activate_sources()
        self.config = None

        if(vman_path):
            self.vman = VaultMan(vman_path) # vault manager
        else:
            self.vman = None

    def activate_sources(self):
        """Go through all sources enabled in the config and load them into the EMLAssess object"""

        assert self.config is not None, "Config must be provided"

        for source in self.config.config["sources"]:
            if(source["enabled"]):
                match source["type"]:
                    case "local":
                        self.sources.append(LocalSource(source["path"], source["name"]))

    def scan(self, path:str) -> EMLReport or List[EMLReport]:
        """
        Scans the target directory or file, giving back a report of the findings

        :return: EMLReport or List[EMLReport]
        """
        
        assert os.path.exists(path),"scan error: directory or file path does not exist"

        if(os.path.isdir(path)):
            results = self.scan_directory()
        else:
            eml= EML(path)
            results = self.scan_eml(eml)

        return results


    def scan_eml(self,eml:EML, check_vault:bool=True) -> EMLReport:
        """
        Scans an EML file, giving back an EMLReport of the findings
        
        :param eml_path: Path to the EML file
        :return: EMLReport
        """
        if(self.vman is not None and check_vault):
            if(self.vman.in_vault(eml)):
                logging.log(msg=f'EML {eml.md5} already in vault', level=logging.INFO)
                return self.vman.retrieve_report_from_vault(eml)

        if(self.vman):
            workspace = self.vman.initialize_workspace(eml)
        report= EMLReport(eml, service_reports=[])
        if(self.config):

            # check email with all enabled services
            for service in self.config.config["services"]:
                if(service["enabled"]):
                    # Handle external service types
                    if(service["type"]=="external"):
                        if(service["target"] == "ip"):
                            for ip in eml.get_ip_addresses():
                                sr = self.execute_service(service["type"], ip=ip, service_cfg=service)
                        elif(service["target"] == "eml"):
                            sr = self.execute_service(service["type"], eml=eml, service_cfg=service)
                        else:
                            sr = self.execute_service(service["type"], service_cfg=service)
                    else:
                        # If any other service type, just run it
                        sr = self.execute_service(service["type"], eml=eml)
                    
                    # go back in after each service runs to re-enrich the report, in case a service is dependent on another's information
                    report = self.enrich_eml_report(report, sr)
                    
                    if(self.vman):
                        # Add service report to workspace
                        self.vman.add_service_report_to_workspace(sr,eml)

        else: # scan this report using default services
            sr = self.execute_service("eml_parser",eml=eml)
            report = self.enrich_eml_report(report, sr)

            if(self.vman):
                self.vman.add_service_report_to_workspace(sr,eml)
                logging.log(msg=f"EML {report.eml.md5} service report added to Vault", level=logging.INFO)



        if(self.vman):
            # Save all attachments
            for attachment in report.eml.attachments:
                self.vman.add_attachment_to_workspace(attachment,report.eml)


        #report.add_service_report(self.execute_service("eml_parser", eml=eml)) # parsing must be done first

        # for ip in eml.get_ip_addresses():
        #     print("new ip", ip)
        #     report.add_service_report(self.execute_service("ipinfo_service", ip=ip)) # reports on IOCs should be done last once all IOCs are found
        

        # Save report to file after all enrichment is complete

        return report            
    
    def enrich_eml_report(self, report:EMLReport, service_report:ServiceReport) -> EMLReport:
        """Enriches the base report with additional information gained from Service Reports
        
        :param report: EMLReport object
        :return: EMLReport object
        """
        match service_report.service_type:
            case "eml_parser":
                report = EMLParserService.enrich(report, service_report)

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
                    service = EMLParserService(eml,self.config,self.vman)
                    return service.execute()
                raise Exception("No EML object provided")

            case "ipinfo_service":
                if(ip):
                    service = IPInfoService(ip_address=ip)
                    return service.execute()
                raise Exception("No IP address provided")

            case "external":
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

    @classmethod
    def extract_eml_headers(eml:EML) -> Dict:
        """Extracts the headers from an EML file
        
        :param eml: EML object
        :return: Dict of headers"""
        sr = EMLParserService(eml).execute()
        report=  EMLParserService.enrich(eml,sr)

        return report.eml.get_header()
    

    def scan_directory(self, path:str, recursive=False) -> List[EMLReport]:
        """Scans a directory, giving back a list of EMLReport objects
        
        :param path: Path to the directory
        :param recursive: Whether to scan subdirectories
        :return: List of EMLReport objects"""


        assert os.path.exists(path), "scan error: directory does not exist"

        eml_files = []

        if(recursive):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if(file.endswith(".eml")):
                        eml_path = os.path.join(root, file)
                        eml_files.append(eml_path)
        else:
            # get all files in directory
            for file in os.listdir(path):
                if(os.path.isfile(os.path.join(path,file))):
                    eml_files.append(os.path.join(path,file))
        
        # scan each file
        reports = []
        for fp in eml_files:
            eml = EML(fp, attachments=[])
            report= self.scan_eml(eml)
            reports.append(report)                

        return reports

    