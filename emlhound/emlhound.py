import os
import threading
from typing import Dict, List
from emlhound.models.eml import EML
from emlhound.models.reports import EMLReport, ServiceReport
from emlhound.operators.operator import Operator
from emlhound.plugins.plugin import Plugin
from emlhound.services.eml_parser import EMLParserService
from emlhound.config import Config
from emlhound.services.external import ExternalService
from emlhound.services.ipinfo import IPInfoService
from emlhound.sources.gmail import GMailSource
from emlhound.sources.imap import IMAPSource
from emlhound.sources.local import LocalSource
from emlhound.sources.source import Source
from emlhound.vaultman import VaultMan
import time 
import logging
import json
class EMLHound():
    """EMLHound Application"""

    def __init__(self, vman_path:str=None, config_path:str=None):

        format = f"[%(levelname)s] %(asctime)s <%(filename)s> %(funcName)s_L%(lineno)d- %(message)s"
        logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

        logging.info("Initializing EMLHound")
        self.sources = []
        self.source_threads = []

        self.operators= []
        self.operators_threads= []

        self.plugins = []
        self.plugin_threads = []

        if(config_path):
            try:
                import redis
            except:
                logging.log(msg="Redis module not found, must run for daemon", level=logging.ERROR)

            self.config = Config(config_path)
            self.vman = VaultMan(self.config.config["vault_path"])
            try:
                self.eml_pool = redis.Redis(host=self.config.config["redis"]["host"], port=self.config.config["redis"]["port"])
                logging.log(msg="Connected to Redis", level=logging.INFO)

                # clear redis queue on start
                for i in range(0, self.eml_pool.llen("eml_queue")):
                    self.eml_pool.lpop("eml_queue")

                logging.log(msg="Cleared redis eml queue: "+str(self.eml_pool.llen("eml_queue")), level=logging.INFO)

            except Exception as e:
                logging.log(msg=f"Redis error: {e}", level=logging.ERROR)

            self.sources = self.load_sources(self.config.config["sources"])

            self.operators = self.load_operators(self.config.config["operators"])

            self.plugins = self.load_plugins(self.config.config["plugins"])

        else:
            logging.info('No config file provided')
            self.config = None
            self.vman = VaultMan(vman_path) if vman_path else None # vault manager
            

    def run(self):
        """Runs EMLHound as a daemon"""

        assert self.config, "No config file provided"
        self.activate_sources()
        self.activate_operators()
        self.activate_plugins()

        try:
            while True:
                if(self.eml_pool.llen("eml_queue")>0):
                    job = json.loads(self.eml_pool.lpop("eml_queue"))
                    logging.debug(msg=f"Retrieved eml from queue")
                    eml = EML(job["path"], attachments=[])

                    report = self.scan_eml(eml,check_vault=job.get("check_vault",False))
                    # save report to vault
                    report.eml.path=job["path"]

                    if(job.get("delete_after_scan")):
                        os.remove(job["path"])
                        report.eml.path=f"{self.vman.path}/{report.eml.md5}/{report.eml.md5}"
                        logging.debug(msg=f"Deleted eml after scan")

                    self.vman.add_eml_report_to_workspace(report)
                    logging.info(msg=f"EML Report {eml.md5} Scan Complete, added report to workspace")

                time.sleep(1)

        except KeyboardInterrupt:
            print("Exiting")
            exit()


    def load_sources(self, sources_conf:Dict)->List[Source]:
        """Loads sources from the config file
        
        :param sources_conf: Dict of sources from the config file
        :return: List of Source objects"""

        sources = []

        for source in sources_conf:
            if(source["enabled"]):
                match source["type"]:
                    case "local":
                        sources.append(LocalSource(source["path"], source["recursive"], eml_pool=self.eml_pool, name=source["name"]))
                    case "imap":
                        sources.append(IMAPSource(source["username"],source["password"], eml_pool=self.eml_pool, vman=self.vman, folder=source["target_folder"],server=source["server"], name=source["name"], period=source["period"]))
                    case "gmail":
                        sources.append(GMailSource(source["key_file"],source["token_file"],self.eml_pool, self.vman, folder=source["target_folder"], name=source["name"], period=source["period"]))
        return sources


    def load_operators(self, op_conf:Dict)->List[Operator]:
        """Loads operators from the config file
        
        :param op_conf: Dict of Operators from the config file
        :return: List of Source Operators"""

        ops = []

        for op in op_conf:
            if(op["enabled"]):
                match op["type"]:
                    case "obsidian":
                        pass
        return ops
    

    def load_plugins(self, plugin_conf:Dict)->List[Plugin]:
        """Loads plugins from config file

        :param plugin_conf: Dict of plugins from the config file
        :return: List of Plugin objects"""
        logging.info("Loading Plugins...")

        plugins = []

        for plugin in plugin_conf:
            if(plugin["enabled"]):
                match plugin["type"]:
                    case "api_server":
                        logging.info("Loading API Server Plugin")

                        from emlhound.plugins.api_server.app import APIServerPlugin

                        plugins.append(APIServerPlugin(eml_pool=self.eml_pool, vman=self.vman, port=plugin["port"],host=plugin["host"]))
                    case "webserver":
                        logging.info("Loading Web Server Plugin")
                        from emlhound.plugins.webserver.app import WebServerPlugin
                        plugins.append(WebServerPlugin(eml_pool=self.eml_pool, vman=self.vman, port=plugin["port"],host=plugin["host"]))
        return plugins


    def activate_plugins(self):
        """Go through all plugins enabled in the config and load them into the EMLHound object"""
        logging.info("Activating Plugins")

        for plugin in self.plugins:
            t= threading.Thread(target=plugin.activate, daemon=True)
            self.plugin_threads.append(t)
            t.start()
            logging.info(f"Activated Plugin {plugin.name} on thread {t.name}")
    

    def activate_operators(self):
        """Go through all operators enabled in the config and load them into the EMLHound object"""

        logging.info("Activating Operators")

        for op in self.operators:
            t= threading.Thread(target=op.activate, daemon=True)
            self.operators_threads.append(t)
            t.start()
            logging.info(f"Activated Plugin {op.name} on thread {t.name}")
    


    def activate_sources(self):
        """Go through all sources enabled in the config and load them into the EMLHound object"""
        logging.info("activating sources")

        for source in self.sources:
            t= threading.Thread(target=source.activate, daemon=True)
            self.source_threads.append(t)
            t.start()
            logging.info(f"Activated source {source.name} on thread {t.name}")
        

    def scan(self, path:str) -> EMLReport or List[EMLReport]:
        """
        Scans the target directory or file, giving back a report of the findings

        :param path: Path to the target directory or file
        :return: EMLReport or List[EMLReport]
        """
        
        assert os.path.exists(path),"scan error: directory or file path does not exist"

        if(os.path.isdir(path)):
            return self.scan_directory(path)
        else:
            return self.scan_eml(EML(path))



    def scan_eml(self,eml:EML, check_vault:bool=True) -> EMLReport:
        """
        Scans an EML file, giving back an EMLReport of the findings
        
        :param eml_path: Path to the EML file
        :return: EMLReport
        """

        logging.debug(msg="EML Scan entered: "+eml.md5)
        if(self.vman is not None and check_vault):
            if(self.vman.in_vault(eml)):
                logging.debug(msg=f'EML {eml.md5} already in vault')
                return self.vman.retrieve_report_from_vault(eml.md5)


        if(self.vman):
            logging.debug(msg=f"Initializing workspace for {eml.md5}")
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
                logging.debug(msg=f"EML {report.eml.md5} service report added to Vault")

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
    

    def scan_directory(self, path:str, recursive=False, check_vault=False) -> List[EMLReport]:
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
                        eml_files.append(os.path.join(root, file))
        else:
            # get all files in directory
            for file in os.listdir(path):
                if(file.endswith(".eml")):
                    eml_files.append(os.path.join(path,file))
        
        # scan each file
        reports = []
        for fp in eml_files:
            eml = EML(fp, attachments=[])
            report= self.scan_eml(eml, check_vault=check_vault)
            reports.append(report)                

        return reports

    