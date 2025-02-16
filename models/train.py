import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models  # Import models và layers đúng cách
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Tăng cường dữ liệu
datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

# Load dữ liệu
train_gen = datagen.flow_from_directory("dataset/", target_size=(160, 160), batch_size=16, subset="training")
val_gen = datagen.flow_from_directory("dataset/", target_size=(160, 160), batch_size=16, subset="validation")

# Xây dựng mô hình CNN từ đầu
model = models.Sequential([
    layers.Conv2D(32, (3, 3), activation="relu", input_shape=(160, 160, 3)),
    layers.MaxPooling2D((2, 2)),

    layers.Conv2D(64, (3, 3), activation="relu"),
    layers.MaxPooling2D((2, 2)),

    layers.Conv2D(128, (3, 3), activation="relu"),
    layers.MaxPooling2D((2, 2)),

    layers.Flatten(),
    layers.Dense(128, activation="relu"),
    layers.Dropout(0.5),
    layers.Dense(len(train_gen.class_indices), activation="softmax")
])

# Compile mô hình
model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

# Train mô hình
model.fit(train_gen, validation_data=val_gen, epochs=15)

# Lưu mô hình
model.save("models/cnn_model.keras")
print("✅ Mô hình CNN đã lưu thành công!")
