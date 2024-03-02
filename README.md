# Script for comparing passwords.

This script was used in the migration process to compare and ensure that all valid credentials that were in the old good passwords.txt are backed up into Bitwarden account.

## Requirements

Create the environment and install dependencies:

```bash
# create and activate virtual environment
python -m venv env
./env/Scripts/activate

# install dependencies:
python -m pip install -r requirements.txt
```

## Usage

I had a `passwords.txt` plain text file where I was storing my passwords... I know, pretty awkward and insecure practice :disappointed:.
The `passwords.txt` has the following format:

```txt
...
<name separated w spaces>
  <username or email>
  <password>
  <another fields>
...
```

The script also awaits a bitwarden json file (format from 2023 - 2024) in the root: `bitwarden*.json`.
The folders names are the prefixed to the account name of each item, like:

```
<folder_name>_<name>
```

Then these modified account names are matched against the names in the `passwords.txt` using `pandas`.
