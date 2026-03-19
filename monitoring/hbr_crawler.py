from monitoring.base_crawler import BaseCrawler

class HBRCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("HBR_Crawler")
        self.urls = ["http://feeds.harvardbusiness.org/harvardbusiness?format=xml"]

    def run(self):
        for url in self.urls:
            self.process_feed(url)
