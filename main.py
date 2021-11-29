from spiders import NaverPlaceSpider
from spiders import InstagrameSpider
from spiders import NaverBlogSpider
from spiders import GoogleMapSpider

if __name__ == '__main__':

    category = ['숙박','관광','음식']

    #컨텐츠크롤링
    #NaverPlaceSpider.scrapNaverPlace(category[0])
    #카카오맵

    #포스팅크롤링
    #InstagrameSpider.scrapNaverPlace(category[0])
    #NaverBlogSpider.scrapNaverBlog(category[1])

    #리뷰크롤링
    GoogleMapSpider.scrapGoogleMaps(category[0])
    #네이버 플레이스

    #전체크롤링
    #for index in range(len(category)) :
    #    NaverPlaceSpider.scrapNaverPlace(category[index])
    #    InstagrameSpider.scrapNaverPlace(category[index])
    #    NaverBlogSpider.scrapNaverBlog(category[index])


    #Kakaomaps
    #망고 플레이트
    #1. 관광, 음식 따라 구조변경
    #2. 리뷰 크롤러 <NaverPlace , GooglePlace > + naverplace ?
    #2. 관광지 권역 설정 및 변경
    #3. facility 설정 및 integer control 가능한 변수 변경필요


