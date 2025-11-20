#!/usr/bin/env python3
"""
eBay Price Scraper using Playwright
This script searches for products on eBay and finds the lowest-priced item.
"""

import sys
import time
import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


class EbayScraper:
    """eBay web scraper for finding the lowest-priced products."""

    def __init__(self, headless=False):
        """
        Initialize the scraper.

        Args:
            headless (bool): Whether to run browser in headless mode (default: False for visible browser)
        """
        self.headless = headless
        self.browser = None
        self.page = None
        self.playwright = None

    def start(self):
        """Start the browser and create a new page."""
        print("🚀 Launching browser...")
        self.playwright = sync_playwright().start()

        # Launch browser in headed mode with a reasonable viewport size
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=['--start-maximized']  # Start browser maximized
        )

        # Create a new browser context with custom viewport
        context = self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        self.page = context.new_page()
        print("✅ Browser launched successfully\n")

    def close(self):
        """Close the browser and cleanup resources."""
        if self.browser:
            print("\n🔒 Closing browser...")
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def handle_cookie_consent(self):
        """Handle cookie consent popup if it appears."""
        try:
            # Wait for cookie consent button (with short timeout)
            # Common eBay cookie consent button selectors
            cookie_selectors = [
                'button#gdpr-banner-accept',
                'button[id*="accept"]',
                'button[class*="gdpr-banner-accept"]',
                '#gdpr-banner-accept'
            ]

            for selector in cookie_selectors:
                try:
                    if self.page.locator(selector).is_visible(timeout=2000):
                        print("🍪 Accepting cookie consent...")
                        self.page.click(selector, timeout=2000)
                        time.sleep(1)
                        print("✅ Cookie consent accepted\n")
                        return
                except:
                    continue

        except Exception as e:
            # If no cookie popup found, continue silently
            pass

    def search_product(self, search_term):
        """
        Search for a product on eBay.

        Args:
            search_term (str): The product to search for

        Returns:
            bool: True if search was successful, False otherwise
        """
        try:
            print(f"🔍 Searching eBay for: \"{search_term}\"")

            # Navigate to eBay homepage
            print("📡 Navigating to eBay.com...")
            self.page.goto("https://www.ebay.com", timeout=30000)
            time.sleep(2)  # Wait to see the homepage

            # Handle cookie consent if present
            self.handle_cookie_consent()

            # Find the search bar (eBay uses input with type="text" and various possible selectors)
            search_selectors = [
                'input[type="text"][placeholder*="Search"]',
                'input[name="__nkw"]',
                'input#gh-ac',
                'input[placeholder="Search for anything"]'
            ]

            search_box = None
            for selector in search_selectors:
                try:
                    if self.page.locator(selector).is_visible(timeout=3000):
                        search_box = selector
                        break
                except:
                    continue

            if not search_box:
                print("❌ Error: Could not find search box")
                return False

            # Fill in the search term
            print(f"⌨️  Typing search term: \"{search_term}\"...")
            self.page.fill(search_box, search_term)
            time.sleep(1)  # Wait to see the typing

            # Submit the search (look for search button)
            search_button_selectors = [
                'input[type="submit"][value="Search"]',
                'button[type="submit"]',
                'input#gh-btn',
                'input.btn-prim'
            ]

            search_button = None
            for selector in search_button_selectors:
                try:
                    if self.page.locator(selector).is_visible(timeout=2000):
                        search_button = selector
                        break
                except:
                    continue

            if search_button:
                print("🔍 Submitting search...")
                self.page.click(search_button)
            else:
                # Fallback: press Enter
                print("🔍 Submitting search (pressing Enter)...")
                self.page.press(search_box, 'Enter')

            # Wait for search results to load
            print("⏳ Waiting for search results...")
            self.page.wait_for_load_state('networkidle', timeout=15000)
            time.sleep(2)  # Wait to see the results

            # Check if we have results
            no_results_selectors = [
                'text="No exact matches found"',
                'text="0 results"',
                '.srp-save-null-search'
            ]

            for selector in no_results_selectors:
                try:
                    if self.page.locator(selector).is_visible(timeout=1000):
                        print(f"❌ No results found for \"{search_term}\"")
                        return False
                except:
                    continue

            print("✅ Search results loaded successfully\n")
            return True

        except PlaywrightTimeoutError:
            print("❌ Error: Timeout while searching. eBay might be slow or unreachable.")
            return False
        except Exception as e:
            print(f"❌ Error during search: {str(e)}")
            return False

    def sort_by_lowest_price(self):
        """
        Sort search results by lowest price first.

        Returns:
            bool: True if sorting was successful, False otherwise
        """
        try:
            print("💰 Sorting results by lowest price...")

            # eBay uses a sort dropdown - common selectors
            sort_selectors = [
                'button[aria-label*="Sort selector"]',
                'button[aria-label*="Sort"]',
                'select.srp-sort-select',
                'button.srp-controls__control--highlighted',
                'button:has-text("Sort")',
            ]

            sort_button = None
            for selector in sort_selectors:
                try:
                    if self.page.locator(selector).first.is_visible(timeout=3000):
                        sort_button = selector
                        break
                except:
                    continue

            if not sort_button:
                print("⚠️  Could not find sort button, trying alternative method...")
                # Try to find the sort dropdown directly
                try:
                    self.page.select_option('select.srp-controls__control', label='Price + Shipping: lowest first')
                    time.sleep(2)
                    print("✅ Sorted by lowest price (using dropdown)\n")
                    return True
                except:
                    print("❌ Error: Could not find sort options")
                    return False

            # Click the sort button to open dropdown
            print("📊 Opening sort menu...")
            self.page.click(sort_button)
            time.sleep(1.5)  # Wait for dropdown to appear

            # Look for "lowest price" option in the dropdown
            price_option_selectors = [
                'a:has-text("Price + Shipping: lowest first")',
                'li:has-text("Price + Shipping: lowest first")',
                'a:has-text("Lowest Price")',
                'span:has-text("Price + Shipping: lowest first")',
            ]

            price_option = None
            for selector in price_option_selectors:
                try:
                    if self.page.locator(selector).first.is_visible(timeout=2000):
                        price_option = selector
                        break
                except:
                    continue

            if not price_option:
                print("❌ Error: Could not find lowest price sorting option")
                return False

            # Click on the lowest price option
            print("💸 Selecting 'Price + Shipping: lowest first'...")
            self.page.click(price_option)

            # Wait for the page to reload with sorted results
            print("⏳ Waiting for results to reload...")
            self.page.wait_for_load_state('networkidle', timeout=15000)
            time.sleep(2)  # Wait to see the sorted results

            print("✅ Results sorted by lowest price\n")
            return True

        except PlaywrightTimeoutError:
            print("❌ Error: Timeout while sorting results")
            return False
        except Exception as e:
            print(f"❌ Error during sorting: {str(e)}")
            return False

    def extract_lowest_price(self):
        """
        Click on the first product and extract its price.

        Returns:
            dict: Dictionary containing price, title, and URL, or None if extraction failed
        """
        try:
            print("🎯 Locating the lowest-priced product...")

            # Find the first product listing
            # eBay search results are typically in list items with class containing 's-item'
            product_selectors = [
                '.s-item__link',
                '.s-item__wrapper a.s-item__link',
                '.srp-results .s-item a',
            ]

            first_product = None
            for selector in product_selectors:
                try:
                    products = self.page.locator(selector)
                    if products.count() > 0:
                        # Skip the first one if it's a sponsored/featured item
                        # Usually the first real product is at index 0 or 1
                        first_product = products.first
                        break
                except:
                    continue

            if not first_product:
                print("❌ Error: Could not find any product listings")
                return None

            # Get the product URL before clicking
            product_url = first_product.get_attribute('href')

            # Click on the first product
            print("🖱️  Clicking on the lowest-priced product...")
            first_product.click()
            time.sleep(2)  # Wait to see the product page loading

            # Wait for the product page to load
            print("⏳ Waiting for product page to load...")
            self.page.wait_for_load_state('networkidle', timeout=15000)
            time.sleep(2)  # Wait to see the product page

            # Extract the product title
            title_selectors = [
                '.x-item-title__mainTitle',
                'h1.x-item-title__mainTitle',
                '.it-ttl',
                'h1[class*="title"]',
            ]

            product_title = "Unknown Product"
            for selector in title_selectors:
                try:
                    if self.page.locator(selector).is_visible(timeout=3000):
                        product_title = self.page.locator(selector).text_content().strip()
                        break
                except:
                    continue

            # Extract the price
            price_selectors = [
                '.x-price-primary span',
                '.x-price-primary',
                '#prcIsum',
                '.x-bin-price__content .ux-textspans',
                'div[class*="price"] span[class*="ux-textspans"]',
            ]

            product_price = None
            for selector in price_selectors:
                try:
                    if self.page.locator(selector).first.is_visible(timeout=3000):
                        price_text = self.page.locator(selector).first.text_content().strip()
                        # Clean up the price text
                        product_price = self.clean_price(price_text)
                        if product_price:
                            break
                except:
                    continue

            if not product_price:
                print("❌ Error: Could not extract product price")
                return None

            print("✅ Successfully extracted product information\n")

            return {
                'title': product_title,
                'price': product_price,
                'url': product_url or self.page.url
            }

        except PlaywrightTimeoutError:
            print("❌ Error: Timeout while loading product page")
            return None
        except Exception as e:
            print(f"❌ Error during price extraction: {str(e)}")
            return None

    def clean_price(self, price_text):
        """
        Clean and format the price text.

        Args:
            price_text (str): Raw price text from the page

        Returns:
            str: Cleaned price or None if invalid
        """
        if not price_text:
            return None

        # Remove extra whitespace
        price_text = price_text.strip()

        # Use regex to extract price (handles formats like $XX.XX, $X,XXX.XX, etc.)
        # Look for currency symbol followed by numbers
        price_pattern = r'[\$£€¥]?\s*[\d,]+\.?\d{0,2}'
        match = re.search(price_pattern, price_text)

        if match:
            price = match.group(0).strip()
            # Ensure it starts with a currency symbol
            if not price.startswith(('$', '£', '€', '¥')):
                price = '$' + price
            return price

        return None

    def scrape(self, search_term):
        """
        Main scraping method that orchestrates the entire process.

        Args:
            search_term (str): The product to search for

        Returns:
            dict: Product information or None if scraping failed
        """
        try:
            # Start the browser
            self.start()

            # Search for the product
            if not self.search_product(search_term):
                return None

            # Sort by lowest price
            if not self.sort_by_lowest_price():
                print("⚠️  Warning: Could not sort by price, continuing with default sort...")

            # Extract the lowest price
            result = self.extract_lowest_price()

            # Wait a bit before closing so user can see the final result
            time.sleep(3)

            return result

        finally:
            # Always close the browser
            self.close()


def main():
    """Main entry point for the script."""
    print("=" * 60)
    print("    eBay Price Scraper - Find the Lowest Price")
    print("=" * 60)
    print()

    # Get search term from command line or user input
    if len(sys.argv) > 1:
        # Use command line argument
        search_term = ' '.join(sys.argv[1:])
    else:
        # Prompt user for input
        search_term = input("Enter the product you want to search for: ").strip()

    if not search_term:
        print("❌ Error: Please provide a search term")
        sys.exit(1)

    # Create scraper instance (headed mode by default)
    scraper = EbayScraper(headless=False)

    try:
        # Run the scraper
        result = scraper.scrape(search_term)

        # Display results
        print()
        print("=" * 60)
        print("                     RESULTS")
        print("=" * 60)

        if result:
            print(f"🏷️  Product: {result['title']}")
            print(f"💰 Price: {result['price']}")
            print(f"🔗 URL: {result['url']}")
            print()
            print("✅ Scraping completed successfully!")
        else:
            print("❌ Could not find product information")
            sys.exit(1)

        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
