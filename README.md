##Gen the py2applet setup.py config
```
$ py2applet --make-setup products_export.csv vaseline.py
```

##Edit the setup.py file
Edit setup to include:

from setuptools import setup

Plist = dict(CFBundleDocumentTypes=[dict(CFBundleTypeExtensions=["csv"],
                                         CFBundleTypeName="CSV Document",
                                         CFBundleTypeRole="Viewer"),
                                    ]
             )
APP = ['vaseline.py']
DATA_FILES = ['products_export.csv']
OPTIONS = {'argv_emulation': True,
           'plist': Plist,
           }

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

## Bundle the app.
```
$ python setup.py py2app 
```

This will create the app under the dist folder.


## References
https://py2app.readthedocs.io/en/latest/tutorial.html
https://pyfpdf.readthedocs.io/en/latest/Tutorial/index.html#line-breaks-and-colors

