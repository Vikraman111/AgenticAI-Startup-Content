from monitoring.base_crawler import BaseCrawler

class ForbesCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("Forbes_Crawler")
        self.urls = [
            "https://www.forbes.com/business/feed/",
            "https://www.forbes.com/innovation/feed/"
        ]

    def run(self):
        for url in self.urls:
            self.process_feed(url)
