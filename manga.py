from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import time
import os
from tqdm import tqdm,trange
from lxml import html
import lzstring
import argparse

menuURL = "https://www.manhuagui.com/comic/3279/"




parser = argparse.ArgumentParser()

parser.add_argument('-s', type=str, help='请输入搜索内容（支持拼音）')

args = parser.parse_args()

if args.s:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }

    cookies = {
        'isAdult': '1'
    }

    search_url = "https://www.manhuagui.com/s/" + args.s + ".html"

    response = requests.get(search_url,headers=headers, cookies=cookies)

    tree = html.fromstring(response.content)

    search_data = tree.xpath('//dt/a')

    stitle_list = []
    shref_list = []

    for s in search_data:
        title = s.get('title')
        href = s.get('href')
        
        if title:
            stitle_list.append(title)
        if href:
            shref_list.append(href)
            
    for i,search_name in enumerate(stitle_list):
        print(str(i) + " : " + search_name)
        
    menuURL = "https://www.manhuagui.com" + shref_list[int(input("请选择漫画（输入编号）"))]




headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

cookies = {
    'isAdult': '1'
}

response = requests.get(menuURL,headers=headers, cookies=cookies)

tree = html.fromstring(response.content)

input_element = tree.xpath('//input[@id="__VIEWSTATE"]')

if input_element:
    value = input_element[0].get("value")

    decoded_html = lzstring.LZString().decompressFromBase64(value)

    tree = html.fromstring(decoded_html)

a_tags = tree.xpath('//a[@class="status0"]')

page_tags = tree.xpath('//a[@class="status0"]/span/i')

title_list = []
href_list = []
page_list = []

for a in a_tags:
    title = a.get('title')
    href = a.get('href')
    
    if title:
        title_list.append(title)
    if href:
        href_list.append(href)

for page in page_tags:

    pageNum = page.text
    
    if pageNum:
        page_list.append(pageNum)


for i,chapter_name in enumerate(title_list):
    print(str(i) + " : " + chapter_name + ";     本章页数：" + page_list[i])

thisChapterNum = input("请选择下载内容（输入编号）")
mangaURL = "https://www.manhuagui.com" + href_list[int(thisChapterNum)]

proxy_ip = "127.0.0.1"
proxy_port = "7890"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f"--proxy-server={proxy_ip}:{proxy_port}")
chrome_options.add_argument("--headless")
chrome_options.add_argument('–disable-gpu')
chrome_options.add_argument('log-level=3')

driver = webdriver.Chrome(options=chrome_options)
driver.get(mangaURL)
driver.add_cookie({"name":"country","value":"US"})
driver.add_cookie({"name":"isAdult","value":"1"})
driver.refresh()
driver.get(mangaURL)
chapter_title = driver.title
os.makedirs("./" + chapter_title, exist_ok=True)


page_1_data = driver.find_element(By.XPATH, '//img[@id="mangaFile"]').get_attribute('src')

url = page_1_data
headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer":"https://www.manhuagui.com/"
}
response=requests.get(url,headers=headers)
image_data=response.content
with open("./" + chapter_title + "/1.jpg","wb") as file:
    file.write(image_data)

pageNumber = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/span').text
pageNumber = pageNumber.split('/')
pageNumber = pageNumber[1].strip(')')


for page in tqdm(range(2, int(pageNumber)+1),desc = ("正在下载:" + title_list[int(thisChapterNum)])):
    # 点击下一页按钮
    next_page_button = driver.find_element(By.XPATH, '//a[text()="下一页"]')
    next_page_button.click()
    
    # 等待页面加载完成
    driver.implicitly_wait(10)
    
    # 获取当前页的数据
    current_page_data = driver.find_element(By.XPATH, '//img[@id="mangaFile"]').get_attribute('src')
    url = current_page_data
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer":"https://www.manhuagui.com/"
    }
    response=requests.get(url,headers=headers)
    image_data=response.content
    with open("./" + chapter_title + "/"+str(page)+".jpg","wb") as file:
        file.write(image_data)

"""
next_url_button = driver.find_element(By.XPATH, '//a[text()="下一章"]')
next_url_button.click()
time.sleep(5)
next_url = driver.current_url
print("下一章链接为：" + next_url)
"""

driver.quit()
