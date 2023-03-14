import requests
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
        writer.writerow(['画像URL', '商品名', 'メーカー名', '商品種類', 'アルコール度数'])

        index = 1
        # 商品情報を含むすべての要素を取得する
        items = soup.select('tr[class="tr-border"]')
        for item in items:
            # # 商品画像を取得して保存する
            # img_url = item.find('img')['src']
            # img_response = requests.get(img_url)
            # with open('images/' + item.find('p', {'class': 'p-item__ttl'}).text.strip() + '.jpg', mode='wb') as img_file:
            #     img_file.write(img_response.content)
            # img_path = 'images/' + item.find('p', {'class': 'p-item__ttl'}).text.strip() + '.jpg'

            # 商品情報を取得する(奇数時：メーカー、偶数時：以外)
            if index % 2 != 0:
                maker = item.find('span').getText().strip()
            else:
                name = item.select('img')[0].get('alt')
                kind = item.find('span', {'class': 'sortBox'}).find('a').getText().strip()
                degree = item.find('td', {'class': 'end'}).find('span', {'class': 'typeClk'}).getText().strip()

                # 取得したデータをcsvファイルに書き込む
                writer.writerow([name, maker, kind, degree])

            index+=1

except ZeroDivisionError as e:
    print(e)
