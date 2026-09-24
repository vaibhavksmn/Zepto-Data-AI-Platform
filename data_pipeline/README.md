# Zepto Catalog Pipeline - Module 1

## Overview
This module extracts book catalog data from `books.toscrape.com`, cleans the raw text, enriches it with a fixed currency conversion rate, and loads it into a normalized SQLite database. 

## Setup & Installation
1. Ensure Python 3.9+ is installed.
2. Install the required dependencies:
   ```bash
   pip install requests beautifulsoup4 pandas nump
   python pipeline.py
