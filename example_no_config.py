from eml_assess.eml_assess import EMLAssess
import os



e = EMLAssess(vman_path="/home/adam/Desktop/vault")
reports = e.scan_directory("/home/adam/Desktop/bak", recursive=False, check_vault=False)


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
