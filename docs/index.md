# Abstract Data <br> Campaign Finance Data

This package is designed to make it easy to download, validate, and load campaign finance data from the Texas Ethics Commission (TEC) website.

## Features

* Download Latest TEC File
* Validate Expense & Contribution Records
* Easily search for Candidates, Committees, and Contributor data

### Downloaded latest TEC Expense/Contribution file

```py title="main.py"
from app.loaders.tec_loader import TECFolderLoader

# initialize TECFolderLoader object
tec_loader = TECFolderLoader()

# download TEC files and extract to temporary folder
tec_loader.download()

# iterate over all files in the expenses TEC category
for file in tec_loader.expenses:
    print(file)

# iterate over all files in the contributions TEC category
for file in tec_loader.contributions:
    print(file)
```

### Load Expense & Contribution Records
```py title="main.py"
from app.loaders.tec_loader import TECFolderLoader

files = TECFolderLoader()

# Load contribution files into a dictionary of TECFile objects
donors = files.contributions.load_files()
```

### Validate Expense & Contribution Records
```py title="main.py"
from app.loaders.tec_loader import TECFolderLoader

files = TECFolderLoader()

# Validate contribution files and return a dictionary of passed and failed records
donor_validation = files.contributions.validate_category()
```
