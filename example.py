from eml_assess.eml_assess import EMLAssess
from pprint import pprint

e = EMLAssess(target="/home/adam/Desktop/eml_ingress",is_directory=True,recursive=False)
reports = e.scan_directory()

for report in reports:
    print("EML PATH: ", report.eml.get_path())
    print("Service Reports:")
    for sr in report.service_reports:
        print('\t'+sr.service_name)
        pprint(sr.results)
