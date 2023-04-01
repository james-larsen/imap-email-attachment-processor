# IMAP Email Attachment Processor

The purpose of this application is to allow people to set up a number of IMAP email accounts, login to them periodically, and check unread emails against a set of patterns, including sender, subject, and body, as well as attachment patterns.  When a match is found, the attachment is routed to a specified location.  New IMAP accounts and patterns can be added using JSON files.

## Requirements

TBD

## Installation

### Via poetry (Installation instructions [here](https://python-poetry.org/docs/)):

```python
poetry install
```

### Via pip:
```python
TBD
```

## Usage

Configure the following files:

* ./src/email_file_monitoring/imap_accounts.json
* ./src/email_file_monitoring/default_email_rules.json

```python
python3 src/email_file_monitoring/main.py
```

## Passwords

The module for retrieving database passwords is located at **'./src/email_file_monitoring/utils/password.py'**.  By default it uses the 'keyring' library, accepts two strings of 'secret_key' and 'user_name' and returns a string of 'password'.  If you wish to use a different method of storing and retrieving database passwords, modify this .py file.

If you require more significant changes to how the password is retrieved (Eg. need to pass a different number of parameters), it is called by the **'./src/email_file_monitoring/main.py'** module.

If you do wish to use the keyring library, create password entries using the "account_name" and "imap_password_key" values discussed below.

## App Configuration

The application is primarily controlled by .json files.  The first is:

**./src/email_file_monitoring/imap_accounts.json**

Contains the details for each IMAP account to be connected to.  It looks like the below:

``` json
{
    "imap_accounts": [
        {
            "account_name": "XYZ_Department_Sales_Files",
            "imap_username": "user1",
            "imap_server": "imap.example.com",
            "imap_port": 993,
            "imap_password_key": "password_key"
        }
    ]
}
```

* ***account_name***:  General name for the file processing area.  It could be named based on the email address being monitored, or the department the files are being delivered for, etc.
* ***imap_username***:  Login username for IMAP server
* ***imap_server***:  IMAP Server Address
* ***imap_port***:  IMAP Server Port
* ***imap_password_key***:  Key to be used along with "account_name" for retrieving the correct password

---

**./src/email_file_monitoring/default_email_rules.json**

Holds the specific patterns to look for and where to deliver the files when they are detected.

``` json
  "conditions": [
    {
      "name": "example_entry_will_be_ignored",
      "pattern": {
        "sender": "@domain",
        "subject": ["Pattern01", "Pattern02"],
        "body": ["Pattern01", "Pattern02"],
        "attachments": [
          {
            "filename": ["filenamepattern", ".csv"]
          }
        ]
      },
      "delivery": {
        "target": "local",
        "path": "/path/to/save/files"
      }
    }
```

* ***name***:  Name for the condition being defined
* ***pattern***
    * ***sender***:  String pattern to check against the "Sender" field
    * ***subject***:  List of strings to check against the "Subject" field
    * ***body***:  List of strings to check against the "Body" field
    * ***filename***:  List of strings to check against the "Filename" field of each attachment
* ***delivery***
    * ***target***:  Delivery target type.  Currently must be 'local', will eventually allow other targets
    * ***path***:  Local file path to deliver attachments

A few notes:

* The first entry "example_entry_will_be_ignored" will be ignored by the program.  Leaving this here may make it easier to refer to the proper syntax and which patterns are available
* For items defined as lists above, leave them in [], even if only a single pattern is desired
* If the body is of type "multipart/alternative", the "text/plain" version will be preferred over the "text/html" version
* Currently the program can only deliver files locally.  Eventually the program will be enhanced to deliver to other locations (S3 buckets, FTP Servers, etc.)

## Account-Specific Conditions

By default all accounts will use the **default_email_rules.json** file to determine their conditions.  However, you can create account-specific condition files, if a given account can locate a file in the same location with the name "**{account_name}_email_rules.json**".

For example, if you have an account_name in your "imap_accounts.json" with a value of "Acme_Sales_Files", then it will look for "**Acme_Sales_Files_email_rules.json**" and use it instead of the default.

## Logging

TBD

## About the Author

My name is James Larsen, and I have been working professionally as a Business Analyst, Database Architect and Data Engineer since 2007.  While I specialize in Data Modeling and SQL, I am working to improve my knowledge in different data engineering technologies, particularly Python.

[https://www.linkedin.com/in/jameslarsen42/](https://www.linkedin.com/in/jameslarsen42/)