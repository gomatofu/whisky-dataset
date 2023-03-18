import requests
import uuid
import os
from bs4 import BeautifulSoup
import csv

try:
    # csvファイルを開く
    with open('whisky_data.csv', mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['image_path', 'product_name', 'manufacturer', 'category', 'alcohol_content'])

        
        # Webページを取得する
        for i in range(1,17):
            if i > 1:
                url = 'https://kakaku.com/drink/whiskey/itemlist.aspx?pdf_pg=' + str(i)
            else:
                url = 'https://kakaku.com/drink/whiskey/itemlist.aspx'
            response = requests.get(url)

            # HTML解析のためにBeautifulSoupを使用する
            soup = BeautifulSoup(response.content, 'html.parser')

            index = 1
            # 商品情報を含むすべての要素を取得する
            items = soup.select('tr[class="tr-border"]')
            for item in items:
                # 商品情報を取得する(tr-borderが3つで1セットであるため)
                if index % 3 == 1:
                    manufacturer = item.find('span').getText().strip()
                elif index % 3 == 2:
                    img_url = item.find('a', {'class': 'withIcnLimited'}).find('img')['src']
                    if img_url is not None:
                        # timeout対策
                        try:
                            img_response = requests.get(img_url,timeout=3)
                            with open(str('./images/')+str(uuid.uuid4())+str('.jpeg'),'wb') as file:
                                    file.write(img_response.content)
                            image_path = os.path.abspath(file.name)
                        except:
                            image_path = ''
                    else:
                        image_path = ''
                    product_name = item.select('img')[0].get('alt')
                    product_typeHTML = item.find('span', {'class': 'sortBox'}).find('a')
                    product_type = product_typeHTML.getText().strip() if product_typeHTML is not None else ''
                    alcoholHTML = item.find('td', {'class': 'end'}).find('span', {'class': 'typeClk'})
                    alcohol = alcoholHTML.getText().strip().replace('度', '') if alcoholHTML is not None else ''

                    # 取得したデータをcsvファイルに書き込む
                    writer.writerow([image_path,product_name, manufacturer, product_type, alcohol])

                index+=1

except ZeroDivisionError as e:
    print(e)
