import requests
import uuid
import os
from bs4 import BeautifulSoup

try:
    import requests
    from bs4 import BeautifulSoup
    import csv

    # Webページを取得する
    url = 'https://kakaku.com/drink/whiskey/itemlist.aspx'
    response = requests.get(url)

    # HTML解析のためにBeautifulSoupを使用する
    soup = BeautifulSoup(response.content, 'html.parser')

    # csvファイルを開く
    with open('whiskey.csv', mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['画像パス', '商品名称', 'メーカー名', '商品種類', 'アルコール度数'])

        index = 1
        # 商品情報を含むすべての要素を取得する
        items = soup.select('tr[class="tr-border"]')
        for item in items:
            # 商品情報を取得する(tr-borderが3つで1セットであるため)
            if index % 3 == 1:
                maker = item.find('span').getText().strip()
            elif index % 3 == 2:
                img_url = item.find('a', {'class': 'withIcnLimited'}).find('img')['src']
                img_response = requests.get(img_url)
                with open(str('./images/')+str(uuid.uuid4())+str('.jpeg'),'wb') as file:
                        file.write(img_response.content)
                file_path = os.path.abspath(file.name)
                name = item.select('img')[0].get('alt')
                kind = item.find('span', {'class': 'sortBox'}).find('a').getText().strip()
                degreeHTML = item.find('td', {'class': 'end'}).find('span', {'class': 'typeClk'})
                degree = degreeHTML.getText().strip() if degreeHTML is not None else ''

                # 取得したデータをcsvファイルに書き込む
                writer.writerow([file_path,name, maker, kind, degree])

            index+=1

except ZeroDivisionError as e:
    print(e)
