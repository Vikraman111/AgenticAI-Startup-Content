from monitoring.base_crawler import BaseCrawler

class BusinessInsiderCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("BusinessInsider")
        # Using the main Feedburner and section-specific mirrors
        self.urls = [
            "https://feeds.feedburner.com/businessinsider",
            "https://www.businessinsider.com/tech/rss",
            "https://www.businessinsider.com/strategy/rss"
        ]

    def run(self):
        for url in self.urls:
            self.process_feed(url)