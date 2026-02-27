from monitoring.base_crawler import BaseCrawler

class TheHustleCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("TheHustle_Crawler")
        self.urls = ["https://thehustle.co/feed/"]

    def run(self):
        for url in self.urls:
            self.process_feed(url)