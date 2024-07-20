# facebook-ads-scraper

This repository contains a Python-based tool for scraping advertisement data from the Facebook Ads Library, focusing on various advertisers. The script uses Selenium to automate web scraping and retrieve detailed ad information, including platforms used, spending amounts, impressions, links, and media content (vvideos or pictures). It is designed to handle multiple advertiser IDs concurrently using multithreading.

## Features

- **Concurrent Scraping:** Utilizes a ThreadPool to handle multiple advertiser IDs simultaneously.
- **Detailed Ad Information:** Extracts comprehensive details for each ad, including platforms (Facebook, Instagram, Messenger, Audience Network), spending amounts, impressions, links, and media content.
- **Robust Web Scraping:** Implements error handling for common Selenium exceptions to ensure smooth scraping.
- **Data Export:** Saves the scraped data into CSV files for further analysis and processing.

## Dependencies

- `selenium`
- `pandas`
- `multiprocessing`

## Usage

1. **Install the necessary packages:**
   ```bash
   pip install selenium pandas
   ```

2. **Set up the WebDriver:**
   Ensure you have the appropriate WebDriver (e.g., ChromeDriver) installed and available in your PATH.

3. **Update Advertiser IDs:**
   Modify the `adv_ids` list with the advertiser IDs you want to scrape in the script.

4. **Run the script:**
   ```python
   python scrape_ads.py
   ```
