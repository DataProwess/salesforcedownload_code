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
- [PowerShell](https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell) (on Windows or cross-platform via PowerShell Core)
- Salesforce credentials or configuration (as required by the Python script)

---
## 📦 Installation

Install the required Python packages:

```pip
pip install -r requirements.txt

```

---
## ⚠️ Warning

Before running the Python script, **make sure to update the project name** in the code:

```python
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

Before running the Powershell script, **make sure to update the $sourceFolder and $siteUrl** in the code:

```bash
$sourceFolder = "LOCAL PATH TO THE FOLDER CONTAINING THE PROJECT"
$siteUrl = "https://lendlease.sharepoint.com/sites/*SITENAME*"

```

### ▶️ Run the Powershell Script

This script Uploads metadata to a Sharepoint site.

```bash
.\pnp_migration.ps1

```

