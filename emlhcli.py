import argparse
from emlhound.emlhound import EMLHound
import os
from pprint import pprint
import logging
from emlhound.models.eml import EML

def prepare_args():
    art= '''
                   __
          \ ______/ V`-,
           }        /~~
          /_)^ --,r'
         |b      |b

    Welcome to EMLHound CLI
    '''
    print(art)

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-d", "--directory", help="set target to directory of emails", action="store_const", const=True, default=False)
    parser.add_argument("-r", "--recursive", help="search a directory recursively", action="store_const", const=True, default=False)
    parser.add_argument("-c", "--config", type=str, help="config file path", required=False)
    parser.add_argument("-o", "--output", type=str, help="output file/directory/workspace path", required=False)
    parser.add_argument("--daemon", help="run as a daemon, requires config", action="store_true", required=False)
    parser.add_argument("--generate-config", help="generate a config file in /tmp", action="store_true")
    parser.add_argument("-t","--target", type=str, required=False, help="path to eml file or directory of emails")

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
        logging.log(msg="Config file not found, generating new config file at: "+str(cfg_path), level=logging.INFO)
        with open(cfg_path,"w") as f:
            f.write(tmp_cfg.format(vault_path=vault_path))

def main():
    args = prepare_args()

    if(args.verbose):
        format = f"[%(levelname)s] %(asctime)s <%(filename)s> %(funcName)s_L%(lineno)d- %(message)s"
        logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    else:
        format = f"[%(levelname)s] %(asctime)s - %(message)s"

        logging.basicConfig(format=format, level=logging.WARNING, datefmt="%H:%M:%S")
    
    if(args.config):
        if(not os.path.exists(args.config)):
            if(args.generate_config):
                print("Generating config file at: ", args.config)
                generate_config(args.config)
            else:
                print("Config file not found, correct path or pass --generate-config to generate a new config file in specified path")
                exit()

    if(args.daemon):
        if(not args.config):
            logging.log(msg="Daemon requires config file", level=logging.ERROR)
            exit()
        else:
            e = EMLHound(config_path=args.config)
            e.run() # script stops here if daemon is enabled


    # If not daemon, run EMLHound as a CLI tool
    e = EMLHound(config_path=args.config,vman_path=args.output)
        
    if(args.directory):
        if(args.target):
            results = e.scan_directory(args.target, args.recursive, check_vault=False)
        else:
            logging.log(msg="No target specified, pass with (-t)", level=logging.ERROR)
            exit()

    else: # scan single eml
        if(args.target):
            if(args.verbose):
                logging.log(msg="Scanning file: "+str(args.target), level=logging.INFO)
            try:
                eml = EML(args.target)
            except Exception as e:
                print(e)

            results = e.scan_eml(eml,check_vault=False)
        else:
            logging.log(msg="No target specified, pass with (-t), or run in daemon (--daemon) mode with config", level=logging.ERROR)
            exit()

    if(type(results) is list):
        for report in results:
            if(args.output):
                if(os.path.exists(f"{args.output}/{report.eml.md5}/report.json")):
                    logging.warning(msg=f"Report already exists for {report.eml.md5}, skipping")
                else:    
                    logging.info(f"writing EML Report to: {args.output}/{report.eml.md5}/report.json")
                    report.to_file(f"{args.output}/{report.eml.md5}/report.json")

    else:
        if(args.output):
            if(os.path.exists(f"{args.output}/{results.eml.md5}/report.json")):
                logging.warning(msg="Report already exists, skipping")
            else:
                logging.info(msg=f"Writing report to: {args.output}/{results.eml.md5}/report.json")
                results.to_file(f"{args.output}/{results.eml.md5}/report.json")

if __name__ == "__main__":
    main()