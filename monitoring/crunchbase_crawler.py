from monitoring.base_crawler import BaseCrawler

class CrunchbaseCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("Crunchbase_Crawler")
        self.urls = ["https://news.crunchbase.com/feed/"]

    def run(self):
        for url in self.urls:
            self.process_feed(url)