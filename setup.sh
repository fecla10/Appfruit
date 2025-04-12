#!/bin/bash

# Make sure we pip install the requirements.txt
pip install -r requirements.txt

# Install plotly and its dependencies explicitly
pip install plotly==5.13.1 packaging numpy pandas --upgrade 