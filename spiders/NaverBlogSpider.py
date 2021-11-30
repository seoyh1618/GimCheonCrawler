from config import Config
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from tqdm import tqdm
import time
import os.path
import pandas as pd
import datetime

driver_path = 'C:/dev_python/Webdriver/chromedriver'
startDate ='2021-11-01' ### 시작날짜
endDate = '2021-12-01'  ### 마지막날짜
url = f'https://section.blog.naver.com/Search/Post.naver?pageNo=1&rangeType=PERIOD&orderBy=sim&startDate={startDate}&endDate={endDate}&keyword='
query_list = {
    '숙박' : ['김천숙소','김천모텔','김천호텔','김천여관','김천게스트하우스','김천숙박','김천펜션'],
    '음식' : ['전국'],
    #,'여행','관광','서울여행','김천여행','경기도여행','인천여행'
    '관광' : ['국내여행','국내관광']
}
def init() :
    driver = Config.get_driver(driver_path)
    driver.get(url)
    return driver

def scrapNaverBlog(value) :
    datalist = get_datalist(value)
    driver = init()
    for index in range(len(query_list[value])):
        urls = get_url(driver,query_list[value][index])
        datalist = NaverBlogCrawler(driver,datalist,urls,query_list[value][index])
        to_csv(datalist,value,query_list[value][index])
    to_csv_result(datalist,value)
def get_url(driver,value) :
    url = f'https://section.blog.naver.com/Search/Post.naver?pageNo=1&rangeType=PERIOD&orderBy=sim&startDate={startDate}&endDate={endDate}&keyword={value}'
    driver.get(url)
    time.sleep(0.5)
    search_number = int(driver.find_element_by_class_name('search_number').text.replace(',','').replace('건','')) # 총 게시물 수
    hrefs = driver.find_elements_by_class_name('desc_inner')
    url_list = []
    page_index = 1
    #range(1, int(search_number/7))
    for num in tqdm(range(1, int(search_number/7))):  # 총 게시물 수/7(한 페이지당 게시물 수)
        driver.implicitly_wait(1)
        hrefs = driver.find_elements_by_class_name('desc_inner')
        time.sleep(0.5)
        for index in range(len(hrefs)):
            # url 수집 후 리스트에 저장
            href = hrefs[index].get_attribute('href')
            url_list.append(href)
            print('')
            print('Url counter :',len(url_list))
            print(href)
        # 다음 페이지로 이동
        page_index += 1
        driver.get(f'https://section.blog.naver.com/Search/Post.naver?pageNo={page_index}&rangeType=PERIOD&orderBy=sim&startDate={startDate}&endDate={endDate}&keyword={value}')
    print('수집된 게시물 수 : ',len(url_list)) # 수집된 게시물 수
    return url_list

def NaverBlogCrawler(driver,datalist,urls,value):
    postingId = []
    searchKeyword = []
    title = []
    author = []
    postingDate = []
    postingUrl = urls
    hashtags = []
    postingText = []
    for index in tqdm(range(len(postingUrl))):
        driver.get(postingUrl[index])
        element = driver.find_element_by_id("mainFrame") #iframe 태그 엘리먼트 찾기
        driver.switch_to.frame(element) #프레임 이동
        driver.implicitly_wait(1)
        try :
            title_t = driver.find_element_by_class_name('pcol1').text # 제목
            title.append(title_t)
        except :
            title.append(None)
        try :
            writer = driver.find_element_by_class_name('nick').text # 글쓴이
            author.append(writer)
        except :
            author.append(None)

        postingId.append(index+1)
        searchKeyword.append(value)
        #time.sleep(0.5)
        try:
            date = driver.find_element_by_class_name('se_publishDate.pcol2').text # 작성일
            postingDate.append(date)
        except:
            postingDate.append("NULL")
        try:
            text = driver.find_element_by_class_name('se-main-container').text.replace('\n',' ') # 본문
            postingText.append(text)
        except:
            postingText.append("NULL")

        try:
            tags = driver.find_elements_by_class_name('item.pcol2.itemTagfont._setTop')
            tags_dummy = []
            for j in range(len(tags)):
                tag = driver.find_elements_by_class_name('item.pcol2.itemTagfont._setTop')[j].text.replace('#','')  # 해쉬태그
                tags_dummy.append(tag)
            hashtags.append(tags_dummy)
        except:
            hashtags.append("NULL")
        print(" ")
        print(f"-----{index}-----")
        print("ID: ", postingId[index])
        print("검색 키워드: ", searchKeyword[index])
        print("제목 : ", title[index])
        print("작성자: ", author[index])
        print("날짜: ", postingDate[index])
        #print("이미지URL: ", imgUrl[index])
        #print("위치: ", postingLocation[index])
        print("포스팅URL: ", postingUrl[index])
        print("해쉬태그: ", hashtags[index])
        #print("좋아요: ", likes[index])
        print("본문: ", postingText[index])
        print("   ")

    datalist['postingId'] =  datalist['postingId'] + postingId
    datalist['searchKeyword'] =  datalist['searchKeyword'] + searchKeyword
    datalist['author'] =  datalist['author'] + author
    datalist['postingDate'] =  datalist['postingDate'] + postingDate
    #datalist['imgUrl'] =  datalist['imgUrl'] + imgUrl
    #datalist['postingLocation'] =  datalist['postingLocation'] + postingLocation
    datalist['postingUrl'] =  datalist['postingUrl'] + postingUrl
    datalist['hashtags'] =  datalist['hashtags'] + hashtags
    #datalist['likes'] =  datalist['likes'] + likes
    datalist['postingText'] =  datalist['postingText'] + postingText
    datalist['title'] =  datalist['title'] + title
    return datalist

def get_datalist(value) :
    data_list = {
        'dataSource' : 'NaverBlog',
        'postingId' : list(),
        'searchKeyword' : list(),
        'title' : list(),
        'author' : list(),
        'postingDate' : list(),
        'imgUrl' :None,
        'postingLocation' : None,
        'postingUrl' :list(),
        'hashtags' : list(),
        'likes' : None,
        'postingText' : list()
    }
    return data_list

def to_csv(datalist,value,query):
    print(len(datalist['postingId']))
    print(len(datalist['searchKeyword']))
    print(len(datalist['title']))
    print(len(datalist['author']))
    print(len(datalist['postingDate']))
    print(len(datalist['postingText']))

    naverblog_df = pd.DataFrame(datalist)
    fileName = 'naverblog_'+value+'_'+query+'_'+str(len(datalist['postingId']))

    print(naverblog_df)
    print(len(naverblog_df))

    result = naverblog_df.drop_duplicates('title')
    print(len(result))
    print(result)

    today = datetime.datetime.now()
    currentDate = today.strftime("%Y%m%d")

    filePath = os.path.abspath('.') + '\data\\'+fileName+currentDate
    result.to_csv(filePath)
def to_csv_result(datalist,value) :
    naverblog_df = pd.DataFrame(datalist)
    fileName = 'result_'+'naverblog'+'_'+value+'_'+str(len(datalist['postingId']))
    filePath = os.path.abspath('.') + '\data\\'+fileName
    print(naverblog_df.head(3))
    print(naverblog_df.tail(3))
    print('중복제거 전 데이터 개수',len(naverblog_df))
    result = naverblog_df.drop_duplicates('title')
    print('중복제거 데이터 개수 :',len(result))

    today = datetime.datetime.now()
    currentDate = today.strftime("%Y%m%d")

    filePath = os.path.abspath('.') + '\data\\'+fileName+currentDate+'.csv'
    result.to_csv(filePath)