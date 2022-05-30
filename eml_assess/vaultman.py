from eml_assess.config import Config
import os
from eml_assess.models.eml import EML
from eml_assess.models.eml_attachment import EMLAttachment

from eml_assess.models.reports import EMLReport, ServiceReport
import json
import shutil
import logging

class VaultMan():
    """Vault Manager
    
    This class is responsible for managing input and output to the EML vault."""
    def __init__(self, vault_path:str):
        self.path = vault_path
    
    def in_vault(self,eml:EML)->bool:
        """
        Checks if the eml file is in the vault
        """
        return os.path.exists(f"{self.path}/{eml.md5}")
        
    def initialize_workspace(self, eml:EML, delete_original:bool=False) -> str:
        """ Initializes a new workspace in the vault for the given EML file

        :param eml: EML file to be stored in the vault
        :return: Path to the new workspace
        """
        
        workspace_path = f"{self.path}/{eml.md5}"

        
        if(not os.path.exists(workspace_path)):
            os.mkdir(workspace_path)
            os.mkdir(workspace_path+"/attachments")
            os.mkdir(workspace_path+"/service_reports")
            shutil.copy(eml.path,workspace_path+"/"+eml.md5)

            if(delete_original):
                os.remove(eml.path)
        else:
            logging.log(msg=f"workspace for {eml.md5} exists", level=logging.WARNING)
            
        return workspace_path
    
    def add_service_report_to_workspace(self, sr:ServiceReport, eml:EML)->None:
        workspace= f"{self.path}/{eml.md5}"
        sr.to_file(f"{workspace}/service_reports/{sr.service_name}_report.json")

    def add_eml_report_to_workspace(self, eml_report:EMLReport)->None:
        workspace= f"{self.path}/{eml_report.eml.md5}"
        eml_report.to_file(f"{workspace}/report.json")


    def add_attachment_to_workspace(self,attachment:EMLAttachment, eml:EML)->None:
        workspace= f"{self.path}/{eml.md5}"
        attachment.to_file(f"{workspace}/attachments/{attachment.hashes['md5']}")


    def retrieve_report_from_vault(self,eml)->EMLReport:
        """
        Retrieves the EMLReport from the vault
        """
        try:
            with open(f"{self.path}/{eml.md5}/report.json") as f:
                report = json.load(f)

                attachments = []

                for attachment in report["eml"]["attachments"]:
                    emla = EMLAttachment(file_type=attachment["file_type"],
                                        file_size=attachment["file_size"],
                                        file_extension=attachment["file_extension"],
                                        mime_type=attachment["mime_type"],
                                        mime_type_short=attachment["mime_type_short"],
                                        hashes=attachment["hashes"])
                    attachments.append(emla)

                report_eml = EML(report["eml"]["path"],
                                 ip_addresses=report["eml"]["ip_addresses"],
                                 header=report["eml"]["header"],
                                 body=report["eml"]["body"],
                                 attachments=attachments)
                
                service_reports= []
                for sr in report["service_reports"]:
                    service_reports.append(
                        ServiceReport(sr["response"], sr["service_name"],
                                      sr["service_type"], sr["timestamp"],
                                      sr["exec_time"], sr["results"])
                    )
                return EMLReport(report_eml,service_reports=service_reports, timestamp=report["timestamp"])
        except Exception as e:
            logging.log(msg=str(e), level=logging.ERROR)
            return None
        
