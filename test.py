import unittest
import summarizer as sum


class MyTestCase(unittest.TestCase):
    def test_something(self):
        pages_url = ["blesk.cz", "ct24.ceskatelevize.cz", "denik.cz", "drbna.cz", "echo24.cz",
                     "expres.cz", "extra.cz", "idnes.cz", "irozhlas.cz", "kurzy.cz",
                     "lidovky.cz", "metro.cz", "novinky.cz", "seznamzpravy.cz", "sport.cz",
                     "tn.cz", "tyden.cz", "root.cz", "bbc.com", "pcmag.com",
                     "cnn.com", "time.com", "news.sky.com", "nytimes.com", "theguardian.com",
                     "reuters.com", "apnews.com", "france24.com", "wsj.com", "usnews.com"]

        summarizer = sum.NewsSummarizer()
        for page in pages_url:
            print('Page: ' + page)
            articles = summarizer.save_articles_to_csv(page)
            print('SIZE: ' + str(len(articles)))

        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
