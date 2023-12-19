import csv
import pickle
import os
import time
import datetime
import requests
import bs4
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.corpus.reader.wordlist import NonbreakingPrefixesCorpusReader
import nltk
import shutil
import re
import heapq


class Page:
    def __init__(self, url):
        self.url = url


class Article:
    def __init__(self, title, url, description, text, summary, keywords, site_name, authors, language):
        self.title = title
        self.url = url
        self.description = description
        self.text = text
        self.summary = summary
        self.keywords = keywords
        self.site_name = site_name
        self.authors = authors
        self.language = language

    def __iter__(self):
        return iter([self.title, self.url, self.description, self.text, self.keywords, self.site_name, self.authors,
                     self.language])


class NewsSummarizer:
    pages_filename = "pages_data.plk"

    def __init__(self):
        self.pages = []
        try:
            filename = os.getenv('APPDATA') + "\\nltk_data\\corpora\\stopwords\\czech"
            if not os.path.isfile(filename):
                shutil.copy2('stopwords-cs.txt', filename)
        except:
            print("Failed to copy czech stopwords into nltk_data folder")

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

    def save_articles_to_csv(self, page_name):
        articles = self.parse_articles_from_url(page_name, -1)
        filename = page_name + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".csv"
        if not os.path.isfile(filename):
            file = open(filename, 'x')
            file.close()

        with open(filename, "w", encoding="utf-8") as stream:
            writer = csv.writer(stream, delimiter=";")
            writer.writerow(["title", "url", "description", "content", "keywords", "site_name", "authors", "language"])
            writer.writerows(articles)

        return articles

    #
    # PAGE SCRAPPING
    #
    def parse_articles_from_url(self, main_page_url, max_articles_size=15):
        start = time.time()
        final_main_page_url = "https://" + main_page_url if not main_page_url.startswith("https://") else main_page_url

        soup = self.download_and_parse_page(final_main_page_url)

        # Vyhledani a filtrace odkazu na aktualni clanky
        page_a_elements = soup.find_all("a", href=True)
        articles_links = set()
        for page_a_element in page_a_elements:
            if self.is_link_to_same_domain(main_page_url, page_a_element) and self.is_link_to_article(page_a_element):
                articles_links.add(page_a_element['href'])
                if 0 < max_articles_size <= len(articles_links):
                    break

        # parsovani potrebnych informaci o clanku z html
        page_articles = []
        for article_link in articles_links:
            page_articles.append(self.parse_article(article_link, final_main_page_url))

        end = time.time()
        print('Execution Time: {}'.format(end - start))
        return page_articles

    def parse_article(self, url, main_page_url):
        if not url.startswith("http"):
            url = main_page_url + url
        soup = self.download_and_parse_page(url)
        page_meta_elements = soup.find_all("meta")
        page_html_element = soup.find("html", lang=True)

        title = None
        description = None
        keywords = []
        site_name = None
        authors = []
        language = None
        if page_html_element is not None:
            language = page_html_element['lang']
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
            site_from_url = url[url.startswith("https://www.") and len("https://www."):]
            site_name = site_from_url[:site_from_url.find("/")]

        # Zpracovani obsahu clanku
        article_segments = []
        page_p_elements = soup.find_all("p")
        for page_p_element in page_p_elements:
            if (page_p_element.text is not None and len(page_p_element.text.split()) > 25
                    and "|" not in page_p_element.text):
                article_segments.append(self.remove_new_lines(page_p_element.text))

        text_summary = self.summary_article_text(article_segments, language)

        return Article(title=title, url=url, description=description, text=article_segments, summary=text_summary,
                       keywords=keywords, site_name=site_name, authors=authors, language=language)

    def download_and_parse_page(self, url):
        response = requests.get(url)
        html = response.text
        response.encoding = 'utf-8'

        return bs4.BeautifulSoup(html, features="html.parser")

    #
    # TEXT SUMMARIZATION
    #
    def summary_article_text(self, article_segments, language_code):
        if len(article_segments) < 1:
            return None

        language = None
        if language_code != None:
            for lang, code in NonbreakingPrefixesCorpusReader.available_langs.items():
                if code in language_code:
                    language = lang
                    break
        if language == None:
            language = 'english'

        article_text = " ".join(str(x) for x in article_segments)
        article_filtered_text = ''.join(c for c in article_text if c.isalpha() or c.isspace())
        article_filtered_text = re.sub(r'\s+', ' ', article_filtered_text)

        sentences = sent_tokenize(article_text, language=language)
        language_stopwords = stopwords.words(language)

        word_frequencies = {}
        for word in nltk.word_tokenize(article_filtered_text, language=language):
            word = word.lower()
            if word not in language_stopwords:
                if word not in word_frequencies.keys():
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1

        max_count = max(word_frequencies.values())
        for word in word_frequencies.keys():
            word_frequencies[word] = (word_frequencies[word] / max_count)

        sentences_score = {}
        for sentence in sentences:
            for word in nltk.word_tokenize(sentence.lower(), language='czech'):
                if word in word_frequencies.keys():
                    if len(sentence.split(' ')) < 30:
                        if sentence not in sentences_score.keys():
                            sentences_score[sentence] = word_frequencies[word]
                        else:
                            sentences_score[sentence] += word_frequencies[word]

        final_summary_sentences = heapq.nlargest(7, sentences_score, key=sentences_score.get)
        final_summary = ' '.join(final_summary_sentences)

        return final_summary

    @staticmethod
    def remove_new_lines(text):
        return text.replace("\n", "").replace("\r", "").replace("\t", "").replace(u'\xa0', ' ').strip()

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
