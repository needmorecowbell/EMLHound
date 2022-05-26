from eml_assess.services.service import Service

class VirustotalService(Service):
    """VirustotalService
    
    This class is a service that provides access to Virustotal for providing input on an IOC in an EML.
    """

    def __init__(self, name="Virustotal Service"):
        super().__init__(name)
        self.service_type="virustotal"
