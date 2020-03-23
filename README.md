# swikilinks 

Picklist and label generator from ship station csv.  The main logic for the pick list gen is in the
picklist_gen.py file. Refer to picklist_gen.py to see how the ship station csv is parsed.

### Prerequisites

- python 3.7.7 
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

Using pyinstaller
```
$ pyinstaller --icon=assets/hotdog.icns --onefile --windowed --osx-bundle-identifier=com.reptilinks.picklistgen src/picklist_gen.py 
$ pyinstaller --onefile picklist_gen.spec
$ pyinstaller --onedir picklist_gen.spec
```

Pyinstaller: generating the spec file from scratch:
```
$ pyi-makespec --icon=assets/hotdog.icns --onefile --windowed --osx-bundle-identifier=com.reptilinks.picklistgen src/picklist_gen.py
```

## References
- https://py2app.readthedocs.io/en/latest/tutorial.html
- https://pyfpdf.readthedocs.io/en/latest/

