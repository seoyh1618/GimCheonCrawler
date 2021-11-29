from config import Config
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm
import time
import os.path
import yaml
import pandas as pd
import googlemaps
import datetime

my_id = 'yeonhhhhh5'   ### ID
my_pw = '@aa1149118'   ### PASSWORD
driver_path = 'C:/dev_python/Webdriver/chromedriver'
url ='https://www.instagram.com'
# id/pw 입력 -> 로그인 정보 저장 여부 -> 피드

query_list = {
    '숙박' : ['김천숙박','김천숙소','김천모텔','김천호텔','김천여관','김천게스트하우스','김천여관','김천게스트하우스','김천펜션'],
    '음식' : ['전국'],
    '관광' : ['김천여행','서울여행']
}

def init() :
    driver = Config.get_driver(driver_path)
    driver.get(url)
    time.sleep(2.5)

    id_ = driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[1]/div/label/input') # id
    id_.send_keys(my_id)
    pw_ = driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[2]/div/label/input') # pw
    pw_.send_keys(my_pw)
    driver.find_element_by_css_selector('#loginForm > div > div:nth-child(3) > button > div').click() # 로그인

    time.sleep(2.5)
    driver.find_element_by_class_name('cmbtv').click() # 정보 저장 안함

    driver.wait = driver.implicitly_wait(10)

    # 알림 설정 나중에
    driver.find_element_by_css_selector('body > div.RnEpo.Yx5HN > div > div > div > div.mt3GC > button.aOOlW.HoLwm').click()

    return driver

def scrapNaverPlace(value) :
    driver = init()
    datalist = get_datalist()

    for index in range(len(query_list[value])):
        datalist = InstargrameCrawler(driver,datalist,query_list[value][index],5)
    to_csv(datalist,value)

