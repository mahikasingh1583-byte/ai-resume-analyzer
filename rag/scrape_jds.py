"""
rag/scrape_jds.py
Batch-scrapes job URLs and saves each as a .txt file into rag/sample_jds/,
ready for build_corpus.py to embed.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.firecrawl_tool import scrape_job_url
urls = [
       "https://www.indeed.com/jobs?q=software+engineer&vjk=7de42ba918c683a6"
"https://www.indeed.com/jobs?q=software+engineer&vjk=3ff79c2c6946bb62"
"https://www.indeed.com/jobs?q=software+engineer&vjk=4b87fbf338497abe"
"https://www.indeed.com/jobs?q=software+engineer&vjk=09cb43ee3a3e6886"
"https://www.indeed.com/jobs?q=machine+learning+engineer&vjk=d7762219f941ae5a"
"https://www.indeed.com/jobs?q=machine+learning+engineer&vjk=103d8d883a0e2780"
"https://www.indeed.com/jobs?q=machine+learning+engineer&vjk=1438200d47d35836"
"https://www.indeed.com/jobs?q=backend+developer&vjk=c8e2a1de6ab08833"
"https://www.indeed.com/jobs?q=backend+developer&vjk=c8e2a1de6ab08833"
"https://www.indeed.com/jobs?q=full+stack+developer&vjk=16a89d83a06c5742"
"https://www.indeed.com/jobs?q=cybersecurity+analyst&vjk=d0d97d6e92c0bb0b"
"https://www.indeed.com/jobs?q=cybersecurity+analyst&vjk=021c844289500398"
"https://www.indeed.com/jobs?q=mobile+developer&vjk=6d04e4df5694cfc2"
"https://www.indeed.com/jobs?q=business+analyst&vjk=6ee38f3a39c720f6",
]

OUT_DIR = os.path.join(os.path.dirname(__file__), "sample_jds")
existing_count = len([f for f in os.listdir(OUT_DIR) if f.endswith(".txt")])

for i, url in enumerate(urls):
    try:
        text = scrape_job_url(url)
        path = os.path.join(OUT_DIR, f"jd_scraped_{existing_count + i}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"✅ Saved {path}")
    except Exception as e:
        print(f"❌ Failed on {url}: {e} — add this one manually instead")