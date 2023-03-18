import pandas as pd
import numpy as np
from PIL import Image
import tensorflow as tf
import os
from keras import layers, models

csv_file = "whisky_data.csv"
df = pd.read_csv(csv_file)

images = []
product_names = []
manufacturers = []
categories = []
alcohol_contents = []

for index, row in df.iterrows():
    # 画像ファイルが存在しない場合
    if not os.path.isfile(str(row['image_path'])):
        continue
    image = Image.open(row['image_path']).convert('RGB')
    image = image.resize((224, 224), Image.ANTIALIAS)
    images.append(np.array(image))
    product_names.append(row['product_name'])
    manufacturers.append(row['manufacturer'])
    categories.append(row['category'])
    alcohol_contents.append(row['alcohol_content'])

image_tensors = tf.convert_to_tensor(images, dtype=tf.float32)

def categorical_to_tensor(categorical_data, na_value="unknown"):
    filled_data = [value if pd.notna(value) else na_value for value in categorical_data]
    unique_values = np.unique(filled_data)
    value_to_index = {value: index for index, value in enumerate(unique_values)}
    indices = [value_to_index[value] for value in filled_data]
    return tf.convert_to_tensor(indices, dtype=tf.int32), unique_values


product_name_tensor, unique_product_names = categorical_to_tensor(product_names)
manufacturer_tensor, unique_manufacturers = categorical_to_tensor(manufacturers)
category_tensor, unique_categories = categorical_to_tensor(categories)
alcohol_content_tensor = tf.convert_to_tensor(alcohol_contents, dtype=tf.float32)

dataset = tf.data.Dataset.from_tensor_slices((image_tensors, {
    'product_name': product_name_tensor,
    'manufacturer': manufacturer_tensor,
    'category': category_tensor,
    'alcohol_content': alcohol_content_tensor
}))
dataset = dataset.shuffle(buffer_size=len(images)).batch(32).repeat()

def create_multitask_model():
    base_model = models.Sequential([
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.Flatten(),
        layers.Dense(64, activation='relu')
    ])

    product_name_output = layers.Dense(len(unique_product_names), activation='softmax', name='product_name')(base_model.output)
    manufacturer_output = layers.Dense(len(unique_manufacturers), activation='softmax', name='manufacturer')(base_model.output)
    category_output = layers.Dense(len(unique_categories), activation='softmax', name='category')(base_model.output)
    alcohol_content_output = layers.Dense(1, activation='linear', name='alcohol_content')(base_model.output)

    model = models.Model(inputs=base_model.input, outputs=[product_name_output, manufacturer_output, category_output, alcohol_content_output])
    return model

multitask_model = create_multitask_model()

multitask_model.compile(optimizer='adam',
                        loss={
                            'product_name': tf.keras.losses.SparseCategoricalCrossentropy(),
                            'manufacturer': tf.keras.losses.SparseCategoricalCrossentropy(),
                            'category': tf.keras.losses.SparseCategoricalCrossentropy(),
                            'alcohol_content': tf.keras.losses.MeanSquaredError()
                        },
                        metrics={
                            'product_name': 'accuracy',
                            'manufacturer': 'accuracy',
                            'category': 'accuracy',
                            'alcohol_content': 'mse'
                        })

num_epochs = 10
steps_per_epoch = len(images) // 32
multitask_model.fit(dataset, epochs=num_epochs, steps_per_epoch=steps_per_epoch)

multitask_model.save('whisky_multitask_model.h5')