# eBay Price Scraper with Playwright

A Python-based web scraper that searches for products on eBay and finds the lowest-priced item. Features a graphical user interface for easy copy/paste and supports multiple eBay regions.

## Features

- 🌍 **Multiple eBay Regions** - Search on eBay UK, US, DE, FR, AU, or CA
- 🖥️ **GUI Interface** - Easy-to-use graphical interface with copy/paste support
- 🔍 **Search for any product** on eBay
- 💰 **Automatically sort** results by lowest price first
- 🎯 **Extract price information** from the lowest-priced item
- 👁️ **Visible browser mode** - watch the scraping happen in real-time (optional)
- 🛡️ **Robust error handling** for network issues and missing elements
- 🍪 **Automatic cookie consent** handling
- ⏱️ **Intelligent delays** to avoid rate limiting
- 📊 **Clean output** with product title, price, and URL

## Project Structure

```
ebay-Price-Checker/
├── scraper.py          # Core scraper logic and CLI
├── gui.py             # Graphical user interface
├── setup.bat          # Windows setup script
├── run_gui.bat        # Windows GUI launcher
├── requirements.txt   # Python dependencies
├── README.md          # This file
└── .gitignore         # Git ignore file
```

## Requirements

- Python 3.7 or higher
- pip (Python package installer)

## Quick Start (Windows)

### 1. One-Click Setup

Double-click **`setup.bat`** in Windows Explorer. This will automatically:

- Create a virtual environment
- Install all dependencies
- Install Chromium browser

Wait for the setup to complete (may take a few minutes).

### 2. Run the GUI

Double-click **`run_gui.bat`** to launch the graphical interface.

#### Using the GUI:

1. Select your eBay region (default: UK)
2. Paste or type your product name
3. Click "🔍 Search eBay" or press Enter
4. Wait for results
5. Click "📋 Copy URL to Clipboard" to copy the product link

## Installation (Manual/Cross-Platform)

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd ebay-Price-Checker
```

### Step 2: Create a Virtual Environment

**On Linux/Mac:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install playwright
playwright install chromium
```

## Usage

### GUI Mode (Recommended)

```bash
python gui.py
```

Or on Windows, just double-click `run_gui.bat`.

### Command-Line Mode

**Method 1: Command-Line Argument**

```bash
python scraper.py "Sheba Select Slices Cat Wet Food"
```

**Method 2: Interactive Input**

```bash
python scraper.py
```

Then enter your search term and region when prompted.

## Supported Regions

- **UK** - eBay.co.uk (default)
- **US** - eBay.com
- **DE** - eBay.de (Germany)
- **FR** - eBay.fr (France)
- **AU** - eBay.com.au (Australia)
- **CA** - eBay.ca (Canada)

## Example Output

```
============================================================
    eBay Price Scraper - Find the Lowest Price
============================================================

🚀 Launching browser...
✅ Browser launched successfully

🔍 Searching eBay UK for: "Sheba Cat Food"
📡 Navigating to https://www.ebay.co.uk...
🍪 Accepting cookie consent...
✅ Cookie consent accepted

⌨️  Typing search term: "wireless headphones"...
🔍 Submitting search...
⏳ Waiting for search results...
✅ Search results loaded successfully

💰 Sorting results by lowest price...
📊 Opening sort menu...
💸 Selecting 'Price + Shipping: lowest first'...
⏳ Waiting for results to reload...
✅ Results sorted by lowest price

🎯 Locating the lowest-priced product...
🖱️  Clicking on the lowest-priced product...
⏳ Waiting for product page to load...
✅ Successfully extracted product information

🔒 Closing browser...

============================================================
                     RESULTS
============================================================
🏷️  Product: Sony WH-1000XM4 Wireless Noise Canceling Headphones
💰 Price: $248.00
🔗 URL: https://www.ebay.com/itm/...
✅ Scraping completed successfully!
============================================================
```

## How It Works

