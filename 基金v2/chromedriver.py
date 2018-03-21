from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# TODO : Abandon
def web_driver():
    '''浏览器驱动'''
    chrome_options = Options()
    chrome_options.add_experimental_option('prefs',{
        'profile.default_content_setting_values': {
            'images': 2
        }
    })
    # 无头浏览
    # chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(chrome_options=chrome_options)
    # 有头浏览
    # browser = webdriver.Chrome()
    return browser
