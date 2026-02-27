from monitoring.base_crawler import BaseCrawler

class SearchCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("Global_Search")
        self.queries = [
            "latest startup funding rounds global",
            "entrepreneurship success stories 2026",
            "new venture capital funds launched",
            "emerging tech startup pivots"
        ]

    def run(self):
        for query in self.queries:
            # RSS bridge for Google News searches
            rss_url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"
            self.process_feed(rss_url)