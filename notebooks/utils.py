# Common webscraping libaries
from bs4 import BeautifulSoup as bs
from markdownify import markdownify
from urllib.parse import urlparse
# Data manipulation libraries
import pandas as pd
import numpy as np
import requests
import time
import re

def attribute_finder(tag,kw,v=False):
    """
        Returns True if the param :kw: is in the tag's class or ID, and false otherwise
    """
    
    if 'class' in tag.attrs:
        if kw in tag.attrs['class'] or any([kw in x for x in tag.attrs['class']]):
            return True
    if 'id' in tag.attrs:
        if kw in tag.attrs['id'] or any([kw in x for x in tag.attrs['id']]):
            return True
    return False

def clean_webpage(url,v=False):
    r = requests.get(url,headers = {'User-Agent': 'Mozilla/5.0'})
    soup = bs(r.text,
            features="html.parser")
    # Get rid of all JS, style forms, footers, headers and navs
    for script in soup(["script",'style' ,"footer","header","nav","noscript"]):
        script.decompose()    # rip it out
    # If the tag contains the word 'nav', 'invis', or 'hidden'
    nav = soup.findAll(lambda tag : attribute_finder(tag,'nav'))
    if v: print('nav',len(nav))
    hidden = soup.findAll(lambda tag : attribute_finder(tag,'hide'))
    if v: print('hidden',len(hidden))
    invis = soup.findAll(lambda tag : attribute_finder(tag,'invis'))
    if v: print('invis',len(invis))
    skip = []#soup.findAll(lambda tag : attribute_finder(tag,'skip'))
    if v: print('skip',len(skip))
    sidebar = []
#     sidebar = soup.findAll(lambda tag : attribute_finder(tag,'sidebar'))
#     if v: print('sidebar',len(sidebar))
    footer = soup.findAll(lambda tag : attribute_finder(tag,'footer'))
    if v: print('footer',len(footer))
    header = soup.findAll(lambda tag : attribute_finder(tag,'header'))
    if v: print('header',len(header))
    hero = soup.findAll(lambda tag : attribute_finder(tag,'hero'))
    if v: print('hero',len(hero))
    shortcut = soup.findAll(lambda tag : attribute_finder(tag,'shortcut'))
    if v: print('shortcut',len(shortcut))
    menu = soup.findAll(lambda tag : attribute_finder(tag,'menu'))
    if v: print('menu',len(menu))
    for tag in nav+hidden+invis+skip+sidebar+footer+header+hero+menu:
        tag.decompose()
    return soup
    
def save_images(url,uni,soup,url_type="Diversity Page",out_folder="output",v=False):
    parsed_uri = urlparse(url)
    pretty_url = url.strip().replace("/","_")
    base_url = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    # Get images
    img_tags = soup.find_all('img')
    urls = [img.get('src') for img in img_tags if img.get('src')]
    
    for i,url in enumerate(urls):
        filename = re.search(r'/([\w_-]+[.](jpg|gif|png))$', url)
        if not filename:
            return
        
        fp = f"../data/{out_folder}/images/{uni}-{pretty_url}-{i}.png"
        with open(fp, 'wb') as f:
            if 'http' not in url:
                if url[0] == "/": 
                    url = url[1:]
                # sometimes an image source can be relative 
                # if it is provide the base url which also happens 
                # to be the site variable atm. 
                if v: print(url)
                url = '{}{}'.format(base_url, url) 
            response = requests.get(url)
            f.write(response.content)
    
def scrape_webpage(url,uni,url_type="Diversity Page",out_folder="output",save_images=True,v=False,sleep=0):
    if v: print(uni,url)
    soup = clean_webpage(url)
    if save_images: save_images(url,uni,soup,url_type,out_folder)
    for script in soup(["img"]):
        script.decompose()    # rip it out
    str_soup = str(soup)
    overview = re.sub(r'\n\s*\n', '\n\n', markdownify(str_soup))
    # Add a linebreak
    bl = "\n** **\n\n"
    overview = f"{url_type} – {url} \n\n {overview} {bl}"
    pretty_uni = uni.strip().replace("/","_")
    with open(f"../data/{out_folder}/text_files/{pretty_uni}.md", "a", encoding='utf-8') as file:
        file.write(str(overview))
    if sleep: time.sleep(sleep)
    text = re.sub(r'\n\s*\n','\n\n',soup.get_text())
    text = re.sub(r'\W+', '', text)
    return text