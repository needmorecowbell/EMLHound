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
            generate_config(args.config)
        config= args.config
    else:
        generate_config(args.output)
        config= "/tmp/emlcfg.json"
    

    e = EMLAssess(args.target_path, is_directory=args.directory, recursive=args.recursive, config_path=config)
        

    results = e.scan()
    if(type(results) is list):
        for report in results:
            if(args.output):
                print("writing report to: ", args.output+"/"+report.eml.header["subject"]+"_report.json")
                report.to_file(f"{args.output}/{report.eml.md5}/{report.eml.header['subject']}_report.json")

            pprint(report.to_dict()["eml"])
            print("\n############################################################\n")
    else:
        pprint(results.to_dict()["eml"])
        if(args.output):
            print(f"writing report to: {args.output}/{results.eml.md5}/{results.eml.header['subject']}_report.json")
            results.to_file(f"{args.output}/{results.eml.md5}/{results.eml.header['subject']}_report.json")

        #print("EML PATH: ",report.eml.get_path())
        #print("\tService Reports: ", len(report.service_reports))
        # for sr in report.service_reports:
        #     print('\t'+sr.service_name)
        #     pprint(sr.results)



if __name__ == "__main__":
    main()