def InstargrameCrawler(driver,datalist,value,scrap_number) :

    # path 설정
    user_id_path = 'e1e1d'
    location_class = 'O4GlU'
    main_text_path = 'C4VMK'
    tags_class_name = ' xil3i'
    likes_path = 'zV_Nj'
    date_path = '_1o9PC.Nzb55'
    next_path = '_65Bje.coreSpriteRightPaginationArrow'

    # data lists
    postingId = []
    postingUrl  = []
    author = []
    postingLocation  = []
    postingText  = []
    postingDate = []
    hashtags = []
    imgUrl = []
    searchKeyword = []
    likes  = []

    #title = []

    try:
        url = 'https://www.instagram.com/explore/tags/{}/'.format(value)
        driver.get(url)
    except :
        time.sleep(3)
        driver.get(url)

    # 첫번째 게시물 클릭
    first_img = '_9AhH0'
    driver.find_element_by_class_name(first_img).click()

    for index in tqdm(range(scrap_number)):

        # sequence
        postingId.append(index)

        # 글 링크
        try:
            time.sleep(1)
            content_link = driver.find_element_by_class_name('zV_Nj').get_attribute('href')
            postingUrl.append(content_link)
        except:
            postingUrl.append("NULL")

        # user ID
        try :
            user_id_obj = driver.find_element_by_class_name(user_id_path)
            user_id = user_id_obj.text

            author.append(user_id)

        except :
            author.append("NULL")


        # 위치정보
        try :
            location_obj = driver.find_element_by_class_name(location_class)
            location_text = location_obj.text
            location_href = location_obj.get_attribute("href")

            postingLocation.append(location_text)
            #location_hrefs.append(location_href)
        except :
            postingLocation.append("NULL")
           # location_hrefs.append("NULL")

        # 이미지 링크
        try:
            time.sleep(2)
            html = driver.page_source
            soup = BeautifulSoup(html)
            instagram = soup.select('.v1Nh3.kIKUG._bz0w')
            img_url = instagram[index].select_one('.KL4Bh').img['src']

            imgUrl.append(img_url)
        except:
            imgUrl.append("NULL")

        # 본문
        try :
            main_text_obj = driver.find_element_by_class_name(main_text_path)
            main_text = main_text_obj.text
            clean_text = main_text.replace("\n"," ")
            #comments = driver.find_element_by_class_name('Mr508 ').text.replace('\n',' ')

            postingText.append(clean_text)
        except :
            postingText.append("NULL")

        # 해쉬태그
        try:
            tag_list = []
            tags = driver.find_elements_by_class_name('xil3i')
            for i in range(len(tags)):
                tag = tags[i].text.replace('#', '')
                tag_list.append(tag)
            hashtags.append(tag_list)
        except:
            hashtags.append("NULL")

        # 좋아요 개수
        try :
            time.sleep(0.5)
            like = int(driver.find_element_by_css_selector('div.Nm9Fw > a > span').text)

            likes.append(like)
        except :
            likes.append("NULL")


        # 날짜
        try :
            date_obj = driver.find_element_by_class_name(date_path)
            # date_text = date_obj.text # 7월 14일
            date_time = date_obj.get_attribute("datetime")
            date_title = date_obj.get_attribute("title") # 2021년 7월 14일

            postingDate.append(date_time)
            #date_titles.append(date_title)
        except :
            #date_texts.append("NULL")
            postingDate.append("NULL")
            #date_titles.append("NULL")

        # searchKeyword
        searchKeyword.append(value)

        print(" ")
        print(f"-----{index}-----")
        print("ID: ", postingId[index])
        print("검색 키워드: ", searchKeyword[index])
        print("작성자: ", author[index])
        print("날짜: ", postingDate[index])
        print("이미지URL: ", imgUrl[index])
        print("위치: ", postingLocation[index])
        print("포스팅URL: ", postingUrl[index])
        print("해쉬태그: ", hashtags[index])
        print("좋아요: ", likes[index])
        print("본문: ", postingText[index])
        print("   ")

        # 다음 페이지 여부 확인
        try:
            next_level = driver.find_element_by_class_name('l8mY4 ')
            next_level.click()
            print('clicked')
            index += 1
        except:
            break
    datalist['postingId'] =  datalist['postingId'] + postingId
    datalist['searchKeyword'] =  datalist['searchKeyword'] + searchKeyword
    datalist['author'] =  datalist['author'] + author
    datalist['postingDate'] =  datalist['postingDate'] + postingDate
    datalist['imgUrl'] =  datalist['imgUrl'] + imgUrl
    datalist['postingLocation'] =  datalist['postingLocation'] + postingLocation
    datalist['postingUrl'] =  datalist['postingUrl'] + postingUrl
    datalist['hashtags'] =  datalist['hashtags'] + hashtags
    datalist['likes'] =  datalist['likes'] + likes
    datalist['postingText'] =  datalist['postingText'] + postingText
    return datalist
def to_csv(datalist,value):
    instargrame_df = pd.DataFrame(datalist)
    fileName = 'insta'+value
    filePath = os.path.abspath('.') + '\data\\'+fileName
    print(instargrame_df.head(3))
    print(instargrame_df.tail(3))
    print(len(instargrame_df))

    result = instargrame_df.drop_duplicates('author')
    print(len(instargrame_df))
    print(len(result))
    print(result)

    today = datetime.datetime.now()
    currentDate = today.strftime("%Y%m%d")

    filePath = os.path.abspath('.') + '\data\\'+currentDate+fileName
    result.to_csv(filePath)



def get_datalist() :
    data_list = {
            'dataSource' : 'NaverPlace',
            'postingId' : list(),
            'searchKeyword' : list(),
            'title' : None,
            'author' : list(),
            'postingDate' : list(),
            'imgUrl' :list(),
            'postingLocation' : list(),
            'postingUrl' :list(),
            'hashtags' : list(),
            'likes' : list(),
            'postingText' : list()
        }
    return data_list
