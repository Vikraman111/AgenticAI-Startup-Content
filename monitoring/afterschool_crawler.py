from monitoring.base_crawler import BaseCrawler

class AfterschoolCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("Afterschool_Crawler")
        self.urls = ["https://afterschool.substack.com/feed"]

    def run(self):
        for url in self.urls:
            self.process_feed(url)