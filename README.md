# Laptop Health Diagnostic Tool

## Overview
The **Laptop Health Diagnostic Tool** is a web-based application that helps you understand the health of your laptop by analyzing HWInfo CSV files. Using a **Random Forest Classifier Model**, it predicts whether your laptop is healthy or shows signs of abnormal performance, and generates a **PDF report** with insights and graphs for easy understanding.

This project was developed to help users—tech-savvy or not—quickly check their laptop’s performance and identify potential issues.

---

## Features
- Upload HWInfo CSV file exported from your system.
- Automatically extract key metrics like CPU, GPU, and memory usage.
- Compare your laptop's metrics against a baseline healthy dataset.
- Predict health status using a Random Forest Classifier ML model.
- Generate a **downloadable PDF report** with detailed analysis and comparison graphs.
- Easy-to-use web interface with step-by-step instructions.

---

## How It Works
1. Export your HWInfo CSV (instructions below).  
2. Upload the CSV file through the web interface.  
3. The system extracts numeric metrics and normalizes the data.  
4. The ML model predicts your laptop’s health status.  
5. A PDF report is generated including:
   - Health status (Healthy / Needs Attention)
   - Key metrics comparison graphs
   - Analysis notes highlighting deviations from healthy values  

---

## How to Get HWInfo CSV
If you don’t know how to export your laptop data from HWInfo:

1. Download and install HWInfo from [https://www.hwinfo.com/](https://www.hwinfo.com/).  
2. Open HWInfo and select **Sensors-only** mode.  
3. Click the **Save** button at the bottom of the sensors window.  
4. Choose CSV format and save the file.  
5. Upload this CSV to the Laptop Health Diagnostic Tool.  

---

## Installation
1. Clone the repository:
```bash
git clone https://github.com/mithunpattabhi/laptop-health-diagnostic.git
cd laptop-health-diagnostic

---


## Website Link:
https://simple-laptop-health-diagnostics.onrender.com/
