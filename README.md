# EML_Assess

**NOTICE:** Don't touch this yet! Just jotting down ideas, nothing works


## Usage

- You can use this project as a library, a cli tool, a web api, a web service -- and much more.

- install requirements from requirements.txt: `pip install -r requirements.txt`
- set up your config.json file, or let the cli tool automatically generate one for you.


**Library**

```python
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

```

**CLI**

```
usage: emlcli.py [-h] [-v] [-d] [-r] [-c CONFIG] [-o OUTPUT] target_path

positional arguments:
  target_path           path to eml file or directory of emails

options:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -d, --directory       set target to directory of emails
  -r, --recursive       search a directory recursively
  -c CONFIG, --config CONFIG
                        config file path
  -o OUTPUT, --output OUTPUT
                        output file/directory/workspace path
```

`python3 emlcli.py -dr ~/Path/to/EML/Directory`

## Structure

### Sources

- [Sources](docs/Sources/README.md) are places where new EML files to be  can be found


### Operators

- [Operators](docs/Operators/README.md) take in [EML Reports](docs/Reports) and take action with them. 


### Services 

- [Services](docs/Services/README.md) are run against different parts of an EML as a report is built.
- Services will always return a [Service Report](docs/Reports), which detail informations about the results and statistics of a service job


## Resources

[]()



