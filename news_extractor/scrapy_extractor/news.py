import nltk, datetime, cloudscraper, time, platform, os, requests, pytz, re
from news_extractor.article_contents.exceptions import *
from news_extractor.article_contents.author import Author
from news_extractor.article_contents.publish_date import PublishDate
from news_extractor.article_contents.title.title import Title
from news_extractor.article_contents.content import Content
from news_extractor.article_contents.helpers import ArticleURL, rand_sleep, NewsVariables, Compare, catch, unicode, ContentVariables, PubDateVariables
from .use_case import get_invalid_keys
from newsplease import NewsPlease
from newspaper import Article
from bs4 import BeautifulSoup
from dateutil.parser import parse
from pprint import pprint
from logs.main_log import init_log
log = init_log('global_parser')
class NewsExtract:
    """
    Instantiate a news article object
        @params:
            url     - url of article to be parsed
            js      - True if article is a javascript rendered site else False
            source  - page source of article
    """

    def __init__(self, url: str, source=None, js: bool=False, lang: str="en", timeout: int=60):
        """
        Initialize method
        """
        if not url or not isinstance(url, str):
            raise NewsError("Invalid URL passed")

        # INSTANTIATE NEWS VARIABLES
        self.news_variables = NewsVariables()

        # CLEAN URL
        # CLEAN_URL = ArticleURL(url)
        # print("sleeping...")
        # time.sleep(2)
        # rand_sleep(3, 5)

        self.url                = url#CLEAN_URL.url
        self.html               = source
        self.lang               = lang
        self.timeout            = timeout
        self.scraped            = False
        self.attr_invalid_keys  = get_invalid_keys()
        self.content_variables  = ContentVariables()
        self.parser             = None
        # PAGE SOURCE IS REQUIRED
        if not self.html:
            raise NewsError("No Page Source passed")

        if js and not self.html:
            raise NewsError("Page source required for dynamic pages.")
        
        # CLEAN HTML
        # print("Cleaning of main HTML")
        clean_html = self.__clean_html(self.html, js=js) if self.html else None
        soup = BeautifulSoup(clean_html, "html.parser")

        # NEWSPAPER 3K
        # print("Extracting Data for newspaper3k")
        article = self.__get_newspaper3k_extract(str(clean_html))
        
        # print("Author Extractor")
        author = catch('None', lambda: Author(clean_html))

        # PUBLISH DATE
        # print("Publish Date Extractor")
        publish_date = catch('None', lambda: PublishDate(clean_html))

        # TITLE | Python Global Parser
        # print("Title Extractor | Global Parser")
        title = catch('None', lambda: Title(clean_html))
        title_instance = None if title.text is None else title.text # Successful catch

        # TITLE | Newspaper3k Parser
        # print("Title catcher for NoneType")
        title_catcher = None if article.title is None else article.title # Successful catch
        # print("Content catcher for Nonetype")
        content = Content(clean_html, title_instance) if title.text is not None else Content(clean_html, title_catcher) if article.title else None # Succesful catch

        # CLASS VARIABLES        
        # print("Get title instance")
        self.title = self.__get_title(title_instance, article)

        # print("Get author instance")
        self.authors = self.__get_authors(author.names, article)

        # Validation for publish_date if none
        # print("Publish Date Extractor")
        publish_date_instance = datetime.datetime.now().isoformat() if publish_date is None else publish_date.date
        self.publish_date = self.__get_publish_date(publish_date_instance, article, clean_html)

        # EXTRACT IMAGE
        # print("Image Extractor")
        self.images = self.__get_images(article)

        # VALIDATE: validation of content parser for choosing the right parser
        # print("Content Instance validator")
        content_instance = self.__get_and_validate_content_parser(content, article, clean_html)

        # CLEAN CONTENT 
        # print("Content Instance")
        self.content = self.__get_content(content_instance, article, js=js)# or self.__get_title(title.text, article)

        # print("Videos Extractor")
        self.videos = catch('list', lambda: article.movies if article.movies else [])
        
        # Newspaper3k Language extractor
        # print("Language Extractor")
        self.language = catch('None', lambda: article.meta_lang if article.meta_lang is not None or article.meta_lang != "" else 'en')

        # BOOLEAN SCRAPED
        self.scraped = True

    def __get_newspaper3k_extract(self, page_source):
        # try:
        if page_source is not None:
            clean_html = self.__clean_html_parser(str(page_source))
            article = Article(' ')
            article.set_html(page_source)
            article.parse()
            article.nlp()
            return article
        else:
            print("News paper is none")
            return None
        # except Exception as e:
        #     print(e)
        #     print("Exception in newspapaer 3k")

    def __clean_html_for_pub_date(self, page_source):
        """
        Clean up page source
        """
        soup = BeautifulSoup(page_source, 'html.parser')

        pub_date_variables = PubDateVariables()

        # REMOVE UNRELATED TAGS
        for tag in soup.find_all(map(lambda key:key, pub_date_variables.tags_for_decompose)):
            tag.decompose()
        return soup

    def __get_and_validate_content_parser(self, content, newspaper3k_article, clean_html):
        '''
            FUNCTION: This function with get and validate all 3 python parsers.
            The order of returning the content is from Python GLobal Parser => NewsPaper3k Extractor => NewsPlease Extractor => None
        '''
        try:
            if content.text is None or content.text == "": 
                # Newspaper3k extractor
                if newspaper3k_article.text is not None and newspaper3k_article.text != "":
                    # print("using newspaper3k for parsing")
                    self.parser = "NewsPaper3k Parser"
                    return newspaper3k_article.text

                # NewsPlease extractor
                elif newspaper3k_article.text is None or newspaper3k_article.text == "":
                    ## Clean html for news please 
                    page_source = self.__clean_html_parser(clean_html) if clean_html is not None else None
                    newsplease = NewsPlease.from_html(str(page_source), url=None)
                    if newsplease.maintext is None or newsplease.maintext == "":
                        self.parser = None
                        return None
                    else:
                        self.parser = "NewsPlease Parser"
                        return newsplease.maintext
                else:
                    self.parser = None
                    return None
            
            # Python Global Parser
            elif content.text is not None:
                self.parser = "Python Global Parser"
                return  content.text
            else:
                self.parser = None
                return None
        except Exception as e:
            print("__get_and_validate_content_parser",e)
            log.error("__get_and_validate_content_parser",e)
            return None

    def generate_data(self):
        """
        Generates article dict data
        """
        if not self.scraped: raise NewsError("Article not scraped")
        date_now = datetime.datetime.today().isoformat()

        data = {
                'article_title': self.title,
                'article_section': [],
                'article_authors': self.authors,
                'article_publish_date': self.publish_date,
                'article_images': self.images,
                'article_content': self.content,
                'article_videos': self.videos,
                'article_media_type': 'web',
                'article_ad_value': 0,
                'article_pr_value': 0,
                'article_language': self.language,
                'article_status': 'Done',
                'article_error_status': None,
                "article_source_from": None,
                'keyword': [],
                'article_url': self.url,
                'date_created': date_now,
                'date_updated': date_now,
                'created_by': "Python Global Scraper",
                'updated_by': "Python Global Scraper"
            }
        
        return data
    
    def __clean_html_parser(self, page_source=None):
        """
        Clean up page source
        """
        if page_source is not None:
            soup = BeautifulSoup(page_source, "html.parser")
            # # DECOMPOSE TAGS WITH INVALID KEY OR MATCHING INVALID KEY
            # for tag in soup.find_all(self.__is_invalid_tag):
            #     if self.__is_valid_tag(tag): continue
            #     tag.decompose()

            # REMOVE UNRELATED TAGS
            for key in self.content_variables.tags_for_decompose:
                for tag in soup.find_all(key):
                    tag.decompose()

            # REMOVE UNRELATED CLASS NAMES
            for c_name in soup.find_all('div', {"class": 'sidebar'}):
                c_name.decompose()

            for id_name in soup.find_all('div', {"id": re.compile(r'magone-labels')}):
                id_name.decompose()

            return soup
        return None

    def __clean_html(self, html: str=None, js: bool=False):
        """
        Private method to clean page source
            @params:
                html    -   page source to clean
                js      -   True if dynamic page else False
        """

        if not html:
            return None
        
        soup = BeautifulSoup(html, "html.parser")
        # REMOVE ALL UNRELATED TAGS FROM SOURCE
        tags_for_decompose = self.news_variables.tags_for_decompose

        for tag in tags_for_decompose:
            for _tag in soup(tag):
                _tag.decompose()
        # looping for all classes that have main-sidebar name on it
        for div_class in soup.find_all("div", {"class": self.attr_invalid_keys}):
            div_class.decompose()

        for id_name in soup.find_all("div", {"id": re.compile(r'main-sidebar|sidebar|magone-labels|site-container')}):
            id_name.decompose()
        if js:
            for tag in soup.find_all(self.__is_invalid_tag):
                tag.decompose()

        return str(soup)
    
    def __is_invalid_tag(self, tag):
        """
        Returns the tag that contains specific invalid keyword
            @params:
                tag     -   BS4 tag/element
        """
        INVALID_KEYS = self.news_variables.invalid_keys
        
        # GET COMPARISON DATA
        INVALID_KEY_DATA = Compare(INVALID_KEYS)
        comparison = None

        for _, v in tag.attrs.items():

            for key in INVALID_KEYS:
                # SET TAG ATTRIBUTE VALUE FOR COMPARISON TO KEYS
                if not isinstance(v, list):
                    comparison = INVALID_KEY_DATA.eval(v)
                
                if key in v:
                    return True
                elif isinstance(v, list) and any(key in i for i in v): # IF V IS A LIST ITERATE THRU ITEMS IN V AND CHECK FOR KEY
                    return True
                elif comparison: # IF KEY IS SIMILAR TO V
                    similarity = str(comparison[0]['similarity']).rstrip("%")

                    if int(similarity) >= 70:
                        return True
                elif isinstance(v, list):
                    for _v in v:
                        _comparison = INVALID_KEY_DATA.eval(v)

                        if _comparison:
                            similarity = str(_comparison[0]['similarity']).rstrip("%")
                        
                        if int(similarity) >= 70: return True

    def __get_title(self, _title: str, article: type(Article)):
        """
        Generate news title
        """
        
        title = catch('None', lambda: unicode(_title) if _title else
                        unicode(article.title) if article.title else 
                        None)

        substring = self.news_variables.invalid_title_keys
        
        if not title:
            return None
        
        for string in substring:
            match = catch('None', lambda: title.lower().index(string.lower()))

            if match: return None
        
        return title

    def __get_authors(self, _author: str, article: type(Article)):
        """
        Generate news authors
        """

        if article is not None:
            authors = catch('list', lambda: _author if _author
                            else article.authors if len(article.authors) != 0
                            else ['No - Author'])
        else:
            authors = _author if _author else ['No - Author']

        if not isinstance(authors, list):
            authors = [authors]

        return authors

    def __get_publish_date_backup(self, _date, article: type(Article)):
        """
        Generate news publish date
        """
        pht = pytz.timezone('Asia/Singapore')
        article_date = None
        try:
            article_date = article.meta_data['article']['published_time']

            if not isinstance(article_date, datetime.datetime):
                article_date = parse(str(article_date))

        except Exception as e:
            article_date = None

        # GET BOTH DATES
        dates = [_date, article_date]
        # REPLACE TZINFO
        datetime_dates = [date.replace(tzinfo=pht) for date in dates if date is not None]

        # GET MIN DATE IF DATETIME_DATES IS NOT NONE
        publish_date = datetime.datetime.now().isoformat() if not datetime_dates else min(datetime_dates).isoformat()

        return publish_date

    def __get_publish_date(self, _date, article: type(Article), page_source):
        """
        Generate news publish date
        """
        pht = pytz.timezone('Asia/Singapore')
        try:
            if article.meta_data.get('article', None) is None or article.meta_data['article'] == {} or article.meta_data['article'].get('published_time', None) is None:
                article_date = None
            else:
                article_date = article.meta_data['article']['published_time']
                if not isinstance(article_date, datetime.datetime):
                    article_date = parse(str(article_date))
        except Exception as e: 
            print("__get_publish_date func", e)
            article_date = None

        # GET BOTH DATES
        newspaper3k_pub_date = article_date.replace(tzinfo=pht) if article_date is not None else None
        global_parser_pub_date = _date.replace(tzinfo=pht) if _date is not None else None
        if newspaper3k_pub_date is not None:
            # print("using newspaper3k date extractor")
            publish_date = newspaper3k_pub_date.isoformat()
        elif newspaper3k_pub_date is None:
            newsplease = NewsPlease.from_html(str(page_source), self.url)
            # print("newsplease pub date is", newsplease.date_publish)
            if newsplease.date_publish is not None:
                # print("using newsplease date extractor")
                publish_date = newsplease.date_publish.isoformat()
            elif newsplease.date_publish is None:
                if global_parser_pub_date is not None:
                    # print("using global parser date extractor")
                    publish_date = global_parser_pub_date.isoformat()
                else:
                    # print("using date now")
                    publish_date = datetime.datetime.now().isoformat()
            else:
                # print("Using date now")
                publish_date = datetime.datetime.now().isoformat()
        else:
            # print("Using date now")
            publish_date = datetime.datetime.now().isoformat()
        # print("the date is", publish_date)
        return publish_date

    def extract_date(self):
        date =  re.findall(r'/(\d{4})/(\d{1,2})/(\d{1,2})/', self.url)
        if date == [] or date is None:
            return None
        else:
            return date[0]
    def __get_images(self, article: type(Article)):
        """
        Generate news images
        """
        if not article:
            images = [catch('list', lambda: article.top_image if article.top_image else [])]
        else:
            images = []

        return images

    def __get_content(self, _content: str, article: type(Article), js: bool=False):
        """
        Generate news content
        """
        if js:
            content = catch('None', lambda: unicode(' '.join(_content.replace('’', '').split())) if _content else None)
            return content
        else:
            if _content is not None:
                return unicode(' '.join(_content.replace('’', '').split()))
            else:
                return None
