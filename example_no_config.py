from eml_assess.eml_assess import EMLAssess
from pprint import pprint
import os

from eml_assess.vaultman import VaultMan 


e = EMLAssess(vman_path="/home/adam/Desktop/vault")
reports = e.scan_directory("/home/adam/Desktop/eml_ingress", recursive=False)


for report in reports:
    if(e.vman.in_vault(report.eml)):
        workspace = e.vman.path+"/"+report.eml.md5
        if(os.path.exists(workspace+"/report.json")):
            print(report.eml.md5, "In vault")
        else:
            report.to_file(workspace+"/report.json")
    else:
        workspace= e.vman.initialize_workspace(report.eml)
        report.to_file(workspace+"/report.json")
