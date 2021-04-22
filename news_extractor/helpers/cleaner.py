from news_extractor.article_contents.helpers import TitleVariables, PubDateVariables, AuthorVariables, catch, compare
from bs4 import BeautifulSoup
class Cleaner:

    def __init__(self, page_source, url=None):
        self.page_source = page_source
        self.url = url
        self.soup = BeautifulSoup(html, "html.parser")
        self.title_variables = TitleVariables()
        self.pub_date_variables = PubDateVariables()
        self.author_variables = AuthorVariables()
        self.content_variables = ContentVariables()

        # Variables for page source all items
        self.title_page_source          = None
        self.author_page_source         = None
        self.content_page_source        = None
        self.date_publish_page_source   = None

        # Trigger cleaner
        self.__process_cleaner()


    # Function to trigger all cleaners and instansiate its page source to init variable
    def __process_cleaner(self):
        if self.page_source is not None:
            cleaned_page_source             = self.__clean_html()
            self.title_page_source          = self.__clean_title()
            self.author_page_source         = self.__clean_author()
            self.content_page_source        = self.__clean_content()
            self.date_publish_page_source   = self.__clean_publish_date()

    # Function for cleaning Title and returning its cleaned page source
    def __clean_title(self):
        soup = BeautifulSoup(self.page_source, "html.parser")
        for key in self.title_variables.tags_for_decompose:
            for tag in soup.find_all(key):
                tag.decompose()
        return soup

    # Function for cleaning Author and returning its cleaned page source to init variable
    def __clean_author(self):
        soup = BeautifulSoup(self.page_source, "html.parser")

        # DECOMPOSE TAGS WITH INVALID KEY OR MATCHING INVALID KEY
        for tag in soup.find_all(self.__is_invalid_tag):
            tag.decompose()

        # REMOVE UNRELATED TAGS
        for key in self.author_variables.tags_for_decompose:
            for tag in soup.find_all(key):
                tag.decompose()
        
        for c_name in soup.find_all("footer"):
            c_name.decompose()

        return soup

    # Function for cleaning Content and returning its cleaned page source to init variable
    def __clean_content(self):
        soup = BeautifulSoup(self.page_source, "html.parser")

        # DECOMPOSE TAGS WITH INVALID KEY OR MATCHING INVALID KEY
        for tag in soup.find_all(self.__is_invalid_tag):
            if self.__is_valid_tag(tag): continue
            tag.decompose()

        # REMOVE UNRELATED TAGS
        for tag in soup.find_all(map(lambda key: key, self.content_variables.tags_for_decompose)):
            tag.decompose()

        for c_name in soup.find_all("div", {"class": re.compile(r'list-label-widget-content')}):
            c_name.decompose()

        return soup

    # Function for cleaning Publish Date and returning its cleaned page source to init variable
    def __clean_publish_date(self):
        soup = BeautifulSoup(self.page_source, "html.parser")
        for key in self.pub_date_variables.tags_for_decompose:
            for tag in soup.find_all(key):
                tag.decompose()

        return soup

    def __clean_html(self):
        soup = BeautifulSoup(self.page_source, "html.parser")

        # REMOVE ALL UNRELATED TAGS FROM SOURCE
        tags_for_decompose = self.news_variables.tags_for_decompose

        # Refactor this code!!
        for tag in tags_for_decompose:
            for _tag in soup(tag):
                _tag.decompose()
        # looping for all classes that have main-sidebar name on it
        for div_class in soup.find_all("div", {"class": self.attr_invalid_keys}):
            div_class.decompose()

        for id_name in soup.find_all("div", {"id": re.compile(r'main-sidebar|sidebar|magone-labels|site-container')}):
            id_name.decompose()

        # if js:
        #     for tag in soup.find_all(self.__is_invalid_tag):
        #         tag.decompose()

        return str(soup)