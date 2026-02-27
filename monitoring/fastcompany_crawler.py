from monitoring.base_crawler import BaseCrawler

class FastCompanyCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("FastCompany_Crawler")
        self.urls = ["https://www.fastcompany.com/rss"]

    def run(self):
        for url in self.urls:
            self.process_feed(url)