import requests
from bs4 import BeautifulSoup
import pandas as pd
import html

# List all URLs you want to scrape
urls = [
    "https://apps.northlincs.gov.uk/application/pa-2025-643",
    "https://apps.northlincs.gov.uk/application/pa-scr-2025-5",
    "https://apps.northlincs.gov.uk/application/pa-2024-584"
]

data = []

for url in urls:
    r = requests.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    rows = soup.select("tr")
    for row in rows:
        try:
            first_td = row.find("strong")
            if not first_td or first_td.text.strip() != "Web":
                continue

            view_button = row.find("a", class_="btn btn-primary")
            if not view_button or "showData(" not in view_button.get("onclick", ""):
                continue

            onclick_attr = view_button["onclick"]
            start = onclick_attr.find("showData('") + len("showData('")
            end = onclick_attr.rfind("')")
            comment_html = onclick_attr[start:end]
            comment_text = html.unescape(comment_html)

            tds = row.find_all("td")
            commenter_name = tds[1].text.strip() if len(tds) > 1 else ""
            comment_date = tds[2].text.strip() if len(tds) > 2 else ""

            data.append({
                "URL": url,
                "Name": commenter_name,
                "Date": comment_date,
                "Comment": comment_text
            })

        except Exception:
            continue

df = pd.DataFrame(data, columns=["URL", "Name", "Date", "Comment"])
df.to_csv("northlincs_web_comments.csv", index=False)
print(f"Scraping complete. {len(df)} comments saved.")
