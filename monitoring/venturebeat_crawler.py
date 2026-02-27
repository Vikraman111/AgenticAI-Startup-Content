from monitoring.base_crawler import BaseCrawler

class VentureBeatCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("VentureBeat_Crawler")
        self.urls = ["https://venturebeat.com/feed/"]

    def run(self):
        for url in self.urls:
            self.process_feed(url)