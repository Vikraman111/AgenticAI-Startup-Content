from monitoring.base_crawler import BaseCrawler

class YCombinatorCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("YCombinator_Crawler")
        # YC Blog
        self.urls = ["https://www.ycombinator.com/blog/rss"]

    def run(self):
        for url in self.urls:
            self.process_feed(url)