# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
import sys
import requests
import datetime
from ebaysdk.exception import ConnectionError
from ebaysdk.finding import Connection
from ebaysdk.shopping import Connection as Shopping
from amazon.api import AmazonAPI
import urllib
import json
import time
from wapy.api import Wapy
import importlib
#import wordpress_api
from lxml import html

# Create your views here.

items_list = []

def SortItemList(items_list):
    # for x in items_list:
    #     print(float(x['price'][1:]))
    items_list.sort(key=lambda x: float(x['price'][1:]))
    # print()
    # print()
    # for x in items_list:
    #     print(float(x['price'][1:]))
    # sorted(items_list[0:40], )

def BestBuyAPI(search_content, items_list):
     baseURL = 'https://api.bestbuy.com/v1/products'
     keyword = '((search=' + search_content + '))'
     apiKey = '?apiKey=8JOVjHGJNdm9BbEIbxX8bNfB'
     sortOptions = '&sort=salePrice.asc'
     showOptions = '&show=name,salePrice,url,image'
     responseFormat = '&format=json'
     url = baseURL + keyword + apiKey + sortOptions + showOptions + responseFormat
     response = requests.get(url)
     # print(type(response))
     response_dict = json.loads(response.text)
     # print(type(response_dict))
     for item in response_dict['products']:
      temp = {
       'source': 'BestBuy',
       'name': item['name'],
       'price': '$' + str(item['salePrice']),
       'url': item['url'],
       'picture': item['image'],  # return a string, which is the url of the image.
      }
      items_list.append(temp)


def WalmartAPI(search_content, items_list):
    wapy = Wapy('47ctafawz2svc2qst3s4h7p4')
    products = wapy.search(search_content)
    for x in range(10):
        #print (products[x].weight)  # 1.0
        #print (products[x].customer_rating)  # 4.445
        title = products[x].name
        price = '$'+str(products[x].sale_price)
        url = products[x].product_url
        picture = products[x].medium_image   #.large_imgage
        temp = {'source': 'Walmart', 'picture': picture, 'name': title, 'price': price, 'url': url}
        items_list.append(temp)



def EtsyAPI(search_content, items_list):
    api_key='kt66836y84hujokqgro9k91e'
    #######https://openapi.etsy.com/v2/listings/active.js?keywords=iphone&limit=12&includes=Images:1&api_key=kt66836y84hujokqgro9k91e
    url = "https://openapi.etsy.com/v2/listings/active.js?keywords=" +search_content + "&limit=12&includes=Images:1&api_key=" + api_key

    ###crawl to get info
    #reload(sys)
    #sys.setdefaultencoding('utf8')
    importlib.reload(sys)

    r = requests.get(url)
    #page_source = r.content.encode(encoding='UTF-8',errors='strict')
    page_source = r.text
    print(page_source)
    #d = json.loads(page_source[4:])
    #print(d['price'])
    #print(d)

    #'''

    end_price = 0
    end_title = 0
    end_url =0
    end_picture=0

    for x in range(10):

        #start_picture=page_source.find("\"url_75x75\":\"", end_picture)
        start_picture = page_source.find("\"url_fullxfull\":\"", end_picture)
        end_picture = page_source.find("\"", start_picture + 18)
        temp_picture = page_source[start_picture + 17:end_picture].replace("\/", "/")

        "Images"
        start_title = page_source.find("\"title\":\"", end_title)
        end_title = page_source.find("\"", start_title + 10)
        temp_title = page_source[start_title + 9:end_title].replace("\/","/")

        start_url = page_source.find("\"url\":\"", end_url)
        end_url = page_source.find("\"", start_url + 7)
        temp_url = page_source[start_url + 7:end_url].replace("\/","/")

        start_price = page_source.find("\"price\":\"", end_price)
        end_price = page_source.find("\"", start_price+10)
        temp_price = page_source[start_price + 9:end_price]


        print(temp_picture)
        # items_list.append(temp_str)
        temp = {'source': 'Etsy','picture':temp_picture, 'name': temp_title, 'price': '$'+temp_price, 'url': temp_url}
        items_list.append(temp)

    #'''

    page_source

def EbayAPI(search_content, items_list):
    try:
        api = Connection(appid='MaozhiTa-MoDeal-PRD-0c22b8256-f6e60466', config_file=None)
        response = api.execute('findItemsAdvanced', {'keywords': search_content})

        assert (response.reply.ack == 'Success')
        assert (type(response.reply.timestamp) == datetime.datetime)
        assert (type(response.reply.searchResult.item) == list)

        append_num=0
        i=0
        while i<len(response.reply.searchResult.item) and append_num<10:
            if response.reply.searchResult.item[i].galleryURL !='http://thumbs1.ebaystatic.com/pict/04040_0.jpg':# and response.reply.searchResult.item[i].condition.conditionDisplayName == 'New':
                title=response.reply.searchResult.item[i].title
                price = '$'+response.reply.searchResult.item[i].sellingStatus.currentPrice.value
                # price=response.reply.searchResult.item[i].sellingStatus.currentPrice.value
                # price+=' '+response.reply.searchResult.item[i].sellingStatus.currentPrice._currencyId
                url=response.reply.searchResult.item[i].viewItemURL
                picture=response.reply.searchResult.item[i].galleryURL
                temp = {'source':'Ebay','picture':picture,'name': title, 'price': price, 'url':url}
                items_list.append(temp)
                append_num+=1
            i+=1
            #print(response.reply.searchResult.item[i].condition)
            #print(response.reply.searchResult.item[i].galleryURL)

        item = response.reply.searchResult.item[0]
        assert (type(item.listingInfo.endTime) == datetime.datetime)
        assert (type(response.dict()) == dict)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())


