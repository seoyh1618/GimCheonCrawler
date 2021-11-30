from config import Config
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from tqdm import tqdm
import time
import os.path
import pandas as pd
import googlemaps
import datetime

url = 'https://www.naver.com'
gmaps_key = 'AIzaSyDFFxNTBDX-ii1yPntiKPmV-uN1TTcwRJE'
driver_path = 'C:/dev_python/Webdriver/chromedriver'
#
query_list = {
    #'김천숙박','김천숙소','김천모텔','김천호텔',
    '숙박' : ['김천여관','김천게스트하우스','김천펜션'], #김천여관 2번째 페이지 에러
    '음식' : ['전국'],
    '관광' : ['전국']
}
def init() :
    driver = Config.get_driver(driver_path)
    driver.get(url)
    return driver

def scrapNaverPlace(value) :
    datalist = get_datalist(value)

    for index in range(len(query_list[value])):
        driver = init()
        enterCrawlTarget(driver,query_list[value][index])

        if value == '숙박':
            datalist = roomCrawler(driver,datalist,query_list[value][index])
        elif value == '음식':
            datalist = foodCrawler(driver,datalist)
        else :
            datalist = tourCrawler(driver,datalist)

    to_csv(datalist,value)

def roomCrawler(driver,datalist,query) :
    #Content_path
    name_p = '#_title > span._3XamX'
    address_p = 'ul > li._1M_Iz._1aj6- > div'
    siteUrl_p = 'div.place_detail_wrapper > div:nth-child(4) > div > div > div > ul > li.iSlFU._2reeS > div > div > a'
    lodgingCategory_p = '#_title > span._3ocDE'
    priceRange_p = 'li._1M_Iz._1nfcX > div > ul > li > div > div._2O0eV'
    description_more_p = 'li._1M_Iz._3__3i > div > a > span.WoYOw'
    description_nomore_p = 'div > ul > li._1M_Iz._3__3i > div > div > span.WoYOw'
    aggregate_rating_p = '#app-root > div > div > div.place_detail_wrapper > div.place_section.no_margin.GCwOh > div > div > div._3XpyR._2z4r0 > div > span._1Y6hi._1A8_M > em'
    facility_p = 'li._1M_Iz > div._1h3B_'
    telephone_p = 'div._1h3B_ >span:nth-child(1)'

    #Page_ctl_path
    scroll = driver.find_element_by_class_name('_1Az1K')
    page_number =  len(driver.find_elements(By.CSS_SELECTOR,'div._2lx2y > div._2ky45 > a'))
    next_page_p = '#app-root > div > div > div._2ky45 > a:nth-child({})'.format(str(page_number))
    if query == '김천펜션' or query =='김천게스트하우스' :
        print('김천펜션')
        detail_info_p = '#_pcmap_list_scroll_container > ul > li > div.kqlfc > a'
    elif query == '김천여관' :
        detail_info_p = '#_pcmap_list_scroll_container > ul > li > div._3ZU00 > a:nth-child(1)'
    else :
        detail_info_p = '#_pcmap_list_scroll_container > ul > li > div._3ZU00._1rBq3 > a:nth-child(1)'

    dataSource = 'NaverPlace'
    name = []
    address = []
    siteUrl = []
    lodgingCategory = []       # 숙박 분류
    description = []
    telephone = []             # 연락 전화
    aggregate_rating = []
    geo = []                   # 위도, 경도
    roomType = []              # 방종류 , 가격 , 방 옵션
    imageUrl = []              # 숙박업체 images url
    administrativeDong = []    # 행정동

    for index in tqdm(range(1,2)) :
        # 스크롤 내리기
        for scl_location in range(1,10) :
            driver.execute_script("arguments[0].scrollBy(0, 1300)", scroll)
            time.sleep(0.2)

        # 장소 이름 클릭하면 상세 보기 페이지로 이동 -> 클릭정보 가져오기
        detail_info_url = driver.find_elements(By.CSS_SELECTOR,detail_info_p)
        print("페이지 하나 개수 : ", len(detail_info_url))
        #Start Crawling
        for index_inner in tqdm(range(len(detail_info_url))) :
            detail_info_url[index_inner].click()

            #Frame 변경 < Place_Detail_info  >
            driver.implicitly_wait(1)
            driver.switch_to.window(driver.window_handles[1])
            detail_info_frame = driver.find_element(By.ID,'entryIframe')
            driver.switch_to.frame(detail_info_frame)

            #매장명 크롤링
            try :
                name_t = driver.find_element(By.CSS_SELECTOR,name_p)
                name.append(name_t.text)
            except :
                name.append(None)

            #매장 주소 크롤링
            try :
                address_t = driver.find_element(By.CSS_SELECTOR,address_p)
                address_str = address_t.text
                address.append(address_str)
            except :
                address.append(None)

            #행정동 크롤링
            try :
                administrativeDong_t = address_str.split('김천시')[1].strip().split(' ')[0]
                administrativeDong.append(administrativeDong_t)
            except :
                administrativeDong.append(None)


            #위도 경도 저장
            gmaps=googlemaps.Client(key = gmaps_key)

            #한국 위도 경도 최소, 최댓값 정의
            max_lat = 38.0
            min_lat = 33.0
            max_lng = 132.0
            min_lng = 126.0

            geo_list = []

            try :
                tmp = gmaps.geocode(address_str, language = "ko")

                if tmp :
                    tmp_loc = tmp[0].get("geometry")
                    tmp_lat = tmp_loc["location"]["lat"]
                    tmp_lng = tmp_loc["location"]["lng"]

                    if (tmp_lat > max_lat or tmp_lat < min_lat or tmp_lng > max_lng or tmp_lng < min_lng):
                        geo_list.append("0")
                        geo_list.append("0")
                    else :
                        geo_list.append(tmp_lat)
                        geo_list.append(tmp_lng)
                else :
                    geo_list.append("0")
                    geo_list.append("0")
            except :
                geo_list.append("0")
                geo_list.append("0")

            geo.append(geo_list)


            #홈페이지 주소 크롤링
            try :
                siteUrl_t = driver.find_element(By.CSS_SELECTOR,siteUrl_p)
                siteUrl.append(siteUrl_t.get_attribute('href'))
            except:
                siteUrl.append(None)
            #매장 설명 크롤링
            try :
                # 펼처보기가 있는 경우
                driver.find_element(By.CSS_SELECTOR,'div.place_section.no_margin > div > ul > li._1M_Iz._3__3i > div > a > span.dX2wL > svg').click()
                driver.implicitly_wait(1)
                description_t = driver.find_element(By.CSS_SELECTOR,description_more_p)

                description.append(description_t.text.replace("\n"," "))
            except :
                # 펼처보기가 없는 경우
                try :
                    description_t = driver.find_element(By.CSS_SELECTOR,description_nomore_p)
                    description.append(description_t.text.replace("\n"," "))
                except :
                    description.append(None)


            #매장 전화 번호 크롤링
            try :
                telephone_t = driver.find_element(By.CSS_SELECTOR,telephone_p)
                telephone.append(telephone_t.text)
            except :
                telephone.append(None)


            #매장 분류 크롤링 (모텔 , 호텔 등등)
            try :
                lodgingCategory_t = driver.find_element(By.CSS_SELECTOR,lodgingCategory_p)
                lodgingCategory.append(lodgingCategory_t.text)
            except :
                lodgingCategory.append(None)


            #별점 크롤링
            try :
                aggregate_rating_t = driver.find_element(By.CSS_SELECTOR,aggregate_rating_p)
                aggregate_rating.append(aggregate_rating_t.text)
            except :
                aggregate_rating.append(None)


            #객실 정보 크롤링
            #dict 형태로 저장 roomType = [  {방이름 , 가격 , 방설명} , ,'''   ]

            try :
                #객실 더보기 클릭
                driver.find_element(By.CSS_SELECTOR,'#app-root > div > div > div.place_detail_wrapper > div > div > div.place_section._3mkep > div._2kAri > a').click()
                driver.implicitly_wait(1)

                roomName_t =[]
                roomPrice_t = []
                roomDescript_t = []
                room_dict = {}

                roomName = driver.find_elements(By.CSS_SELECTOR,'div.place_section._1gjmL > div > ul > li > a > div._1Tcwx > div._29WF6 > div > span')
                roomPrice = driver.find_elements(By.CSS_SELECTOR,'div.place_section._1gjmL > div > ul > li > a > div._1Tcwx > div._2QlZz > span.FSeNw')
                roomDescript = driver.find_elements(By.CSS_SELECTOR,'div.place_section._1gjmL > div > ul > li > a > div._1Tcwx > div._33Hep')

                for i in range(len(roomName)) :
                    try :
                        roomName_t.append(roomName[i].text)
                    except :
                        roomName_t.append(None)
                    try :
                        roomPrice_t.append(roomPrice[i].text)
                    except :
                        roomPrice_t.append(None)
                    try :
                        roomDescript_t.append(roomDescript[i].text)
                    except :
                        roomDescript_t.append(None)

                room_dict['roomName'] = roomName_t
                room_dict['roomPrice'] = roomPrice_t
                room_dict['roomDescription'] = roomDescript_t

                roomType.append(room_dict)
            except :
                roomType.append(None)

            #이미지 url
            try :
                #이미지 더보기 클릭
                driver.find_element(By.CSS_SELECTOR,'#_autoPlayable').click()
                time.sleep(0.8)
                images = driver.find_elements(By.CSS_SELECTOR,'ul._3TiO6._1wsFm > li._2OSze > a > img')

                images_t = []

                for img_index in range(len(images)) :
                    images_t.append(images[img_index].get_attribute('src'))

                imageUrl.append(images_t)
            except :
                imageUrl.append(None)
            print('-------------------------')
            print('name : ',name[index_inner])
            print('administratorDong',administrativeDong[index_inner])
            print('lodgingCategory : ',lodgingCategory[index_inner])
            print('telephone : ',telephone[index_inner])
            print('address : ',address[index_inner])
            print('siteUrl : ',siteUrl[index_inner])
            print('description : ',description[index_inner])
            print('aggregate_rating',aggregate_rating[index_inner])
            print('roomType : ',roomType[index_inner])
            print('geo :',geo[index_inner])
            print('images :',imageUrl[index_inner])

            #Frame 변경 < Search_List_Place >
            driver.implicitly_wait(1)
            driver.switch_to.window(driver.window_handles[1])
            back_frame = driver.find_element(By.ID,'searchIframe')
            driver.switch_to.frame(back_frame)
        try :
            #Next Page Click
            driver.find_element(By.CSS_SELECTOR,next_page_p).click()
        except :
            break

    datalist['name'] =  datalist['name'] + name
    datalist['address'] =  datalist['address'] + address
    datalist['geo'] =  datalist['geo'] + geo
    datalist['siteUrl'] =  datalist['siteUrl'] + siteUrl
    datalist['administrativeDong'] =  datalist['administrativeDong'] + administrativeDong
    datalist['lodgingCategory'] =  datalist['lodgingCategory'] + lodgingCategory
    datalist['roomType'] =  datalist['roomType'] + roomType
    datalist['description'] =  datalist['description'] + description
    datalist['aggregate_rating'] =  datalist['aggregate_rating'] + aggregate_rating
    datalist['telephone'] =  datalist['telephone'] + telephone
    datalist['imageUrl'] =  datalist['imageUrl'] + imageUrl
    return datalist

