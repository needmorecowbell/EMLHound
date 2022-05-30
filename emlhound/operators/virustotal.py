from emlhound.operators.operator import Operator

class VirusTotalOperator(Operator):
    """VirusTotalOperator
    
    This class is an operator that provides access to Virustotal for making comments on IOCs.
    """
    
    def __init__(self, name="VirusTotal Operator"):
        super().__init__(name)