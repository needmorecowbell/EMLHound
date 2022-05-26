from typing import List

class EML():
    """
    Represents an EML file in python code
    """
    def __init__(self, path:str):
        self.path = path
        self.ip_addresses=[]

       
    def get_ip_addresses(self) -> List[str]:
        """
        Returns a list of IP addresses in the EML file
        
        :return: List of IP addresses"""

        return self.ip_addresses


    def get_path(self) -> str:
        """
        Returns the path to the EML file
        """
        return self.path
      