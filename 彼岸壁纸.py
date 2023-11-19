import requests
from bs4 import BeautifulSoup
import re
import os
import time
from prettytable import PrettyTable

cookies = {
    'trenvecookieclassrecord': '%2C17%2C7%2C12%2C19%2C',
    'trenvecookieinforecord': '%2C17-32587%2C17-32504%2C12-32585%2C19-32254%2C',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Referer': 'http://www.netbian.com/youxi/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
}

photo_list = []
category_dict = {}  # Define category_dict globally

directory = input('请输入你想要创建的文件夹名称: ')

if not os.path.exists(directory):
    os.makedirs(directory)

def display_category_table(links):
    table = PrettyTable()
    table.field_names = ["类目", "类目的网页链接"]

    for link in links:
        title = link.text
        key = link['href']
        full_url = f'http://www.netbian.com{key}'
        category_dict[title] = full_url
        table.add_row([title, full_url])

    print(table)

def get_id():
    url = 'http://www.netbian.com/'
    response = requests.get(url)
    response.encoding = "gbk"
    soup = BeautifulSoup(response.text, 'html.parser')
    all_id = soup.find('div', class_='nav cate')
    links = all_id.find_all('a')
    display_category_table(links)

    # User input for category
    user_input = input("请输入一个类目: ")
    page_input = input('请输入你想获取页数，每一页大概20张图: ')

    # Check if the user input is in the category_dict
    if user_input in category_dict:
        lin = category_dict[user_input]

        for i in range(2, int(page_input)):
            try:
                response = requests.get(f'{lin}index_{i}.htm', cookies=cookies, headers=headers)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error during the request: {e}")
                exit()

            response.encoding = "gbk"

            soup = BeautifulSoup(response.text, 'html.parser')

            img_list = soup.find('div', class_='list')

            if img_list:
                lists = img_list.find_all('li')
                for image in lists:
                    images = {}
                    href_tag = image.find('a')

                    if href_tag:
                        href = href_tag.get('href', '')
                        if href.endswith('m'):
                            title = href_tag.get('title')
                            if title:
                                parts = title.split(' 更新时间', 1)
                                result = parts[0].strip()

                                # Add to the images dictionary only if both href and title are present
                                if href and title:
                                    images['href'] = href
                                    images['title'] = title

                    # Check if the images dictionary is not empty before appending
                    if images:
                        photo_list.append(images)

def download_picture():
    get_id()
    for photograph in photo_list:
        pid = photograph['href']
        number = pid.split('/')[-1].split('.')[0]
        title = photograph['title']
        base_link = 'http://www.netbian.com'
        total_link = base_link + pid
        response = requests.get(url=total_link, headers=headers, cookies=cookies)
        response.encoding = "gbk"
        picture_url = re.findall(f'<div class="pic"><p><a href="/desk/{number}-1920x1080.htm" target="_blank"><img src="(.*?)"', response.text)

        if picture_url:
            r = requests.get(picture_url[0])
            content = r.content

            file_name = os.path.join(directory, title + '.jpg')

            try:

                with open(file_name, mode='wb') as f:
                    f.write(content)
                    time.sleep(0.5)
                    print(f'{title} has been downloaded')
            except:
                pass


download_picture()
