import numpy as np
from PIL import Image
import tensorflow as tf
import pandas as pd

def load_product_names(file_path):
    with open(file_path, "r") as f:
        names = [line.strip() for line in f.readlines()]
    return names

def load_image(image_path):
    img = Image.open(image_path).convert('RGB')
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    return img_array


def predict_whisky_name(model, image_path, product_names):
    # 画像を読み込み、前処理する
    img = load_image(image_path)
    img = np.expand_dims(img, axis=0)  # Add batch dimension

    # 予測を行う
    predictions = model.predict(img)

    # 最も確率が高いカテゴリのインデックスを取得
    predicted_index = np.argmax(predictions, axis=1)[0]

    # インデックスを商品名にデコード
    predicted_name = product_names[predicted_index]

    return predicted_name

# 商品名のリストをファイルから読み込む
product_names = load_product_names("product_names.txt")

# 保存されたモデルを読み込む
loaded_model = tf.keras.models.load_model("whisky_model.h5")

# 予測したい画像のファイルパス
test_image_path = "C:\\goto\\src\\python\\whisky-dataset\\test_images\\m91229481069_1.jpg"

# 画像を使って商品名を予測する
predicted_name = predict_whisky_name(loaded_model, test_image_path, product_names)

print(f"Predicted whisky name: {predicted_name}")
