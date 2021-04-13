import json, re, sys, time, requests, unidecode
from urllib.parse import unquote

import chromedriver_binary
import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from newspaper import Article
from newsplease import NewsPlease
from requests import get
from selenium import webdriver
from selenium.webdriver.chrome.options import Options