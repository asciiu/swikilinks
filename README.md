# swikilinks 

Picklist and label generator from ship station csv. 

### Prerequisites

- python 2.7 or better (comes preinstalled on all macs)
- install python pip using "sudo easy_install pip"
- install python py2app using "pip install py2app"
- install python pyfpdf using "pip install fpdf==1.7"

### Running via command line in terminal app: 
```
$ cd /path/to/swickilinks
$ python picklist_gen.py /path/to/shipstations.csv true
```

This method of running the script will dump the label and pick list pdf 
in the same directory.

### How to generate the hotdog app in the terminal app.
```
$ cd /path/to/swickilinks
$ python setup.py py2app 
```

This will create the app under the dist folder.


## References
- https://py2app.readthedocs.io/en/latest/tutorial.html
- https://pyfpdf.readthedocs.io/en/latest/

