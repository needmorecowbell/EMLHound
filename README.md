# EMLHound

## Usage

- You can use this project as a library, a cli tool, a web api, a web service -- and much more.

- install requirements from requirements.txt: `pip install -r requirements.txt`
- start or connect to an existing Redis Server, pass the credentials into your `config.json` in the `redis` section. 
- set up your config.json file if you would like to run services. To just run the commandline tool without saving files to a vault, you don't need to provide a config



**Library**

- The library is the most flexible way to use EMLHound. You can quickly extract and identify attachments, as well as run a suite of tools to determine more information about the file being investigated. 

Retrieve all headers from eml files in a directory:
```python
from emlhound.emlhound import EMLHound
from pprint import pprint

e = EMLHound(vman_path="/home/user/eml_vault")
reports = e.scan_directory("/path/to/directory", recursive=False)

for report in reports
  pprint(report.eml.header)
    
```

```python
from emlhound.vaultman import VaultMan
from pprint import pprint

vman = VaultMan(path="/home/user/eml_vault")

attachments = vman.get_all_attachments_with_mimetype("application/pdf")
print("Attachments: ", len(attachments))
pprint([attachment.to_dict() for  attachment in attachments])

```

**CLI**

```
usage: emlhcli.py [-h] [-v] [-d] [-r] [-c CONFIG] [-o OUTPUT] [--daemon] [--generate-config] [-t TARGET]

options:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -d, --directory       set target to directory of emails
  -r, --recursive       search a directory recursively
  -c CONFIG, --config CONFIG
                        config file path (or env var EMLH_CFG)
  -o OUTPUT, --output OUTPUT
                        output file/directory/workspace path
  --daemon              run as a daemon, requires config
  --generate-config     generate a config file in /tmp
  -t TARGET, --target TARGET
                        path to eml file or directory of emails
```

`python3 emlcli.py -dr ~/Path/to/EML/Directory`


**Plugins**

Temporary Fix:

If any plugins are enabled, you must include the config path as an environment variable, stored as `EMLH_CFG`. Conveniently, this allows you to not have to enter in your config path each time: 

`-> % export EMLH_CFG="/path/to/config.json"`
`-> % python3 emlhcli.py --daemon -v`

However, the problem is that you can't run multiple daemon instances of EMLHound with different configs. To fix this, I would need to reevaluate how configs are passed into the structure. Merge requests/issues with advice on this topic are much appreciated.





**Tip: Too Complicated?**
- You don't need to use the config, or know all about the structure of EMLHound.

-  While sources have to be defined for daemon use, alternatively you can directly scan a file or folder by using the command line tool. This avoids Sources, the EMLPool, and Operators altogether. The only service that runs in this mode is the EMLParser service.

- You can also use most of the tools included in this app separately as libraries if you don't like how they work as one.


## Structure

### Sources

- [Sources](docs/Sources/README.md) are places where new EML files to be  can be found
- The Local Source is a directory watcher, looking for recently created files in the directory being watched with an *.eml pattern
- If a file is found, it is added to the EMLPool for the next available scan job.

### Operators

- [Operators](docs/Operators/README.md) take in [EML Reports](docs/Reports) from the EMLPool and take action with them. 
- Operators help you do things like share information to other places as they happen.

- Examples include:
  - a virustotal message bot for sending results out to the community when an ip address is confirmed to have send malicious content
  - enriching a local obsidian.md vault to find relationships between emails in an investigation.

### Vault

- The vault is where all emails are stored. They are stored in workspace directories, labeled with the eml file's md5 hash.

- Inside the workspace contains:
  - the eml will be stored with the filename as it's md5 hash.
  - report.json, the EMLReport for the file once it's been scanned
  - attachments directory containing all extracted attachments from eml
  - service_reports directory containing all reports information that has been run during scanning

### VaultMan
 
 - VaultMan is the Manager class for the Vault
 
 - This class can be used separately from the app for management of the eml vault, but it also is a core part of how sources, services, and operators interact with each other

### EMLPool
  
  - The EMLPool is a redis instance that contains a list called `eml_queue`. This list only contains filepaths for incoming eml files to scan. EMLPool is only used when using the app as a daemon.

  - All sources must append their results to the EMLPool, which is regularly checked for new files. These new files are handled as they come in, spawning on new reports for all incoming filepaths.
### Services 

- [Services](docs/Services/README.md) are run against different parts of an EML as a report is built.

- Services will always return a [Service Report](docs/Reports), which detail informations about the results and statistics of a service job

**TODO**
- In the future, services will be able to stack upon one another with workflows. Ie, once attachments have been extracted, separate all image files. With the image files, use an OCR Service to try and read text from the image. Enrich the EML attachment with acquired information.


### Plugins

- There are currently two plugins available, the web server and the api server. These can be configured in `config.json`
- Check the usage section for information abouut how to run these
- Plugins load under separate threads, all managed under the EMLHound application. These apps could just as easily be run separately by using the library.


## Resources

[]()



