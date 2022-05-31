from typing import List
from emlhound.config import Config
import os
from emlhound.models.eml import EML
from emlhound.models.eml_attachment import EMLAttachment

from emlhound.models.reports import EMLReport, ServiceReport
import json
import shutil
import logging


class VaultMan():
    """Vault Manager
    
    This class is responsible for managing input and output to the EML vault.
    """

    def __init__(self, vault_path:str):
        self.path = vault_path
        self.stats = self.refresh_stats()
        self.refresh_stats()


    def refresh_stats(self)->dict:
        """
        Gets statistics about the vault

        :return: Dictionary with statistics about vault
        """
        stats = {}
        stats["vault_size"] = self.human_readable_bytes(self.get_size(self.path))
        stats["emails_in_vault"] = len(os.listdir(self.path))
        #stats["vault_attachments"] = len([self.get_attachments_from_workspace(eml_md5) for eml_md5 in os.listdir(self.path)])
        
        return stats


    def get_all_attachments_with_mimetype(self,mimetype_short:str)->List[EMLAttachment]:
        """
        Returns a list of all attachments in the vault with the given mimetype

        :param mimetype_short: Short mimetype
        :return: List of EMLAttachment objects
        """

        results = []

        for eml_hash in  self.get_eml_hashes():
            attachments = self.get_attachments_from_workspace(eml_hash)
            for attachment in attachments:
                if(attachment.mime_type_short == mimetype_short):
                    results.append(attachment)
                
        return results

    def get_eml_hashes(self)->list:
        return os.listdir(self.path)
    
    def get_size(self, path:str)->int:
        """
        Returns the size in bytes of directory (sum of contents) or file at the given path

        :param path: Path to the directory or file
        :return: Size in bytes
        """

        if(os.path.isdir(path)):
            sum = 0
            for dir,_,files in os.walk(path):
                for file in files:
                    sum += os.path.getsize(f"{dir}/{file}")
            return sum
        else:
            return os.stat(path).st_size

    
    def human_readable_bytes(self,bytes):
        suffixes = ['B', 'K', 'M', 'G', 'T', 'P']

        i = 0
        while (bytes >= 1024 and i < len(suffixes)-1):
            bytes /= 1024.
            i += 1
        
        f = ('%.2f' % bytes).rstrip('0').rstrip('.')
        return '%s %s' % (f, suffixes[i])


    def in_vault(self,eml:EML)->bool:
        """
        Checks if the eml file is in the vault

        :param eml: EML file to be checked
        :return: True if the file is in the vault, False otherwise
        """
        return os.path.exists(f"{self.path}/{eml.md5}")
    
    def get_path_from_hash(self,md5:str)->str:
        """
        Finds the path for a given hash

        :param md5: string MD5 hash of the workspace
        """
        for dir,_,files in os.walk(self.path):
            for file in files:
                if(file == md5):
                    return f"{self.path}/{dir}/{file}"

    def get_attachments_from_workspace(self, eml_md5:str)->list:
        """
        Returns a list of all workspace paths with attachments

        :param eml_md5: string MD5 hash of the EML file
        :return: List of paths to attachments
        """

        if(eml_md5 in os.listdir(self.path)):
            report = self.retrieve_report_from_vault(eml_md5=eml_md5)
            return report.eml.attachments

        else:
            logging.INFO(f"{eml_md5} not found in vault")
            return []
        
    
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
                logging.info("Deleting original EML file"+str(eml.path))
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


    def delete_workspace(self, eml_md5:str)->None:
        """
        Deletes the workspace with the given MD5 hash

        :param eml_md5: MD5 hash of the workspace
        """
        workspace = f"{self.path}/{eml_md5}"

        if(os.path.exists(workspace)):
            shutil.rmtree(workspace)
        else:
            logging.log(msg=f"Failed to delete workspace: {workspace} does not exist", level=logging.WARNING)
            raise Exception(f"Failed to delete workspace: {workspace} does not exist")


    def retrieve_report_from_vault(self,eml_md5:str)->EMLReport:
        """
        Retrieves the EMLReport from the vault

        :param eml_md5: MD5 hash of the EML file
        :return: EMLReport object
        """

        try:
            with open(f"{self.path}/{eml_md5}/report.json") as f:
                report = json.load(f)

                logging.info("Retrieved report file from vault")

                attachments = []

                for attachment in report["eml"]["attachments"]:
                    emla = EMLAttachment(file_type=attachment["file_type"],
                                        file_size=attachment["file_size"],
                                        file_extension=attachment["file_extension"],
                                        mime_type=attachment["mime_type"],
                                        mime_type_short=attachment["mime_type_short"],
                                        hashes=attachment["hashes"])
                    attachments.append(emla)
                
                logging.info("Got all attachments from report file")

                path = report["eml"].get("path")
                if(path is None):
                    path= f'{self.path}/{eml_md5}/{eml_md5}'


                report_eml = EML(path,
                                 ip_addresses=report["eml"]["ip_addresses"],
                                 header=report["eml"]["header"],
                                 body=report["eml"]["body"],
                                 attachments=attachments)
                
                logging.info("EML file created from report file")

                
                service_reports= []
                for sr in report["service_reports"]:
                    service_reports.append(
                        ServiceReport(sr["response"], sr["service_name"],
                                      sr["service_type"], sr["timestamp"],
                                      sr["exec_time"], sr["results"])
                    )
                
                logging.info("Service Reports created from report file")

                return EMLReport(report_eml,service_reports=service_reports, timestamp=report["timestamp"])
        except Exception as e:
            logging.log(msg=str(e), level=logging.ERROR)
            return None
        
