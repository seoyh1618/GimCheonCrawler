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
        to_csv(datalist,value,query_list[value][index])
    to_csv_result(datalist,value)
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

    url_list = []

    for x in tqdm(range(2)):# 마지막 페이지 제외 1회당 20개
        for i in range(25): # 페이지 스크롤 다운 기능
            driver.find_element_by_class_name('a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd').send_keys(Keys.PAGE_DOWN)

        upso_list = driver.find_elements_by_class_name('a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd') # 숙박업소 리스트

        for j in range(len(upso_list)): # url 스크랩

            detail_url = upso_list[j].get_attribute('href')
            url_list.append(detail_url)

        driver.find_element_by_css_selector('#ppdPk-Ej1Yeb-LgbsSe-tJiF1e').click() # 다음 페이지 클릭
        x+=1
        time.sleep(2.5)
    return url_list
    ### 검색 내역이 끝나면 종료됨
def googlemapCrawler(driver,datalist,url_list,query,value) :
    reviewCounter = 0
    reviewId = list()
    searchKeyword = list()
    reviewSubject = list()# value '숙박','음식','관광'
    reviewTarget =list() # name
    reviewUrl =list()    # review URL
    author =list()
    reviewDate = list()
    rating =list()
    reviewText= list()
    for outer_index in tqdm(range(2,len(url_list))):
        # url로 이동
        driver.get(url_list[outer_index])
        time.sleep(1)

        reviewTarget_var = driver.find_element_by_class_name('x3AX1-LfntMc-header-title-title.gm2-headline-5').text
        try :
            #리뷰 더보기 클릭
            driver.find_element_by_css_selector('#pane > div > div.Yr7JMd-pane-content.cYB2Ge-oHo7ed > div > div > div.x3AX1-LfntMc-header-title > div.x3AX1-LfntMc-header-title-ma6Yeb-haAclf > div.x3AX1-LfntMc-header-title-ij8cu > div.x3AX1-LfntMc-header-title-ij8cu-haAclf > div > div.gm2-body-2.h0ySl-wcwwM-RWgCYc > span:nth-child(3) > span > span > span.OAO0-ZEhYpd-vJ7A6b.OAO0-ZEhYpd-vJ7A6b-qnnXGd > span:nth-child(1) > button').click()
        except :
            continue
        time.sleep(3)

        try :
            #리뷰 스크롤 진행
            for index_for in range(100) :
                driver.find_element_by_class_name('siAUzd-neVct.section-scrollbox.cYB2Ge-oHo7ed.cYB2Ge-ti6hGc').send_keys(Keys.PAGE_DOWN)

            #get_element
            author_v = driver.find_elements_by_css_selector('div.ODSEW-ShBeI-title')
            reviewDate_v = driver.find_elements_by_css_selector('span.ODSEW-ShBeI-RgZmSc-date-J42Xof-Hjleke > span:nth-child(1)')
            reviewText_v = driver.find_elements_by_css_selector('div.ODSEW-ShBeI-RWgCYc > div > span.ODSEW-ShBeI-text')
            rating_v = driver.find_elements_by_css_selector('span.ODSEW-ShBeI-RGxYjb-wcwwM')

            # text로 변환
            for inner_index in range(len(author_v)) :
                reviewCounter = reviewCounter + 1

                reviewId.append(reviewCounter)
                reviewSubject.append(value)
                searchKeyword.append(query)
                reviewTarget.append(reviewTarget_var)

                try :
                    author.append(author_v[inner_index].text)
                except :
                    author.append(None)
                try :
                    reviewDate.append(reviewDate_v[inner_index].text)
                except :
                    reviewDate.append(None)
                try :
                    if reviewText_v[inner_index].text.replace('\n',' ') == '' :
                        reviewText.append(None)
                    else :
                        reviewText.append(reviewText_v[inner_index].text.replace('\n',' '))
                except :
                    reviewText.append(None)
                try :
                    rating.append(round(float(rating_v[inner_index].text.split('/')[0].strip())))
                except :
                    rating.append(None)

                reviewUrl.append(url_list[outer_index])


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
        except:
            print('Inner Block Exception')
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
    fileName = 'googlemap'+'_'+value+'_'+query+'_'
    filePath = os.path.abspath('.') + '\data\\'+fileName
    print(googlemap_df.head(3))
    print(googlemap_df.tail(3))
    print(len(googlemap_df))

    today = datetime.datetime.now()
    currentDate = today.strftime("%Y%m%d")

    filePath = os.path.abspath('.') + '\data\\'+fileName+currentDate+'df.csv'
    googlemap_df.to_csv(filePath)
def to_csv_result(datalist,value) :
    googlemap_df = pd.DataFrame(datalist)
    fileName = 'googlemap'+'_'+value+'_'+'result_df_'
    filePath = os.path.abspath('.') + '\data\\'+fileName
    print(googlemap_df.head(3))
    print(googlemap_df.tail(3))
    print('중복제거 전 데이터 개수'+len(googlemap_df))
    result = googlemap_df.drop_duplicates('reviewText')
    print('중복제거 데이터 개수 :'+len(result))

    today = datetime.datetime.now()
    currentDate = today.strftime("%Y%m%d")

    filePath = os.path.abspath('.') + '\data\\'+fileName+currentDate+'.csv'
    result.to_csv(filePath)