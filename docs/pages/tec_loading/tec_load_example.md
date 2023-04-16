
Put together, `TECRecord`, `TECFile`, and `TECCategory` handle everything you need for loading, validating, and inserting TEC records into a SQL database through the `TECFolderLoader` class.

## Example

```py title="main.py"
from app.loaders.tec_loader import TECFolderLoader

files = TECFolderLoader()

# Load contribution files into a dictionary of TECFile objects
donors = files.contributions.load_files()

# Validate contribution files and return a dictionary of passed and failed records
donor_validation = files.contributions.validate_category()
```