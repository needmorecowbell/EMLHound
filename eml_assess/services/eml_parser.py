from datetime import datetime
import json
import eml_parser as emlp
from eml_assess.models.reports import ServiceReport
from eml_assess.models.eml import EML
from eml_assess.models.eml_attachment import EMLAttachment
from eml_assess.services.service import Service
import time

class EMLParserService(Service):
  def __init__(self, eml:EML, name: str = "EMLParser Service", ):
      super().__init__(name)
      self.eml= eml
      self.service_handle="eml_parser"
    
  def json_serial(self,obj):
    if isinstance(obj, datetime):
      serial = obj.isoformat()
      return serial

    raise TypeError("Type not serializable")


  def execute(self) -> ServiceReport:
    """Runs the service, returning a ServiceReport Object"""

    start = time.time()
    results = {}
    response = "success"
    try:
      with open(self.eml.path, 'rb') as f:
        raw_email = f.read()

      ep = emlp.EmlParser()
      parsed_eml = ep.decode_email_bytes(raw_email)
      #results = json.dumps(parsed_eml, default=self.json_serial) # dump the results to a json string
    except Exception as e:
      print("eml parser failure: ", e)
      response = "failure"
    finally:
      elapsed = time.time() - start
      return ServiceReport(response=response,
                           service_name=self.name,
                           timestamp=datetime.now(),
                           exec_time=elapsed,
                           results=parsed_eml)

