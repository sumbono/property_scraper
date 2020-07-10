# Maxwellbayne Scraper
This app created using Python with Selenium framework.

This app scraping properties detail information from maxwellbaynes website and export it to JSON and CSV file.

## Prerequisite
Install python on your machine. You can use [python](https://www.python.org/) or [anaconda](https://www.anaconda.com/).

Install all libraries needed:
```bash
#if using pip:
pip install selenium
pip install pandas
pip install tqdm
```

Selenium will need a browser driver for running. In this code we are using Chromedriver, and the Chrome browser should have installed on your machine.

To download Chromedriver visit this url:
```bash
https://sites.google.com/a/chromium.org/chromedriver/home 
```
Use the same version as your Chrome browser.

Follow the Chromedriver installation instruction in: chromedriver_installation_instruction.txt

## Run the script
Make sure that all preprequisite and Chromedriver was installed on your machine.

On your command line:
```bash
python maxwellbaynes_scraper_new.py
```