def foodCrawler(datalist) :
    pass

def tourCrawler(datalist) :
    pass

def to_csv(datalist,value) :
    naverPlace_df = pd.DataFrame(datalist)
    fileName = '김천숙소'
    filePath = os.path.abspath('.') + '\data\\'+fileName
    print(naverPlace_df.head(3))
    print(naverPlace_df.tail(3))
    print(len(naverPlace_df))

    result = naverPlace_df.drop_duplicates('address')
    print(len(naverPlace_df))
    print(len(result))

    today = datetime.datetime.now()
    currentDate = today.strftime("%Y%m%d")

    filePath = os.path.abspath('.') + '\data\\'+currentDate+fileName
    result.to_csv(filePath)

def get_datalist(value) :
    if not value in query_list :
        print('Target Error')
        return None;

    #숙박 데이터 리스트 반환
    if value == '숙박' :
        data_list = {
            'dataSource' : 'NaverPlace',
            'name' : list(),
            'address' : list(),
            'geo' : list(),
            'siteUrl' : list(),
            'tourArea' : list(),
            'administrativeDong' :list(),
            'lodgingCategory' : list(),
            'roomType' :list(),
            'description' : list(),
            'aggregate_rating' : list(),
            'star_rating' : list(),
            'officalRating' : list(),
            'facility' : list(),
            'lastUpdate': list(),
            'telephone' : list(),
            'imageUrl' : list(),
            'event': list()
        }
    #음식 데이터 리스트 반환
    elif value == '음식' :
        pass
    #관광 데이터 리스트 반환
    else :
        pass

    return data_list

def enterCrawlTarget(driver,query) :
    driver.implicitly_wait(10)
    driver.find_element(By.ID,'query').send_keys(query)
    driver.find_element(By.ID,'search_btn').click()

    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR,'#place-app-root div.api_more_wrap').click()
    driver.switch_to.window(driver.window_handles[1])
    element = driver.find_element(By.XPATH,'//*[@id="searchIframe"]')
    driver.switch_to.frame(element)