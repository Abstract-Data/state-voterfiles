
## Overview
The `TECFolderLoader` class is responsible for loading the TEC (Texas Ethics Commission) files into the database and returning a dictionary of SQL models. It contains methods for downloading TEC files from a URL and extracting them into a temporary folder, as well as a method for listing all the files in the folder.

### Attributes
* `folder`: A Path object representing the folder where the TEC files are located. By default, this is set to the current working directory (Path.cwd()) followed by the "tmp" subdirectory.
* `_ZIPFILE_URL`: A string representing the URL where the TEC files are located.
* `expenses`: A TECCategory object representing the expenses TEC category.
* `contributions`: A TECCategory object representing the contributions TEC category.

### Methods
* `file_list(cls, prefix)`: Returns a generator object that yields all the files in the folder with the specified prefix. The prefix argument should be a string that represents the prefix of the file name.
* `download(cls, read_from_temp=True)`: Downloads the TEC files from the _ZIPFILE_URL URL and extracts them into the folder directory. By default, the method reads from the temporary folder if it exists (read_from_temp=True). If the read_from_temp argument is set to False, the method prompts the user to overwrite the temporary folder or use it as the source. If the user chooses to overwrite the temporary folder, the method downloads the files from the URL and extracts them into the temporary folder. If the user chooses to use the temporary folder as the source, the method checks if the temporary folder contains the necessary CSV files. If not, it extracts the ZIP file into the temporary folder. If the user chooses not to overwrite the temporary folder, the method exits.
* `__post_init__(self)`: This method initializes the expenses and contributions class variables with the files in the folder directory that match the settings.EXPENSE_FILE_PREFIX and settings.CONTRIBUTION_FILE_PREFIX prefixes, respectively.

## Example 
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

In this example, we first create a new `TECFolderLoader` object. We then download the TEC files and extract them to the temporary folder by calling the `download` method. Finally, we iterate over all the files in the expenses and contributions TEC categories by accessing the `expenses` and `contributions` attributes, respectively.