# ThousandEyes-Test-Report

This script leverages [ThousandEyes v7 REST APIs](https://developer.cisco.com/docs/thousandeyes/v7) to pull detailed information from a ThousandEyes account and formats it into a comprehensive CSV file for Cloud and Enterprise Agent Tests. This script aims to streamline the process of extracting and analyzing ThousandEyes test data, reducing the time and effort required to gather and analyze network performance data for better monitoring and optimization.

## Sample Output:
﻿<img width="1354" alt="image" src="https://github.com/user-attachments/assets/bdb28284-fd81-496d-852a-ca9cff497497">

    Primary Language: Python 3.x
    Dependencies (Python Libraries): 
    - Requests library for API calls
    - CSV module for data formatting
    - dotenv module for loading environment variables from a .env file
    - OS module for interacting with the operating system
    - SYS module for system-specific parameters and functions
    Standalone Script: Designed as a standalone script, but can be integrated into larger automation frameworks if needed


## Contacts:
 - Andrew Pignataro (apignata@cisco.com)
 - Kalai Shanmugam (kmurugap@cisco.com)
 - Mark McBride (markmcbr@cisco.com)


## Installation:

Clone the repo
```bash
git clone https://wwwin-github.cisco.com/apignata/ThousandEyes-Health-Check.git
```

Set up a Python venv
First make sure that you have Python 3 installed on your machine. We will then be using venv to create an isolated environment with only the necessary packages.

Install virtualenv via pip
```bash
pip install virtualenv
```

Create the venv
```bash
python3 -m venv venv
```

Activate your venv
```bash
source venv/bin/activate
```

Install dependencies
```bash
pip install -r requirements.txt
```

## Configuration:
1. Obatin the `OAuth Bearer Token` from your ThousandEyes Account for the authentication when communicating with the APIs
  - [Navigate to your ThousandEyes](https://app.thousandeyes.com/account-settings/users-roles/)
  - Account Settings -> Users and Roles -> User API Tokens -> OAuth Bearer Token -> Create

```
https://app.thousandeyes.com/account-settings/users-roles/
```
  Create an OAuth Bearer Token
  
  ﻿<img width="960" alt="image" src="https://github.com/user-attachments/assets/14515621-0008-4799-9d19-42da1429385d">
 
  Copy the Token and store in a secure location
  
  ![image](https://github.com/user-attachments/assets/6b5bb022-aceb-49dc-802c-b6d833f62ac9)

2. Create a .env File

  - Create a file named .env in the root directory of your python project. 

  - This file will contain your environment variables in the format KEY=VALUE.
    
  - The KEY will be set to `BEARER_TOKEN` and VALUE as `OAuth Bearer Token`

  - We will store `OAuth Bearer Token` in the .env file

  Example: 
  
  <img width="413" alt="image" src="https://github.com/user-attachments/assets/9df3e779-d501-4e0f-b407-460a4fd3e14e">

  

3. (Optional) Set Account Group Name

- The script will pull the default account group, if no name is set
- You can confirm account group in ThousandEyes by checking the image below

<img width="309" alt="image" src="https://github.com/user-attachments/assets/673ec14d-d42c-458e-a7a2-33d9e6fd930d">

- To change the account group name, set the variable `Account_Group_Name` in the python code
<img width="345" alt="image" src="https://github.com/user-attachments/assets/77b0fa52-a669-4813-b0bc-10db4dfae212">

## Usage

Run the script:

```
python3 main.py
```
