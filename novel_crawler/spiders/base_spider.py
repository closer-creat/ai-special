import requests
import time
import random
import threading
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

class BaseSpider:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.update_headers()
        # 使用threading.local()来为每个线程存储自己的driver实例
        self.local = threading.local()
        # 存储所有线程的driver实例，以便在爬虫结束时关闭
        self.drivers = []
    
    def update_headers(self):
        """更新请求头，使用随机User-Agent"""
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.fanqie.com/',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1'
        }
    
    def get_html(self, url, use_selenium=False):
        """获取页面HTML，支持requests和selenium两种方式"""
        max_retries = 3
        for retry in range(max_retries):
            try:
                if use_selenium:
                    try:
                        return self._get_html_selenium(url)
                    except Exception as e:
                        print(f"Selenium获取页面失败，尝试使用requests: {e}")
                        # 降级使用requests
                        return self._get_html_requests(url)
                else:
                    return self._get_html_requests(url)
            except Exception as e:
                print(f"获取页面失败 (尝试 {retry+1}/{max_retries}): {e}")
                if retry < max_retries - 1:
                    print("等待后重试...")
                    time.sleep(random.uniform(5, 10))
                else:
                    print("达到最大重试次数，放弃获取")
                    return None
    
    def _get_html_requests(self, url):
        """使用requests获取页面"""
        self.update_headers()
        print(f"使用requests获取页面: {url}")
        print(f"请求头: {self.headers}")
        response = self.session.get(url, headers=self.headers, timeout=20)
        print(f"响应状态码: {response.status_code}")
        print(f"响应编码: {response.encoding}")
        print(f"响应内容长度: {len(response.text)}")
        # 打印响应内容的前500个字符，以便查看是否是反爬页面
        print(f"响应内容预览: {response.text[:500]}...")
        response.encoding = response.apparent_encoding
        # 添加随机延迟，避免反爬
        time.sleep(random.uniform(2, 4))
        return response.text
    
    def _get_html_selenium(self, url):
        """使用selenium获取页面"""
        driver = self.get_driver()
        try:
            driver.get(url)
            # 模拟人类浏览行为
            time.sleep(random.uniform(2, 4))  # 减少等待时间
            # 模拟滚动页面
            for i in range(2):  # 减少滚动次数
                driver.execute_script(f"window.scrollTo(0, {i*300});")
                time.sleep(random.uniform(0.5, 1))  # 减少等待时间
            html = driver.page_source
            return html
        except Exception as e:
            print(f"Selenium获取页面失败: {e}")
            return None
    
    def get_soup(self, html):
        if html:
            return BeautifulSoup(html, 'lxml')
        return None
    
    def close_driver(self):
        """关闭所有selenium driver实例"""
        for driver in self.drivers:
            try:
                driver.quit()
            except Exception as e:
                print(f"关闭driver失败: {e}")
        # 清空drivers列表
        self.drivers.clear()
        # 清除线程本地存储
        if hasattr(self, 'local'):
            if hasattr(self.local, 'driver'):
                delattr(self.local, 'driver')
    
    def get_driver(self):
        # 为每个线程返回自己的driver实例
        if not hasattr(self.local, 'driver'):
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument(f'user-agent={self.ua.random}')
            # 禁用自动化特征
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            # 执行JavaScript以隐藏webdriver特征
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            # 存储到线程本地和全局列表
            self.local.driver = driver
            self.drivers.append(driver)
        return self.local.driver