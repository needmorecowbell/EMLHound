import argparse
from eml_assess.eml_assess import EMLAssess
import os
from pprint import pprint
import json

from eml_assess.models.eml import EML

def prepare_args():
    art= ''''''
    print(art+"Welcome to EML ASSESS CLI\n")

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-d", "--directory", help="set target to directory of emails", action="store_const", const=True, default=False)
    parser.add_argument("-r", "--recursive", help="search a directory recursively", action="store_const", const=True, default=False)
    parser.add_argument("-c", "--config", type=str, help="config file path", required=False)
    parser.add_argument("-o", "--output", type=str, help="output file/directory/workspace path", required=False)
    parser.add_argument("--generate-config", help="generate a config file in /tmp", action="store_true")
    parser.add_argument("target_path", help="path to eml file or directory of emails")

    args = parser.parse_args()
    return args

def generate_config(cfg_path=None, vault_path=None):
    """
    Generates a config file in tmp directory
    """

    tmp_cfg="""
{   
    "vault_path": "{vault_path}",
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
    if(cfg_path is None):
        cfg_path = "/tmp/emlcfg.json"
    if not os.path.exists(cfg_path):
        print("Config file not found, generating new config file at: ", cfg_path)
        with open(cfg_path,"w") as f:
            f.write(tmp_cfg.format(vault_path=vault_path))

def main():
    args = prepare_args()
    
    if(args.config):
        if(not os.path.exists(args.config)):
            if(args.generate_config):
                print("Generating config file at: ", args.config)
                generate_config(args.config)
            else:
                print("Config file not found, correct path or pass --generate-config to generate a new config file in specified path")
                exit()


    e = EMLAssess(config_path=args.config,vman_path=args.output)
        
    if(args.directory):
        results = e.scan_directory(args.target_path, args.recursive)

    else: # scan single eml
        if(args.verbose):
            print("Scanning file: ", args.target_path)
        try:
            eml = EML(args.target_path)
        except Exception as e:
            print(e)

        results = e.scan_eml(eml)

    if(type(results) is list):
        for report in results:
            if(args.output):
                if(os.path.exists(f"{args.output}/{report.eml.md5}/report.json")):
                    print(f"Report already exists for {report.eml.md5}, skipping")
                else:    
                    print("writing report to: ", f"{args.output}/{report.eml.md5}/report.json")
                    report.to_file(f"{args.output}/{report.eml.md5}/report.json")

           # pprint(report.to_dict())
        print("\n############################################################\n")
    else:
        pprint(results.to_dict()["eml"])
        if(args.output):
            if(os.path.exists(f"{args.output}/{results.eml.md5}/report.json")):
                print("Report already exists, skipping")
            else:
                print("Writing report to: ", f"{args.output}/{results.eml.md5}/report.json")
                results.to_file(f"{args.output}/{results.eml.md5}/report.json")

        #print("EML PATH: ",report.eml.get_path())
        #print("\tService Reports: ", len(report.service_reports))
        # for sr in report.service_reports:
        #     print('\t'+sr.service_name)
        #     pprint(sr.results)



if __name__ == "__main__":
    main()