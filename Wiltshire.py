from playwright.sync_api import sync_playwright
import time
import csv
from datetime import datetime

def scrape_all_planning_comments():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        all_comments = []
        page_num = 1
        
        try:
            print("Navigating to planning page...")
            page.goto('https://development.wiltshire.gov.uk/pr/s/planning-application/a0iQ3000006yo9lIAA/pl202405527?tabset-8903c=3', wait_until='networkidle')
            
            while True:
                print(f"Scraping page {page_num}...")
                
                # Wait for the page content to load
                page.wait_for_selector('tr[role="row"]', timeout=15000)
                time.sleep(3)
                
                # Scrape comments from current page
                page_comments = scrape_comments_from_page(page)
                all_comments.extend(page_comments)
                
                print(f"Found {len(page_comments)} comments on page {page_num}")
                
                # Try to find and click next page button using the correct selector
                next_button = page.query_selector('button.slds-button:has-text("Next")')
                
                if next_button and not next_button.get_attribute('disabled'):
                    print("Moving to next page...")
                    next_button.click()
                    page_num += 1
                    time.sleep(3)  # Wait for next page to load
                else:
                    print("No more pages available or next button is disabled.")
                    break
                    
        except Exception as e:
            print(f"Error during scraping: {e}")
        finally:
            browser.close()
        
        return all_comments

def scrape_comments_from_page(page):
    """Extract comments from the current page"""
    comments_data = []
    
    try:
        # Find all comment rows
        comment_rows = page.query_selector_all('tr[role="row"]')
        print(f"Processing {len(comment_rows)} rows on current page...")
        
        for i, row in enumerate(comment_rows):
            try:
                # Extract name
                name_el = row.query_selector('th[data-label="Name"] lightning-formatted-url a')
                name = name_el.inner_text().strip() if name_el else "Unknown"
                
                # Extract date
                date_el = row.query_selector('td[data-label="Date"] lightning-base-formatted-text')
                date = date_el.inner_text().strip() if date_el else "Unknown date"
                
                # Extract comment
                comment_el = row.query_selector('td[data-label="Comment"] lightning-base-formatted-text')
                comment = comment_el.inner_text().strip() if comment_el else None
                
                # Only add if we have a comment
                if comment and name != "Unknown":
                    comments_data.append({
                        'commenter': name,
                        'date': date,
                        'comment': comment
                    })
                    
            except Exception as e:
                print(f"Error processing row {i}: {e}")
                continue
                
    except Exception as e:
        print(f"Error scraping page: {e}")
    
    return comments_data

def save_comments_to_csv(comments, filename=None):
    """Save comments to CSV file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"planning_comments_all_pages_{timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['commenter', 'date', 'comment'])
        writer.writeheader()
        for comment in comments:
            writer.writerow(comment)
    
    print(f"All comments saved to {filename}")
    return filename

def print_summary(comments):
    """Print a summary of the scraping results"""
    print("\n" + "="*60)
    print("SCRAPING SUMMARY")
    print("="*60)
    print(f"Total comments scraped: {len(comments)}")
    
    if comments:
        # Get unique commenters
        unique_commenters = set(comment['commenter'] for comment in comments)
        print(f"Unique commenters: {len(unique_commenters)}")
        
        # Date range
        dates = [comment['date'] for comment in comments if comment['date'] != 'Unknown date']
        if dates:
            print(f"Date range: {min(dates)} to {max(dates)}")
        
        # Show first few comments as preview
        print("\nFirst 3 comments preview:")
        print("-" * 40)
        for i, comment in enumerate(comments[:3], 1):
            print(f"{i}. {comment['commenter']} - {comment['date']}")
            print(f"   {comment['comment'][:100]}...")
            print()

if __name__ == "__main__":
    print("Starting to scrape all comments from all pages...")
    
    # Scrape all comments from all pages
    all_comments = scrape_all_planning_comments()
    
    if all_comments:
        # Save to CSV
        csv_filename = save_comments_to_csv(all_comments)
        
        # Print summary
        print_summary(all_comments)
        
        print(f"\nScraping completed successfully!")
        print(f"File saved: {csv_filename}")
    else:
        print("No comments were found.")
