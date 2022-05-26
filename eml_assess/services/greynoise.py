from eml_assess.services.service import Service

class GreyNoiseService(Service):
    """GreyNoiseService
    
    This class is a service that provides access to GreyNoise for providing input on an IOC in an EML.
    """

    def __init__(self, name="GreyNoise Service"):
        super().__init__(name)
        self.service_type="greynoise"

    