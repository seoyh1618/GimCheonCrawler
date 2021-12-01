from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy,ProxyType
import random

# Chrome Driver Path Settings

def get_driver(driver_path) :
    # select random IP
    user = UserAgent(verify_ssl=False)
    random_user  = user.random

    # Chrome Init
    chrome_options = Options()
    #chrome_options.add_argument("headless")
    chrome_options.add_argument("window-size=1920x1080")
    chrome_options.add_argument(f'user-agent={random_user}')

    proxy = get_proxy()

    #Setting Proxy
    proxy = Proxy()
    proxy.proxyType = ProxyType.MANUAL
    proxy.autodetect = False
    proxy.httpProxy = proxy.sslProxy = proxy.socksProxy = "127.0.0.1:9000"
    chrome_options.proxy = proxy

    chrome_options.add_argument("ignore-certificate-errors")

    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=driver_path)
    return driver

def get_proxy() :
    proxy_list = ["188.40.183.185:1080",
                  "203.19.92.3:80",
                  "203.202.245.58:80",
                  "190.93.156.107:8080",
                  "201.55.160.99:3128",
                  "191.102.116.114:999",
                  "35.220.131.188:80",
                  "36.37.177.186:8080",
                  "205.185.127.8:8080",
                  "27.255.58.72:8080",
                  "52.53.135.163:3128",
                  "109.74.130.129:8080",
                  "125.62.192.225:83"]
    return random.choice(proxy_list)