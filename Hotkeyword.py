#coding=utf-8

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from pyquery import PyQuery as pq
from jieba import analyse
import time


browser = webdriver.Chrome()
wait = WebDriverWait(browser,10)

def login():
    browser.get('https://weibo.com/')
    time.sleep(2)
    input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR,'#loginname'))
    )
    # username为用户名
    input.send_keys('username')
    input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR,'#pl_login_form > div > div:nth-child(3) > div.info_list.password > div > input'))
    )
    time.sleep(1)
    # password为密码
    input.send_keys('password')
    button = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR,'#pl_login_form > div > div:nth-child(3) > div.info_list.login_btn > a'))
    )
    time.sleep(2)
    button.click()

def getHot():
    browser.get('https://s.weibo.com/top/summary?Refer=top_hot&topnav=1&wvr=6')
    for i in range(2,12):
        button = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,'#pl_top_realtimehot > table > tbody > tr:nth-child('+str(i)+') > td.td-02 > a'))
        )
        yield button

def get_detail_content():
    weibos = []
    target = 1
    for button in getHot():
        weibo = []
        weibo.append(button.text)
        print(button.text)
        button.click()
        browser.switch_to.window(browser.window_handles[target])
        target+=1
        html = browser.page_source
        # 把xmlns去掉，下面对a标签的remove才能生效
        html = html.replace('xmlns="http://www.w3.org/1999/xhtml"','')
        doc = pq(html)
        all_contents = doc('.m-main .m-wrap .m-con-l .card-wrap').items()
        all_contents = list(all_contents)
        true_content = ''
        for con in all_contents[1:6]:
            temp = con('.card .card-feed .content .txt')
            temp('a').remove()
            c = temp.text()
            c = c.replace('\n','')
            true_content+=c+' '
        # print(true_content)
        keywords = analyse.textrank(true_content,topK=20)
        weibo.append(keywords)
        time.sleep(6)
        browser.switch_to.window(browser.window_handles[0])
        weibos.append(weibo)
    return weibos

def release_weibo(weibos):
    main_button = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR,'#weibo_top_public > div > div > div.gn_position > div.gn_nav > ul > li:nth-child(1) > a'))
    )
    main_button.click()
    input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR,'#v6_pl_content_publishertop > div > div.input > textarea'))
    )
    input.clear()
    now = time.strftime('%Y-%m-%d')
    weibo_content=''
    weibo_content+=now
    weibo_content+=' 让我们来看看今天都发生了什么事儿~\n'
    for num,item in enumerate(weibos):
        weibo_content += str(num+1)+'.#'+item[0]+'#\n'
        for key in item[1]:
            weibo_content += key+' '
        weibo_content+='\n'

    input.send_keys(weibo_content)
    release_button = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR,'#v6_pl_content_publishertop > div > div.func_area.clearfix > div.func > a'))
    )
    time.sleep(3)
    release_button.click()


if __name__=='__main__':
    login()
    time.sleep(6)
    weibo = get_detail_content()
    release_weibo(weibo)


