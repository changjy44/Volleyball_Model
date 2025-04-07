# Using Scraper

1. For all folders (vnl, poland, italy, france, japan),

- Run any other python file to find the matches to scrape
- Run all `xxx_scrape_match.py`. This will actively scrape matches, and create [year]-[league]-data.json

2. In processor folder, run `process_match_starters.py` to assign roles to each starting position. This will create [year]-[league]-data-processed.json
3. In sql folder, run `format_sql_data.py` to combine all data, and create matches.csv and statistics.csv. This also creates [year]-[league]-data-final.json, where each row conforms to a standardized format
4. In the visualizer folder, run `python -m http.server 8000` to run the data visualizer website. Go to `localhost:8000` to view matches and other statitcis

## Disclaimer

- Everything was done for the purposes for FYP. The scrapers may not work as intended, slight modifications may be needed. Please compare to the finalized dataset should anything to check for differences
