import argparse
from eml_assess.eml_assess import EMLAssess
import os
from pprint import pprint
import json

def prepare_args():
    art= ''''''
    print(art+"Welcome to EML ASSESS CLI\n")

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-d", "--directory", help="set target to directory of emails", action="store_const", const=True, default=False)
    parser.add_argument("-r", "--recursive", help="search a directory recursively", action="store_const", const=True, default=False)
    parser.add_argument("-c", "--config", type=str, help="config file path", required=False)
    parser.add_argument("-o", "--output", type=str, help="output file/directory/workspace path", required=False)

    parser.add_argument("target_path", help="path to eml file or directory of emails")

    args = parser.parse_args()
    return args

def generate_config(path=None):
    """
    Generates a config file in tmp directory
    """

    tmp_cfg="""
{   
    "sources":[
        {
            "name":"Source 1",
            "type":"local",
            "remove_from_source":true,
            "path":"/home/adam/Desktop/eml_ingress"
        }
    ],

    "services" : [
        {
            "type" : "eml_parser",
            "name" : "EML Parser Service",
            "description" : "EML Parser, parses out EML body contents"
        }
    ],

    "operators" : []
}  
    """
    if(path is None):
        path = "/tmp/emlcfg.json"
    if not os.path.exists(path):
        print("Config file not found, generating new config file at: ", path)
        with open(path,"w") as f:
            f.write(tmp_cfg)

def main():
    args = prepare_args()
    
    if(args.config):
        if(not os.path.exists(args.config)):
            generate_config(args.config)
        config= args.config
    else:
        generate_config()
        config= "/tmp/emlcfg.json"
    

    e = EMLAssess(args.target_path, is_directory=args.directory, recursive=args.recursive, config_path=config)
        

    reports = e.scan()

    for report in reports:
        pprint(report.to_dict())
        print("\n############################################################\n")
        #print("EML PATH: ",report.eml.get_path())
        #print("\tService Reports: ", len(report.service_reports))
        # for sr in report.service_reports:
        #     print('\t'+sr.service_name)
        #     pprint(sr.results)



if __name__ == "__main__":
    main()