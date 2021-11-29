from config import Config
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from tqdm import tqdm
import time
import os.path
import pandas as pd
import datetime

driver_path = 'C:/dev_python/Webdriver/chromedriver'
first_url ='https://www.google.com/maps/'

query_list = {
    '숙박' : ['김천숙소','김천모텔','김천호텔','김천여관','김천게스트하우스','김천숙박','김천펜션'],
    '음식' : ['전국'],
    '관광' : ['김천여행','서울여행']
}

def init() :
    driver = Config.get_driver(driver_path)
    driver.get(first_url)
    return driver

def scrapGoogleMaps(value) :
    datalist = get_datalist(value)
    driver = init()
    for index in range(len(query_list[value])):
        urls = get_url(driver,query_list[value][index])
        datalist = googlemapCrawler(driver,datalist,urls,query_list[value][index],value)
        to_csv(datalist,value)

def get_datalist(value) :
    data_list = {
        'dataSource' : 'GoogleMap',
        'reviewId' : list(),
        'searchKeyword' : list(),
        'reviewSubject' : list(),# value '숙박','음식','관광'
        'reviewTarget' : list(), # name
        'reviewUrl' : list(),    # review URL
        'author' :list(),
        'reviewDate' : list(),
        'rating' :list(),
        'reviewText' : list(),
    }
    return data_list
def get_url(driver,value) :
    query_url = f'https://www.google.com/maps/search/{value}'
    driver.get(query_url)
    url_list = []
    j = 0

    for x in range(20):
        for i in range(10): # 페이지 스크롤 다운 기능
            driver.find_element_by_class_name('a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd').send_keys(Keys.PAGE_DOWN)

        upso_list = driver.find_elements_by_class_name('a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd') # 식당 리스트
        try:
            for j in range(len(upso_list)): # url 스크랩
                time.sleep(2)
                detail_url = upso_list[j].get_attribute('href')
                url_list.append(detail_url)
                j += 1
        except:
            continue

        try:
            driver.find_element_by_css_selector('#ppdPk-Ej1Yeb-LgbsSe-tJiF1e > img').click() # 다음 페이지 클릭
        except:
            break
    return url_list
    ### 검색 내역이 끝나면 종료됨
def googlemapCrawler(driver,datalist,urls,query,value) :
    reviewCounter = 0
    reviewId : list()
    searchKeyword : list()
    reviewSubject : list()# value '숙박','음식','관광'
    reviewTarget : list() # name
    reviewUrl : list()    # review URL
    author :list()
    reviewDate : list()
    rating :list()
    reviewText : list()

    i = 0
    x = 0
    j = 1
    for x in range(len(urls)):
        # url로 이동
        driver.get(urls[x])
        time.sleep(1)
        #x += 1


        # 식당 이름
        restaurant = driver.find_element_by_class_name('x3AX1-LfntMc-header-title-title.gm2-headline-5').text

        try:
            # 리뷰 더보기 클릭
            driver.find_element_by_css_selector('#pane > div > div.Yr7JMd-pane-content.cYB2Ge-oHo7ed > div > div > div.x3AX1-LfntMc-header-title > div.x3AX1-LfntMc-header-title-ma6Yeb-haAclf > div.x3AX1-LfntMc-header-title-ij8cu > div.x3AX1-LfntMc-header-title-ij8cu-haAclf > div > div.gm2-body-2.h0ySl-wcwwM-RWgCYc > span:nth-child(3) > span > span > span.OAO0-ZEhYpd-vJ7A6b.OAO0-ZEhYpd-vJ7A6b-qnnXGd > span:nth-child(1) > button').click()
            time.sleep(1)

            try:

                for i in range(500): # 리뷰 500개까지 스크랩
                    review_dict = {}

                    name = driver.find_elements_by_class_name('ODSEW-ShBeI-title')[i].text # 작성자
                    date = driver.find_elements_by_class_name('ODSEW-ShBeI-RgZmSc-date')[i].text # 작성일
                    text = driver.find_elements_by_class_name('ODSEW-ShBeI-text')[i].text # 내용
                    rating_t = int(driver.find_elements_by_class_name('ODSEW-ShBeI-H1e3jb')[i].get_attribute('aria-label').replace(' 별표 ','').replace('개 ',''))
                    reviewCounter = reviewCounter +1

                    reviewId.append(reviewCounter)
                    reviewSubject.append(value)
                    searchKeyword.append(query)
                    reviewTarget.append(restaurant)
                    author.append(name)
                    reviewDate.append(date)
                    reviewText.append(text.replace('\n',' '))
                    rating.append(rating_t)
                    reviewUrl.append(urls[x])

                    i += 1

                    print(" ")
                    print(f"-----{reviewCounter-1}-----")
                    print("리뷰ID: ", reviewId[reviewCounter-1])
                    print("구분: ", reviewSubject[reviewCounter-1])
                    print("검색 키워드: ", searchKeyword[reviewCounter-1])
                    print("매장명: ", reviewTarget[reviewCounter-1])
                    print("작성자: ", author[reviewCounter-1])
                    print("리뷰 URL: ", reviewUrl[reviewCounter-1])
                    print("날짜: ", reviewDate[reviewCounter-1])
                    print("점수: ", rating[reviewCounter-1])
                    print("본문: ", reviewText[reviewCounter-1])
                    print("   ")

                    # 스크롤 다운
                    driver.find_element_by_class_name('siAUzd-neVct.section-scrollbox.cYB2Ge-oHo7ed.cYB2Ge-ti6hGc').send_keys(Keys.PAGE_DOWN)
            except:
                print('ok')
                continue
        except:
            continue

    datalist['reviewId'] =  datalist['reviewId'] + reviewId
    datalist['searchKeyword'] =  datalist['searchKeyword'] + searchKeyword
    datalist['reviewSubject'] =  datalist['reviewSubject'] + reviewSubject
    datalist['reviewTarget'] =  datalist['reviewTarget'] + reviewTarget
    datalist['reviewUrl'] =  datalist['reviewUrl'] + reviewUrl
    datalist['author'] =  datalist['author'] + author
    datalist['reviewDate'] =  datalist['reviewDate'] + reviewDate
    datalist['rating'] =  datalist['rating'] + rating
    datalist['reviewText'] =  datalist['reviewText'] + reviewText
    return datalist

def to_csv(datalist,value,query):
    googlemap_df = pd.DataFrame(datalist)
    fileName = 'googlemap'+'_'+value+'_'+query+'df_'
    filePath = os.path.abspath('.') + '\data\\'+fileName
    print(googlemap_df.head(3))
    print(googlemap_df.tail(3))
    print(len(googlemap_df))

    today = datetime.datetime.now()
    currentDate = today.strftime("%Y%m%d")

    filePath = os.path.abspath('.') + '\data\\'+fileName+currentDate+'.csv'
    googlemap_df.to_csv(filePath)