def AmazonCrawl(search_content, items_list):
    #reload(sys)
    importlib.reload(sys)
    #sys.setdefaultencoding('utf8')
    url = "https://www.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=" + search_content
    #url = "https://www.amazon.com/s/keywords=" + search_content

    headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    r = requests.get(url,headers=headers)

    '''
    XPATH_LIST = '//li[contatins(@id,"result_")]'
    XPATH_URL = './/a[contatins(@class,"s-access-detail-page")]/@href'
    XPATH_TITLE = '//a[contatins(@class,"s-access-detail-page")]/h2/text()'
    XPATH_PRICE = './/span[@class="s-item__price"]/text()'
    XPATH_PICTURE = './/img[@class="s-item__image-img"]/@data-src'

    doc=html.fromstring(r.text)
    product_list = doc.xpath(XPATH_LIST)

    num=0
    for product in product_list:
        if num<10:
            pic=product.xpath(XPATH_PICTURE)
            title=product.xpath(XPATH_TITLE)
            price = product.xpath(XPATH_PRICE)
            url = product.xpath(XPATH_URL)
            temp = {'source': 'Amazon','picture':pic, 'name': title, 'price': price, 'url': url}
            items_list.append(temp)
        num+=1
    '''
    page_source = r.text
    start = 0
    end = 0
    end_name=0
    start_name = page_source.find("title=\"", end_name)
    end_name = page_source.find("\"", start_name + 7)
    temp_str = ""
    for x in range(10):
        start = page_source.find("<span class=\"a-offscreen\">", end)
        end = page_source.find("</span>", start)
        temp_str = page_source[start + 26:end]

        start_name = page_source.find("title=\"", end_name)
        end_name = page_source.find("\"", start_name + 7)
        temp_name_str = page_source[start_name + 6:end_name]

        # items_list.append(temp_str)
        temp = {'source': 'Amazon', 'name': temp_name_str, 'price': temp_str, 'url': ''}
        #temp = {'name': temp_name_str, 'price': temp_str}
        items_list.append(temp)

        # print(start,end,temp_str)
        # print(start_name, end_name, temp_name_str)

def BestBuyCrawl(search_content, items_list):
    #reload(sys)
    importlib.reload(sys)
    #sys.setdefaultencoding('utf8')

    url = "https://www.bestbuy.com/site/searchpage.jsp?st="+search_content+"&_dyncharset=UTF-8&id=pcat17071&type=page&sc=Global&cp=1&nrp=&sp=&qp=&list=n&af=true&iht=y&usc=All+Categories&ks=960&keys=keys"
    r = requests.get(url)
    page_source = r.text
    start = 0
    end = 0
    end_name = 0
    start_name = page_source.find("title=\"", end_name)
    end_name = page_source.find("\"", start_name + 7)
    temp_str = ""
    for x in range(10):
        start = page_source.find("<span class=\"a-offscreen\">", end)
        end = page_source.find("</span>", start)
        temp_str = page_source[start + 26:end]

        start_name = page_source.find("title=\"", end_name)
        end_name = page_source.find("\"", start_name + 7)
        temp_name_str = page_source[start_name + 6:end_name]

        # items_list.append(temp_str)
        temp = {'name': temp_name_str, 'price': temp_str}
        items_list.append(temp)

        # print(start,end,temp_str)
        # print(start_name, end_name, temp_name_str)

def index(request):
    global items_list
    if request.method == 'POST':
        items_list= []
        print(request.POST)
        search_content = request.POST.get('search_content')

        t0=time.clock()
        EbayAPI(search_content,items_list)
        # t1 = time.clock()
        # t2 = time.clock()
        WalmartAPI(search_content, items_list)
        SortItemList(items_list)
        #AmazonCrawl(search_content, items_list)
        EtsyAPI(search_content, items_list)
        #SortItemList(items_list)
        BestBuyAPI(search_content, items_list)

        # print("ebay:", t1-t0)
        # print("etsy:", t2 - t1)

    return render(request, 'index.html', {'data': items_list,'search_content':search_content})

    #return HttpResponse('Hello World!')


def home(request):
    #search_content = request.POST.get('search_content')
    if request.method == 'POST':
        return index(request)
    return render(request,'home.html')