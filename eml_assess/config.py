from typing import Dict
import json
import logging

class Config():
    def __init__(self, cfg_path:str):
        self.config = self.parse_config(cfg_path)
        pass


    def parse_config(self,cfg_path) -> Dict:
        """
        Parses the config file
        
        :param cfg_path: Path to the config file
        :return: Dict of config values
        """

        try:
            with open(cfg_path) as f:
                config = json.load(f)
            
            return config
        except Exception as e:
            logging.log(msg="Error loading config file: " + str(e), level=logging.ERROR)
