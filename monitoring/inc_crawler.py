from monitoring.base_crawler import BaseCrawler

class IncCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("Inc_Crawler")
        self.urls = ["https://www.inc.com/rss"]

    def run(self):
        for url in self.urls:
            self.process_feed(url)
