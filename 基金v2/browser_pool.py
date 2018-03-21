import threading
import time
from queue import Queue, Empty

import psutil as psutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#============= Object ======================
browser_pool = None # Browser Pool Object
#============= Config ======================
browser_amount = 0 # If browser_amount <= 0 , means unlimit, then lazy_load must be True
minimize = False

memory_rate = 90

lazy_load = True
log_silence = True # 输出安静
#== Option Config ==
load_picture = False
head_less = False
#=======================================
if not load_picture or head_less:
    use_chrome_options = True

chrome_options = Options()
if not load_picture:
    chrome_options.add_experimental_option('prefs', {
        'profile.default_content_setting_values': {
            'images': 2
        }
    })
if head_less:
    chrome_options.add_argument('--headless')
#============= Program ====================
class Browser_Pool:
    '''
    浏览器池
    '''
    def __init__(self):
        self.browsers = []
        self._acquire_queue = Queue(maxsize=-1)
        self._done = False

        self._create_browser()
        self._acquire()
        self._cleaner()

    def _create_browser(self):
        '''
        创建 浏览器
        :param id:浏览器编号
        '''
        def create(id):
            browser = Browser(id, self)
            self.browsers.append(browser)

        threads = []
        if not lazy_load and browser_amount>0:
            for index in range(browser_amount):
                thread = threading.Thread(target=create, args=(index,))
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()

    def close(self):
        '''
        销毁 浏览器池
        '''
        self.clean()
        self._done = True

    def _acquire(self,):
        '''
        监听/分配 浏览器 线程
        '''
        def distribut():
            while not self._done:
                try:
                    bowl = self._acquire_queue.get(timeout=0.5)
                except Empty:
                    if self._done:
                        break
                    else:
                        continue
                found = False
                while not found:
                    for browser in self.browsers:
                        if browser.vailiable:
                            browser.vailiable = False
                            bowl.bowl = browser
                            found = True
                            break
                    if bowl.isclean : break
                    if not found and (browser_amount<1 or len(self.browsers)<browser_amount) \
                            and psutil.virtual_memory().percent<memory_rate:
                        browser = Browser(len(self.browsers), self)
                        self.browsers.append(browser)
                        browser.vailiable = False
                        bowl.bowl = browser
                        found = True
                    if not found:
                        time.sleep(0.05)
        threading.Thread(target=distribut).start()

    class _Bowl:
        '''
        申请 碗
        '''

        def __init__(self, isclean = False):
            self.isclean = isclean
            self.bowl = None

    def acquire(self):
        '''
        申请 浏览器
        '''
        bowl = self._Bowl()
        self._acquire_queue.put(bowl)
        while bowl.bowl == None:
            time.sleep(0.05)
        return bowl.bowl

    def _acquire_for_cleaner(self):
        '''
        申请 浏览器 for cleaner
        '''
        bowl = self._Bowl(isclean=True)
        self._acquire_queue.put(bowl)
        while bowl.bowl == None and len(self.browsers)>0:
            time.sleep(0.05)
        return bowl.bowl

    def _cleaner(self):
        '''
        自清理，高于内存使用率时 自动清理多余浏览器
        '''
        def cleanner():
            while not self._done:
                if psutil.virtual_memory().percent >= memory_rate:
                    browser = self._acquire_for_cleaner()
                    if browser != None:
                        browser.destroy_by_force()
                time.sleep(0.05)
        threading.Thread(target=cleanner).start()

    def clean(self):
        '''
        清空 浏览器池
        '''
        def destroy_browser(browser):
            if browser != None:
                c_out('浏览器[{}] 已被销毁。'.format(browser.id))
                browser.destroy_by_force()
        while len(self.browsers)>0:
            browser = self._acquire_for_cleaner()
            threading.Thread(target=destroy_browser, args=(browser,)).start()
            time.sleep(0.05)

class Browser(webdriver.Chrome):
    '''
    浏览器 驱动
    '''
    def __init__(self, id : int = -1, browser_pool=None):
        '''
        Initialize
        :param id:Browser Id, If id is defult(-1) means nameless
        '''
        if use_chrome_options:
            super(Browser, self).__init__(chrome_options = chrome_options)
        else:
            super(Browser, self).__init__()

        self.browser_pool = None
        self.id = id
        self.vailiable = True

        if browser_pool != None:
            self.browser_pool = browser_pool

        c_out('浏览器[{}] 已被创建。'.format(id))
        if minimize:
            self.set_window_size(0, 0)

    def release(self, str = None):
        if str != None:
            print(str)
        self.get('about:blank')
        self.vailiable = True
        c_out('浏览器编号[{}] 已被释放。'.format(self.id))

    def destroy_by_force(self):
        self.quit()
        self.browser_pool.browsers.remove(self)

    def browser_amount(self):
        c_out('当前浏览器数量 : {}'.format(len(self.browser_pool.browsers)))

def c_out(*args):
    if not log_silence:
        print('\033[0;32;0m', end='')
        print(*args, '\033[0m')
#=============== Object =======================
# 浏览器池 引用
browser_pool = Browser_Pool()

#=============== Test =======================
def run():
    import time

    browser = browser_pool.acquire()
    browser.get('http://baidu.com')
    browser.release()

    time.sleep(1)
    browser_pool.close()

if __name__ == '__main__':
    run()