from datetime import datetime
import json
import eml_parser as emlp
from eml_assess.models.reports import EMLReport, ServiceReport
from eml_assess.models.eml import EML
from eml_assess.models.eml_attachment import EMLAttachment
from eml_assess.services.service import Service
import time
from pprint import pprint

class EMLParserService(Service):
  def __init__(self, eml:EML, name: str = "EMLParser Service", ):
      super().__init__(name)
      self.eml= eml
      self.service_type="eml_parser"

  @classmethod
  def enrich(self, report:EMLReport, service_report:ServiceReport )-> EMLReport:
    """Enriches the base EML report with additional information gained from Service Reports
    
    :param report: EMLReport
    :param service_report: ServiceReport
    :return: EMLReport"""

    for key, value in service_report.results.items():
      if(key == "body"):
        report.eml.body = value
      if(key == "header"):
        report.eml.header = value

      if(key == "attachment"):
        for file in value:
          eml_attachment = self.extract_attachment(file=file)
          report.eml.append_attachment(eml_attachment)

    service_report.results= "Merged to Report"
    report.add_service_report(service_report)

    return report

  @classmethod
  def extract_attachment(self, file:dict)->EMLAttachment:
    """Handle Attachment Data from an incoming EML file"""
    attachment = EMLAttachment()

    attachment.file_name = file.get("filename")
    attachment.file_extension= file.get("extension")
    attachment.file_size = file.get("size")
    attachment.hashes = file.get("hash")
    attachment.mime_type = file.get("mime_type")
    attachment.mime_type_short = file.get("mime_type_short")
    attachment.raw = file.get("raw")

    return attachment


  def execute(self) -> ServiceReport:
    """Runs the service, returning a ServiceReport Object"""

    start = time.time()
    results = {}
    response = "success"
    try:
      ep = emlp.EmlParser(include_attachment_data=True)
      parsed_eml = ep.decode_email(self.eml.path)

    except Exception as e:
      print("eml parser failure: ", e)
      response = "failure"
    finally:
      elapsed = time.time() - start
      return ServiceReport(response=response,
                           service_name=self.name,
                           service_type= self.service_type,
                           timestamp=datetime.now(),
                           exec_time=elapsed,
                           results=parsed_eml)

