from monitoring.base_crawler import BaseCrawler

class TechCrunchCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("TechCrunch_Crawler")
        self.urls = ["https://techcrunch.com/feed/"]

    def run(self):
        for url in self.urls:
            self.process_feed(url)