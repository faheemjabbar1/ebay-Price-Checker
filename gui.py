#!/usr/bin/env python3
"""
eBay Price Scraper GUI
Interactive widget for searching eBay products and finding the lowest price.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from scraper import EbayScraper


class EbayScraperGUI:
    """GUI application for eBay price scraper."""

    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("eBay Price Scraper")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # Configure style
        style = ttk.Style()
        style.theme_use('clam')

        self.scraper = None
        self.is_scraping = False

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights for responsive layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="🛒 eBay Price Scraper",
            font=("Arial", 18, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))

        # Input Frame
        input_frame = ttk.LabelFrame(main_frame, text="Search Product", padding="10")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)

        # Search entry
        self.search_entry = ttk.Entry(input_frame, font=("Arial", 12))
        self.search_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.search_entry.focus()

        # Bind Enter key to search
        self.search_entry.bind('<Return>', lambda e: self.start_search())

        # Placeholder text
        self.search_entry.insert(0, "Enter product name (e.g., 'iPhone 15 Pro')")
        self.search_entry.bind('<FocusIn>', self.on_entry_click)
        self.search_entry.bind('<FocusOut>', self.on_focusout)
        self.search_entry.config(foreground='grey')

        # Region selector
        region_frame = ttk.Frame(input_frame)
        region_frame.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))

        ttk.Label(region_frame, text="eBay Region:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 10))

        self.region_var = tk.StringVar(value='UK')
        region_combo = ttk.Combobox(
            region_frame,
            textvariable=self.region_var,
            values=['UK', 'US', 'DE', 'FR', 'AU', 'CA'],
            state='readonly',
            width=10
        )
        region_combo.pack(side=tk.LEFT)

        # Store name input
        store_frame = ttk.Frame(input_frame)
        store_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        store_frame.columnconfigure(1, weight=1)

        ttk.Label(store_frame, text="Your Store Name (optional):", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        self.store_entry = ttk.Entry(store_frame, font=("Arial", 10))
        self.store_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        self.store_entry.insert(0, "uniquesellingmart")

        # Headless mode checkbox
        self.headless_var = tk.BooleanVar(value=False)
        headless_check = ttk.Checkbutton(
            input_frame,
            text="Run in headless mode (no browser window)",
            variable=self.headless_var
        )
        headless_check.grid(row=3, column=0, sticky=tk.W, pady=(0, 10))

        # Search button
        self.search_button = ttk.Button(
            input_frame,
            text="🔍 Search eBay",
            command=self.start_search
        )
        self.search_button.grid(row=4, column=0, pady=(0, 5))

        # Progress bar
        self.progress = ttk.Progressbar(
            input_frame,
            mode='indeterminate',
            length=300
        )
        self.progress.grid(row=5, column=0, pady=(10, 0))

        # Status label
        self.status_label = ttk.Label(
            input_frame,
            text="Ready to search",
            font=("Arial", 10)
        )
        self.status_label.grid(row=6, column=0, pady=(5, 0))

        # Results Frame
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Results text area with scrollbar
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            width=60,
            height=15,
            font=("Courier New", 10),
            state='disabled'
        )
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure text tags for colored output
        self.results_text.tag_config("title", foreground="#2E86AB", font=("Arial", 12, "bold"))
        self.results_text.tag_config("price", foreground="#06A77D", font=("Arial", 14, "bold"))
        self.results_text.tag_config("url", foreground="#5E60CE", underline=True)
        self.results_text.tag_config("error", foreground="#D62828", font=("Arial", 11, "bold"))
        self.results_text.tag_config("info", foreground="#6C757D")
        self.results_text.tag_config("success", foreground="#06A77D", font=("Arial", 11, "bold"))

        # Copy URL button (initially hidden)
        self.copy_button = ttk.Button(
            results_frame,
            text="📋 Copy URL to Clipboard",
            command=self.copy_url
        )
        self.current_url = None

    def on_entry_click(self, event):
        """Handle entry click event to remove placeholder."""
        if self.search_entry.get() == "Enter product name (e.g., 'iPhone 15 Pro')":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(foreground='black')

    def on_focusout(self, event):
        """Handle focus out event to restore placeholder if empty."""
        if self.search_entry.get() == "":
            self.search_entry.insert(0, "Enter product name (e.g., 'iPhone 15 Pro')")
            self.search_entry.config(foreground='grey')

    def update_status(self, message):
        """Update the status label."""
        self.status_label.config(text=message)

    def append_result(self, text, tag=None):
        """Append text to the results area."""
        self.results_text.config(state='normal')
        if tag:
            self.results_text.insert(tk.END, text, tag)
        else:
            self.results_text.insert(tk.END, text)
        self.results_text.see(tk.END)
        self.results_text.config(state='disabled')

    def clear_results(self):
        """Clear the results area."""
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state='disabled')
        # Hide copy button
        self.copy_button.grid_remove()
        self.current_url = None

    def copy_url(self):
        """Copy the URL to clipboard."""
        if self.current_url:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_url)
            messagebox.showinfo("Success", "URL copied to clipboard!")

    def start_search(self):
        """Start the scraping process in a separate thread."""
        # Get search term
        search_term = self.search_entry.get().strip()

        # Check if it's the placeholder text
        if search_term == "Enter product name (e.g., 'iPhone 15 Pro')" or not search_term:
            messagebox.showwarning("No Input", "Please enter a product name to search!")
            return

        if self.is_scraping:
            messagebox.showwarning("Busy", "A search is already in progress!")
            return

        # Clear previous results
        self.clear_results()

        # Disable search button
        self.search_button.config(state='disabled')
        self.is_scraping = True

        # Start progress bar
        self.progress.start(10)

        # Update status
        self.update_status(f"Searching for '{search_term}'...")

        # Run scraper in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self.run_scraper, args=(search_term,))
        thread.daemon = True
        thread.start()

    def run_scraper(self, search_term):
        """Run the scraper in a background thread."""
        try:
            # Create scraper instance
            headless = self.headless_var.get()
            region = self.region_var.get()
            store_name = self.store_entry.get().strip() or None

            scraper = EbayScraper(headless=headless, region=region)

            # Run the scraper with optional store name
            result = scraper.scrape(search_term, store_name=store_name)

            # Schedule GUI update in main thread
            self.root.after(0, self.display_results, result, search_term)

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, self.display_error, error_msg)

    def display_results(self, result, search_term):
        """Display the scraping results."""
        # Stop progress bar
        self.progress.stop()

        # Enable search button
        self.search_button.config(state='normal')
        self.is_scraping = False

        if result and 'lowest' in result:
            # Update status
            self.update_status("Search completed successfully!")

            # Display results with formatting
            self.append_result("━" * 60 + "\n")
            self.append_result("  PRICE COMPARISON RESULTS\n", "success")
            self.append_result("━" * 60 + "\n\n")

            # Lowest price
            lowest = result['lowest']
            self.append_result("💰 LOWEST PRICE ON EBAY\n", "success")
            self.append_result("━" * 60 + "\n")
            self.append_result("🏷️  Product:\n", "info")
            self.append_result(f"{lowest['title']}\n\n", "title")
            self.append_result("💵 Price:\n", "info")
            self.append_result(f"{lowest['price']}\n\n", "price")
            self.append_result("🔗 URL:\n", "info")
            self.append_result(f"{lowest['url']}\n\n", "url")

            # Store URL for copying (lowest price URL)
            self.current_url = lowest['url']

            # Your store's price if found
            if 'your_store' in result:
                your_store = result['your_store']
                self.append_result("━" * 60 + "\n")
                self.append_result("🏪 YOUR STORE'S LISTING\n", "info")
                self.append_result("━" * 60 + "\n")
                self.append_result("🏷️  Product:\n", "info")
                self.append_result(f"{your_store['title']}\n\n", "title")
                self.append_result("💵 Your Price:\n", "info")
                self.append_result(f"{your_store['price']}\n\n", "price")
                self.append_result("🔗 Your URL:\n", "info")
                self.append_result(f"{your_store['url']}\n\n", "url")

                # Calculate price difference
                try:
                    lowest_price_val = float(lowest['price'].replace('£', '').replace('$', '').replace(',', '').strip())
                    your_price_val = float(your_store['price'].replace('£', '').replace('$', '').replace(',', '').strip())
                    diff = your_price_val - lowest_price_val

                    self.append_result("━" * 60 + "\n")
                    if diff > 0:
                        self.append_result(f"⚠️  You are £{diff:.2f} MORE expensive than the lowest price\n", "error")
                    elif diff < 0:
                        self.append_result(f"✅ You are £{abs(diff):.2f} CHEAPER than the competition!\n", "success")
                    else:
                        self.append_result("✅ Your price matches the lowest price!\n", "success")
                except:
                    pass

            self.append_result("\n" + "━" * 60 + "\n")

            # Show copy button
            self.copy_button.grid(row=1, column=0, pady=(10, 0))

        else:
            # Update status
            self.update_status("Search failed")

            # Display error message
            self.append_result("━" * 60 + "\n")
            self.append_result("  SEARCH FAILED\n", "error")
            self.append_result("━" * 60 + "\n\n")
            self.append_result(f"Could not find product information for '{search_term}'.\n\n", "info")
            self.append_result("Possible reasons:\n", "info")
            self.append_result("• No results found on eBay\n")
            self.append_result("• Network connection issues\n")
            self.append_result("• eBay page structure changed\n\n")
            self.append_result("Please try:\n", "info")
            self.append_result("• A different search term\n")
            self.append_result("• Checking your internet connection\n")
            self.append_result("• Running the search again\n")

    def display_error(self, error_msg):
        """Display an error message."""
        # Stop progress bar
        self.progress.stop()

        # Enable search button
        self.search_button.config(state='normal')
        self.is_scraping = False

        # Update status
        self.update_status("An error occurred")

        # Display error
        self.append_result("━" * 60 + "\n")
        self.append_result("  ERROR\n", "error")
        self.append_result("━" * 60 + "\n\n")
        self.append_result(f"{error_msg}\n")


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    app = EbayScraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