1. **Browser Launch**: Opens a Chromium browser in headed mode (visible)
2. **Navigation**: Goes to eBay.com homepage
3. **Cookie Handling**: Automatically accepts cookie consent if present
4. **Search**: Enters your search term and submits the search
5. **Sorting**: Changes the sort order to "Price + Shipping: lowest first"
6. **Selection**: Clicks on the first product (lowest priced)
7. **Extraction**: Extracts the product title, price, and URL
8. **Display**: Shows the results in a clean format

## Configuration

### Running in Headless Mode

If you want to run the scraper without a visible browser, modify line 254 in `scraper.py`:

```python
# Change this:
scraper = EbayScraper(headless=False)

# To this:
scraper = EbayScraper(headless=True)
```

### Adjusting Delays

The scraper includes delays between actions to:

- Allow you to observe what's happening
- Avoid being rate-limited by eBay

You can adjust these delays in `scraper.py` by modifying the `time.sleep()` values:

- Shorter delays = faster scraping (but higher chance of being blocked)
- Longer delays = slower scraping (but more reliable)

## Troubleshooting

### Issue: "Could not find search box"

**Solution**: eBay may have changed their page structure. The scraper tries multiple selectors, but you may need to update them in the `search_product()` method.

### Issue: "Could not find sort options"

**Solution**: Try running the scraper again. If the issue persists, eBay's sort dropdown selectors may have changed.

### Issue: Browser doesn't launch

**Solutions**:

1. Make sure you ran `playwright install chromium`
2. Check if you have the required system dependencies:
   ```bash
   playwright install-deps chromium
   ```

### Issue: Timeout errors

**Solutions**:

1. Check your internet connection
2. eBay might be slow - try increasing timeout values in the code
3. Your IP might be rate-limited - wait a few minutes and try again

### Issue: "No results found"

**Solution**: Try a different search term. Some very specific searches may return no results.

## Important Notes

### Legal and Ethical Considerations

- ⚖️ **Respect eBay's Terms of Service**: This scraper is for **educational purposes only**
- 🤖 **Check robots.txt**: eBay's robots.txt should be respected
- ⏱️ **Rate Limiting**: The scraper includes delays to avoid overwhelming eBay's servers
- 📚 **Educational Use**: Use this tool to learn about web scraping, not for commercial purposes
- 🔒 **Data Privacy**: Don't store or misuse any data you collect

### Best Practices

- Don't run the scraper too frequently
- Add appropriate delays between requests
- Consider using eBay's official API for production applications
- Be respectful of eBay's resources

## Customization

### Adding More Data Fields

You can extract additional information by modifying the `extract_lowest_price()` method. Possible additions:

- Product condition (new, used, etc.)
- Seller information
- Shipping cost
- Number of items sold
- Product ratings

### Searching Multiple Products

You can modify the script to accept multiple search terms and compare prices:

```python
products = ["wireless headphones", "bluetooth speakers", "gaming mouse"]
for product in products:
    scraper.scrape(product)
```

## Dependencies

- **playwright** (1.40.0): Browser automation framework

## Contributing

Feel free to fork this repository and submit pull requests for improvements!

## License

This project is provided as-is for educational purposes.

## Disclaimer

This tool is intended for educational purposes only. The authors are not responsible for any misuse of this software. Always respect website terms of service and robots.txt files. Consider using official APIs when available.

## Support

If you encounter issues:

1. Check the Troubleshooting section above
2. Make sure all dependencies are installed correctly
3. Verify your Python version (3.7+)
4. Check that Playwright browsers are installed

## Future Enhancements

Possible improvements for future versions:

- [ ] Export results to CSV or JSON
- [ ] Compare prices across multiple platforms
- [ ] Email notifications for price drops
- [ ] Support for other eBay regions (ebay.co.uk, ebay.de, etc.)
- [ ] Filter by condition (new, used, refurbished)
- [ ] Track price history over time
- [ ] Support for pagination (checking multiple pages of results)

---

**Happy Scraping! 🎉**
