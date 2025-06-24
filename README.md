# Salesforce Code Download and Migration

This repository provides tools for downloading specific Salesforce project code and migrating it using PowerShell. It includes:

- A Python script to download Salesforce project metadata.
- A PowerShell script to assist with PnP (Patterns and Practices) migration tasks.

---

## 📁 Contents

- `Salesforce_download_code_specific_project.py`: Python script to download specific Salesforce project metadata/code.
- `pnp_migration.ps1`: PowerShell script for handling PnP-based migration.
- `requirements.txt`: Python dependencies list.

---

## ✅ Prerequisites

Make sure the following are installed:

- [Python 3.7+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/)
- [PowerShell-7]
- [Salesforce CLI] (https://developer.salesforce.com/tools/salesforcecli)
- .env file in the current directory with the needed credentials 
- Salesforce credentials or configuration (as required by the Python script)

---
## 📦 Installation

Install the required Python packages:

```pip
pip install -r requirements.txt

```

Install Salesforce CLI to get access token by running these commands in order in terminal:

```salesforce cli
sf --version
 
sf org login web
 
sf org display --target-org email_associated_to_the_production_salesforce_env

```

---
## ⚠️ Warning

Before running the Python script, **make sure to update the `access_token`**, **`instance_url`** and **`project_name`** in the code:

```python

access_token =  "ACCESS token from Salesforce CLI"
instance_url = "instance_url from Salesforce CLI"
project_name = "YOUR DESIRED PROJECT NAME"  # Replace with your actual project name

```
## 🚀 Usage

### ▶️ Run the Python Script

This script downloads metadata/code from a specific Salesforce project.

```python
python Salesforce_download_code_specific_project.py

```
---
## ⚠️ Warning

Before running the Powershell script, **make sure to update the `$sourceFolder` and `$siteUrl`** in the code:

```bash
$sourceFolder = "LOCAL PATH TO THE FOLDER CONTAINING THE PROJECT"
$siteUrl = "https://lendlease.sharepoint.com/sites/*SITENAME*"

```

### ▶️ Run the Powershell Script

This script Uploads metadata to a Sharepoint site.

```bash
.\pnp_migration.ps1

```

