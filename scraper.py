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

    # eBay region URLs
    EBAY_REGIONS = {
        'UK': 'https://www.ebay.co.uk',
        'US': 'https://www.ebay.com',
        'DE': 'https://www.ebay.de',
        'FR': 'https://www.ebay.fr',
        'AU': 'https://www.ebay.com.au',
        'CA': 'https://www.ebay.ca',
    }

    def __init__(self, headless=False, region='UK'):
        """
        Initialize the scraper.

        Args:
            headless (bool): Whether to run browser in headless mode (default: False for visible browser)
            region (str): eBay region to search (default: 'UK')
        """
        self.headless = headless
        self.region = region
        self.ebay_url = self.EBAY_REGIONS.get(region, self.EBAY_REGIONS['UK'])
        self.browser = None
        self.page = None
        self.playwright = None
        self.context = None

    def start(self):
        """Start the browser and create a new page."""
        import os
        print("🚀 Launching browser...")
        self.playwright = sync_playwright().start()

        # Launch browser in headed mode with a reasonable viewport size
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=['--start-maximized']  # Start browser maximized
        )

        # Set geolocation and locale based on region
        geolocation_settings = {
            'UK': {'latitude': 51.5074, 'longitude': -0.1278, 'locale': 'en-GB'},  # London
            'US': {'latitude': 37.7749, 'longitude': -122.4194, 'locale': 'en-US'},  # San Francisco
            'DE': {'latitude': 52.5200, 'longitude': 13.4050, 'locale': 'de-DE'},  # Berlin
            'FR': {'latitude': 48.8566, 'longitude': 2.3522, 'locale': 'fr-FR'},  # Paris
            'AU': {'latitude': -33.8688, 'longitude': 151.2093, 'locale': 'en-AU'},  # Sydney
            'CA': {'latitude': 43.6532, 'longitude': -79.3832, 'locale': 'en-CA'},  # Toronto
        }

        region_settings = geolocation_settings.get(self.region, geolocation_settings['UK'])

        # Path to store cookies
        cookies_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'browser_data')
        os.makedirs(cookies_dir, exist_ok=True)
        cookies_file = os.path.join(cookies_dir, f'ebay_{self.region.lower()}_cookies.json')

        # Create a new browser context with custom settings
        context_options = {
            'viewport': {'width': 1280, 'height': 720},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'locale': region_settings['locale'],
            'geolocation': {
                'latitude': region_settings['latitude'],
                'longitude': region_settings['longitude']
            },
            'permissions': ['geolocation'],
        }

        # Load saved cookies if they exist
        if os.path.exists(cookies_file):
            print(f"📂 Loading saved cookies for {self.region}...")
            context_options['storage_state'] = cookies_file

        self.context = self.browser.new_context(**context_options)
        self.page = self.context.new_page()
        self.cookies_file = cookies_file

        print(f"✅ Browser launched successfully (Location: {self.region})\n")

    def close(self):
        """Close the browser and cleanup resources."""
        # Save cookies before closing
        if self.context and hasattr(self, 'cookies_file'):
            try:
                print("💾 Saving cookies for next session...")
                self.context.storage_state(path=self.cookies_file)
                print(f"✅ Cookies saved to {self.cookies_file}")
            except Exception as e:
                print(f"⚠️  Could not save cookies: {str(e)}")

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

    def set_delivery_location(self):
        """Set the delivery location based on the region."""
        try:
            # For UK, set a UK postcode
            region_postcodes = {
                'UK': 'SW1A 1AA',  # London postcode
                'US': '10001',  # New York ZIP
                'DE': '10115',  # Berlin postcode
                'FR': '75001',  # Paris postcode
                'AU': '2000',  # Sydney postcode
                'CA': 'M5H 2N2',  # Toronto postcode
            }

            postcode = region_postcodes.get(self.region, region_postcodes['UK'])

            print(f"📍 Setting delivery location to {self.region} ({postcode})...")

            # Try to set location via cookie/localStorage
            # This simulates eBay's location cookie
            self.page.evaluate(f"""
                localStorage.setItem('ebay_postcode', '{postcode}');
                localStorage.setItem('ebay_country', '{self.region}');
            """)

            print(f"✅ Delivery location set to {self.region}\n")
            return True

        except Exception as e:
            print(f"⚠️  Could not set delivery location: {str(e)}")
            return False

    def search_product(self, search_term):
        """
        Search for a product on eBay.

        Args:
            search_term (str): The product to search for

        Returns:
            bool: True if search was successful, False otherwise
        """
        try:
            print(f"🔍 Searching eBay {self.region} for: \"{search_term}\"")

            # Navigate to eBay homepage
            print(f"📡 Navigating to {self.ebay_url}...")
            self.page.goto(self.ebay_url, timeout=30000)
            time.sleep(2)  # Wait to see the homepage

            # Handle cookie consent if present
            self.handle_cookie_consent()

            # Set delivery location
            self.set_delivery_location()

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
            try:
                # Try to wait for network idle, but don't fail if it times out
                self.page.wait_for_load_state('domcontentloaded', timeout=10000)
                print("✅ Page loaded")
            except:
                print("⚠️  Page still loading, but continuing...")

            time.sleep(3)  # Give it extra time to fully load

            # Debug: Print current URL to see where we are
            current_url = self.page.url
            print(f"📍 Current URL: {current_url}")

            # Check if we have results
            no_results_selectors = [
                'text="No exact matches found"',
                'text="0 results"',
                '.srp-save-null-search',
                'text="No results found"'
            ]

            for selector in no_results_selectors:
                try:
                    if self.page.locator(selector).is_visible(timeout=1000):
                        print(f"❌ No results found for \"{search_term}\"")
                        return False
                except:
                    continue

            # Verify we actually have product listings
            try:
                # Wait a bit for products to appear
                print("🔍 Waiting for product listings to appear...")
                self.page.wait_for_selector('li.s-card, .s-item', timeout=10000)
                products = self.page.locator('li.s-card, .s-item').count()
                print(f"📊 Found {products} product listings")
                if products == 0:
                    print("❌ No product listings found on page")
                    # Take a screenshot for debugging
                    try:
                        self.page.screenshot(path='debug_search_results.png')
                        print("📸 Screenshot saved to debug_search_results.png")
                    except:
                        pass
                    return False
            except Exception as e:
                print(f"⚠️  Error checking for products: {str(e)}")
                print("⚠️  Could not find products, but continuing...")

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
        Sort search results by lowest price first by manipulating the URL.

        Returns:
            bool: True if sorting was successful, False otherwise
        """
        try:
            print("💰 Sorting results by lowest price...")

            # Get current URL
            current_url = self.page.url
            print(f"🔍 Current URL: {current_url}")

            # Parse URL and parameters
            from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

            parsed = urlparse(current_url)
            params = parse_qs(parsed.query, keep_blank_values=True)

            # Add or update the sort parameter
            params['_sop'] = ['15']  # Price + Shipping: lowest first

            # Remove tracking parameters that might interfere
            params.pop('_trksid', None)

            # Rebuild the query string
            new_query = urlencode(params, doseq=True)
            new_url = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment
            ))

            print(f"🔗 New sorted URL: {new_url}")

            # Navigate to the sorted URL
            print("🔗 Navigating to sorted results...")
            self.page.goto(new_url, timeout=30000)

            # Wait for the page to load
            print("⏳ Waiting for sorted results to load...")
            self.page.wait_for_load_state('networkidle', timeout=15000)
            time.sleep(2)  # Wait to see the sorted results

            # Verify the sort parameter is in the final URL
            final_url = self.page.url
            if '_sop=15' in final_url:
                print("✅ Results sorted by lowest price (_sop=15 confirmed)\n")
            else:
                print("⚠️  Sort parameter may not have persisted, but continuing...\n")

            return True

        except PlaywrightTimeoutError:
            print("❌ Error: Timeout while sorting results")
            return False
        except Exception as e:
            print(f"❌ Error during sorting: {str(e)}")
            return False

    def extract_lowest_price(self, store_name=None):
        """
        Extract the lowest price and optionally a specific store's price.

        Args:
            store_name (str): Optional store name to find (e.g., 'uniquesellingmart')

        Returns:
            dict: Dictionary containing lowest price info and optional store price, or None if extraction failed
        """
        try:
            print("🎯 Locating the first product (iid:1)...")

            # Find the first listing item with data-view containing iid:1
            first_item = self.page.locator('li[data-view*="iid:1"]').first

            if first_item.count() == 0:
                print("❌ Error: Could not find first item (iid:1)")
                return None

            print("✅ Found first item (iid:1)")

            # Find the clickable link element (the <a> tag containing the title)
            link_selectors = [
                'a.s-card__link[href*="/itm/"]',
                'a.s-item__link'
            ]

            clickable_link = None
            for selector in link_selectors:
                try:
                    elem = first_item.locator(selector).first
                    if elem.count() > 0:
                        clickable_link = elem
                        print(f"✅ Found clickable link with selector: {selector}")
                        break
                except Exception as e:
                    print(f"⚠️  Selector {selector} failed: {str(e)}")
                    continue

            if not clickable_link:
                print("❌ Error: Could not find clickable link element")
                return None

            # Get title text from inside the link
            try:
                title_elem = clickable_link.locator('.su-styled-text, .s-card__title, .s-item__title').first
                if title_elem.count() > 0:
                    title_text = title_elem.text_content().strip()
                else:
                    # Fallback to link text
                    title_text = clickable_link.text_content().strip()[:100]  # First 100 chars
            except:
                title_text = "Product Title"

            print(f"📝 Product title: {title_text}")

            # Extract listing ID from the parent li element's data-listingid attribute
            listing_id = first_item.get_attribute('data-listingid')

            if listing_id:
                # Construct clean URL using listing ID
                product_url = f"{self.ebay_url}/itm/{listing_id}"
                print(f"📝 Listing ID: {listing_id}")
                print(f"🔗 Product URL: {product_url}")
            else:
                # Fallback to href attribute
                product_url = clickable_link.get_attribute('href')
                print(f"🔗 Product URL (from href): {product_url}")

            print("🖱️  Navigating to product page...")
            self.page.goto(product_url, timeout=30000)

            # Wait for product page to load
            print("⏳ Waiting for product page to load...")
            try:
                self.page.wait_for_load_state('domcontentloaded', timeout=10000)
                print("✅ Product page loaded")
            except:
                print("⚠️  Page loading slowly, but continuing...")

            time.sleep(3)  # Extra wait for dynamic content

            # Extract price from product page
            print("💰 Extracting price from product page...")

            price_selectors = [
                '.x-bin-price__content .x-price-primary span.ux-textspans',
                '.x-price-primary span.ux-textspans',
                '.x-price-primary span',
                '#prcIsum'
            ]

            product_price = None
            for selector in price_selectors:
                try:
                    price_elem = self.page.locator(selector).first
                    if price_elem.is_visible(timeout=3000):
                        price_text = price_elem.text_content().strip()
                        product_price = self.clean_price(price_text)
                        if product_price:
                            print(f"✅ Found price: {product_price}")
                            break
                except:
                    continue

            if not product_price:
                print("❌ Error: Could not extract price from product page")
                return None

            product_url = self.page.url

            lowest_price_info = {
                'title': title_text,
                'price': product_price,
                'url': product_url
            }

            print(f"✅ Lowest price: {product_price} - {title_text}")

            result = {
                'lowest': lowest_price_info
            }

            # If store name provided, go back and find that store's listing
            if store_name:
                print(f"\n🔙 Going back to search results...")
                self.page.go_back()
                self.page.wait_for_load_state('networkidle', timeout=15000)
                time.sleep(2)

                print(f"🏪 Looking for store: {store_name}...")

                # Find all listing items
                all_items = self.page.locator('li.s-card, li.s-item')

                # Search through items for the store
                for i in range(min(all_items.count(), 50)):
                    try:
                        item = all_items.nth(i)
                        item_html = item.inner_html()

                        # Check if this listing is from the target store
                        if store_name.lower() in item_html.lower():
                            print(f"✅ Found {store_name} listing at position {i + 1}")

                            # Find and click the link (not just the title)
                            store_link = None
                            for link_selector in ['a.s-card__link[href*="/itm/"]', 'a.s-item__link']:
                                try:
                                    elem = item.locator(link_selector).first
                                    if elem.count() > 0:
                                        store_link = elem
                                        break
                                except:
                                    continue

                            if store_link and store_link.count() > 0:
                                # Get title
                                try:
                                    title_elem = store_link.locator('.su-styled-text, .s-card__title, .s-item__title').first
                                    if title_elem.count() > 0:
                                        store_title = title_elem.text_content().strip()
                                    else:
                                        store_title = store_link.text_content().strip()[:100]
                                except:
                                    store_title = "Store Product"

                                print(f"📝 Store product: {store_title}")

                                # Extract listing ID from the parent li element's data-listingid attribute
                                store_listing_id = item.get_attribute('data-listingid')

                                if store_listing_id:
                                    # Construct clean URL using listing ID
                                    store_url = f"{self.ebay_url}/itm/{store_listing_id}"
                                    print(f"📝 Store Listing ID: {store_listing_id}")
                                    print(f"🔗 Store product URL: {store_url}")
                                else:
                                    # Fallback to href attribute
                                    store_url = store_link.get_attribute('href')
                                    print(f"🔗 Store product URL (from href): {store_url}")

                                print("🖱️  Navigating to store product page...")
                                self.page.goto(store_url, timeout=30000)

                                try:
                                    self.page.wait_for_load_state('domcontentloaded', timeout=10000)
                                    print("✅ Store product page loaded")
                                except:
                                    print("⚠️  Page loading slowly, but continuing...")

                                time.sleep(3)

                                # Extract price from store's product page
                                store_price = None
                                for selector in price_selectors:
                                    try:
                                        price_elem = self.page.locator(selector).first
                                        if price_elem.is_visible(timeout=3000):
                                            price_text = price_elem.text_content().strip()
                                            store_price = self.clean_price(price_text)
                                            if store_price:
                                                print(f"✅ Store price: {store_price}")
                                                break
                                    except:
                                        continue

                                if store_price:
                                    result['your_store'] = {
                                        'title': store_title,
                                        'price': store_price,
                                        'url': self.page.url
                                    }
                                break
                    except Exception as e:
                        print(f"⚠️  Error checking item {i}: {str(e)}")
                        continue

                if 'your_store' not in result:
                    print(f"⚠️  Could not find listing from store: {store_name}")

            print("\n✅ Successfully extracted price information\n")
            return result

        except PlaywrightTimeoutError:
            print("❌ Error: Timeout while extracting prices")
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

    def scrape(self, search_term, store_name=None):
        """
        Main scraping method that orchestrates the entire process.

        Args:
            search_term (str): The product to search for
            store_name (str): Optional store name to find your listing

        Returns:
            dict: Product information or None if scraping failed
        """
        try:
            # Start the browser
            self.start()

            # Search for the product
            if not self.search_product(search_term):
                return None

            # Sort results by lowest price
            if not self.sort_by_lowest_price():
                print("⚠️  Sorting failed, but continuing with unsorted results...")

            # Extract the lowest price and optionally the store's price
            result = self.extract_lowest_price(store_name=store_name)

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

    # Ask for region
    print("\nAvailable regions: UK, US, DE, FR, AU, CA")
    region = input("Enter eBay region (default: UK): ").strip().upper()
    if not region:
        region = 'UK'

    if region not in EbayScraper.EBAY_REGIONS:
        print(f"⚠️  Unknown region '{region}', using UK instead")
        region = 'UK'

    # Create scraper instance (headed mode by default)
    scraper = EbayScraper(headless=False, region=region)

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
