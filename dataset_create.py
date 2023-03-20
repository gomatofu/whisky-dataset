import pandas as pd
import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split
import os
import tensorflow as tf
from keras import layers

# CSVファイルの読み込み
csv_path = 'whisky_data.csv'
df = pd.read_csv(csv_path)

# 画像データの読み込みと前処理
def load_image(image_path):
    img = Image.open(image_path).convert('RGB')
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    return img_array

# 商品名称を数値にエンコード
labels = pd.Categorical(df['product_name']).codes

# 画像データの読み込みと前処理
images = []
valid_labels = []

for index, row in df.iterrows():
    image_path = row['image_path']
    
    if os.path.exists(str(image_path)):
        try:
            img = load_image(image_path)
            images.append(img)
            valid_labels.append(labels[index])
        except:
            print(f"Failed to load image: {image_path}")
    else:
        print(f"Image not found: {image_path}")

# データセットの分割
X_train, X_test, y_train, y_test = train_test_split(images, valid_labels, test_size=0.2, random_state=42)

# Convert X_train, X_test, y_train, and y_test to NumPy arrays
X_train = np.array(X_train)
X_test = np.array(X_test)
y_train = np.array(y_train).astype(np.int32)
y_test = np.array(y_test).astype(np.int32)

# モデルの作成
model = tf.keras.Sequential([
    layers.Input(shape=(224, 224, 3)),
    layers.Conv2D(32, kernel_size=(3, 3), activation='relu'),
    layers.MaxPooling2D(pool_size=(2, 2)),
    layers.Conv2D(64, kernel_size=(3, 3), activation='relu'),
    layers.MaxPooling2D(pool_size=(2, 2)),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dense(len(np.unique(labels)), activation='softmax')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# モデルの訓練
history = model.fit(X_train, y_train, epochs=10, validation_split=0.1)

# モデルの評価
test_loss, test_acc = model.evaluate(X_test, y_test)
print('Test accuracy:', test_acc)

# モデルの保存
model.save('whisky_model.h5')

# 商品名のリストを作成
product_names = pd.Categorical(df['product_name']).categories

# 商品名のリストをファイルに保存
with open("product_names.txt", "w") as f:
    for name in product_names:
        f.write(name + "\n")
