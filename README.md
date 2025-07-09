# Security Checks

Security Checks is a flask application interacts with various AWS account IDs using AWS profiles and identifies the list of security vulnerabilities.

## Running in Local

Creating and activating virtual environment
``` shell
python3 -m venv .vnev
source ./venv/bin/activate
```

Installing Dependencies

```aiignore
pip3 install -r requirements.txt
```

Running Flask application in local

```aiignore
python3 -m flask --app security_check run --debug
```