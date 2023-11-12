import pickle
import os
import requests
import bs4


class Page:
    def __init__(self, url):
        self.url = url


class Article:
    def __init__(self, title, url, description, text):
        self.title = title
        self.url = url
        self.description = description
        self.text = text


class NewsSummarizer:
    pages_filename = "pages_data.plk"

    def __init__(self):
        self.pages = []

    def get_pages(self):
        if not self.pages:
            if not os.path.isfile(self.pages_filename):
                open(self.pages_filename, 'x')

            with open(self.pages_filename, "rb") as f:
                while True:
                    try:
                        self.pages.append(pickle.load(f))
                    except EOFError:
                        break

        return self.pages

    def save_pages(self):
        with open(self.pages_filename, 'wb') as f:
            for d in self.pages:
                pickle.dump(d, f)

    def add_page(self, page):
        self.pages.append(page)
        self.save_pages()

    def remove_page(self, pageUrl):
        removePage = None
        for page in self.pages:
            if page.url == pageUrl:
                removePage = page
                break

        if removePage:
            self.pages.remove(removePage)
            self.save_pages()

    def parse_articles_from_url(self, main_page_url):
        if not main_page_url.startswith("https://www."):
            main_page_url = "https://www." + main_page_url

        soup = self.download_and_parse_page(main_page_url)

        page_a_elements = soup.find_all("a", href=True)
        articles_links = []
        for page_a_element in page_a_elements:
            if (page_a_element['href'].startswith(main_page_url) or page_a_element['href'].startswith("/")) and len(
                    page_a_element.text) > 0 and len(page_a_element.text.split()) > 4:
                articles_links.append(page_a_element['href'])

        page_articles = []
        for article_link in articles_links[:10]:
            soup = self.download_and_parse_page(article_link)
            page_meta_elements = soup.find_all("meta", property=True, content=True)

            title = None
            description = None
            for page_meta_element in page_meta_elements:
                property = page_meta_element['property']
                content = page_meta_element['content']
                if property == "og:title":
                    title = content
                elif property == "og:description":
                    description = content

            h1 = soup.find("h1")
            if h1 is not None and len(h1.text) > 0:
                title = h1.text

            article_segments = []
            page_p_elements = soup.find_all("p")
            for page_p_element in page_p_elements:
                if page_p_element.text is not None and len(page_p_element.text.split()) > 10:
                    article_segments.append(page_p_element.text)

            page_articles.append(Article(title=title, url=article_link, description=description, text=article_segments))

        return page_articles

    def download_and_parse_page(self, url):
        response = requests.get(url)
        html = response.text
        response.encoding = self.parse_charset_from_html(html)

        return bs4.BeautifulSoup(html, features="lxml")

    def parse_charset_from_html(self, html):
        charset_tag = "<meta charset=\""
        charset_tag_index = html.lower().find(charset_tag)
        charset = html[charset_tag_index + len(charset_tag):charset_tag_index + len(charset_tag) + 50]
        return charset[:charset.find("\"")]
