from monitoring.base_crawler import BaseCrawler

class EntrepreneurCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("Entrepreneur_Crawler")
        self.urls = ["https://www.entrepreneur.com/latest.rss"]

    def run(self):
        for url in self.urls:
            self.process_feed(url)
