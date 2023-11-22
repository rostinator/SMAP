import pickle
import os
import requests
import bs4


class Page:
    def __init__(self, url):
        self.url = url


class Article:
    def __init__(self, title, url, description, text, keywords, site_name, authors):
        self.title = title
        self.url = url
        self.description = description
        self.text = text
        self.keywords = keywords
        self.site_name = site_name
        self.authors = authors


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

    def remove_page(self, page_url):
        remove_page_index = None
        for x in range(0, len(self.pages)):
            if self.pages[x].url == page_url:
                remove_page_index = x
                break

        if remove_page_index:
            self.pages.pop(remove_page_index)
            self.save_pages()

    def parse_articles_from_url(self, main_page_url, max_articles_size=10):
        final_main_page_url = "https://" + main_page_url if not main_page_url.startswith("https://") else main_page_url

        soup = self.download_and_parse_page(final_main_page_url)

        # Vyhledani a filtrace odkazu na aktualni clanky
        page_a_elements = soup.find_all("a", href=True)
        articles_links = []
        for page_a_element in page_a_elements:
            if self.is_link_to_same_domain(main_page_url, page_a_element) and self.is_link_to_article(page_a_element):
                articles_links.append(page_a_element['href'])
                if len(articles_links) >= max_articles_size:
                    break

        # parsovani informaci o clanku
        page_articles = []
        for article_link in articles_links:
            if not article_link.startswith("http"):
                article_link = final_main_page_url + article_link
            soup = self.download_and_parse_page(article_link)
            page_meta_elements = soup.find_all("meta")

            title = None
            description = None
            keywords = []
            site_name = None
            authors = []
            for page_meta_element in page_meta_elements:
                property = page_meta_element['property'] if page_meta_element.has_attr('property') else None
                content = page_meta_element['content'] if page_meta_element.has_attr('content') else None
                name = page_meta_element['name'] if page_meta_element.has_attr('name') else None

                if property == "og:title":
                    title = content
                elif property == "og:description" or property == "description" or name == "description":
                    description = content
                elif name == "keywords":
                    keywords = content.split(', ')
                elif property == "og:site_name":
                    site_name = content
                elif name == "author":
                    authors = content.split(', ')

            page_h1_elements = soup.find_all("h1", limit=10)
            for page_h1_element in page_h1_elements:
                if len(page_h1_element.text.split()) > 4:
                    title = self.remove_new_lines(page_h1_element.text)
                    break

            if site_name is None:
                site_from_url = article_link[article_link.startswith("https://www.") and len("https://www."):]
                site_name = site_from_url[:site_from_url.find("/")]

            # Zpracovani obsahu clanku
            article_segments = []
            page_p_elements = soup.find_all("p")
            for page_p_element in page_p_elements:
                if (page_p_element.text is not None and len(page_p_element.text.split()) > 25
                        and "|" not in page_p_element.text):
                    article_segments.append(self.remove_new_lines(page_p_element.text))

            page_articles.append(Article(title=title, url=article_link, description=description, text=article_segments,
                                         keywords=keywords, site_name=site_name, authors=authors))

        return page_articles

    def download_and_parse_page(self, url):
        response = requests.get(url)
        html = response.text
        response.encoding = self.parse_charset_from_html(html)

        return bs4.BeautifulSoup(html, features="html.parser")

    @staticmethod
    def parse_charset_from_html(html):
        charset_tag = "<meta charset=\""
        charset_tag_index = html.lower().find(charset_tag)
        charset = html[charset_tag_index + len(charset_tag):charset_tag_index + len(charset_tag) + 50]
        return charset[:charset.find("\"")]

    @staticmethod
    def remove_new_lines(text):
        return text.replace("\n", "").replace("\r", "").replace("\t", "").strip()

    @staticmethod
    def is_link_to_article(page_a_element):
        return (len(page_a_element['href']) > 30
                and len(page_a_element.text) > 0
                and len(page_a_element.text.split()) > 4
                and "|" not in page_a_element.text
                and "/" not in page_a_element.text)

    @staticmethod
    def is_link_to_same_domain(main_page_url, page_a_element):
        return main_page_url in page_a_element['href'] or (
                page_a_element['href'].startswith("/") and len(page_a_element['href']) > 30)
