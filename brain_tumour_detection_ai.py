# -*- coding: utf-8 -*-
"""Brain_Tumour_Detection_AI.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1fGLw-RitIcSjN3mtfS90EDFw4mn6l5mj

# Pre-processing

Gradio and GitHub set up
"""

!pip install gradio

import gradio as gr

!git config --global user.email "manhamalik77@gmail.com"
!git config --global user.name "Manha"

!git config --global credential.helper store
!echo "https://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:@github.com" > ~/.git-credentials

# Commented out IPython magic to ensure Python compatibility.
# Clone the repository
!git clone https://github.com/manhamalik/Brain_Tumour_Detection_AI.git

# Change directory to the repository
# %cd Brain_Tumour_Detection_AI

# Copy the current notebook to the repository directory
!cp /content/Brain_Tumour_Detection_AI.ipynb /content/Brain_Tumour_Detection_AI/

# Change to the repository directory
# %cd /content/Brain_Tumour_Detection_AI

# Add, commit, and push the notebook
!git add Brain_Tumour_Detection_AI.ipynb
!git commit -m "Add initial Brain Tumour Detection AI notebook"
!git push origin main

!pwd

!ls

!ls -a

"""Dataset Setup"""

!pip install kaggle

import shutil
import os

# Path to the directory you want to delete
directory_to_delete = "brain_tumor_mri"

# Delete the directory and its contents
if os.path.exists(directory_to_delete):
    shutil.rmtree(directory_to_delete)
    print(f"Deleted directory: {directory_to_delete}")
else:
    print(f"Directory does not exist: {directory_to_delete}")

!pip uninstall tensorflow

!pip install keras==2.3.1

!pip install tensorflow==2.14.0

!pip install 'h5py==2.10.0'

"""# **Dataset Processing**

## **Mounting Google Drive**
"""

from google.colab import drive
drive.mount('/content/drive')

from google.colab import files
files.upload()

!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

"""## **Imports**"""

import os
import numpy as np
import keras
from keras import layers
from tensorflow import data as tf_data
import matplotlib.pyplot as plt
import tensorflow as tf
from google.colab import files
import shutil
import hashlib

"""## **Load The Data: Brain Tumor MRI Dataset**

### **Raw Data Download**

Downloading and unzipping the dataset to mounted google drive.
"""

!kaggle datasets download -d masoudnickparvar/brain-tumor-mri-dataset

!unzip -q brain-tumor-mri-dataset.zip -d /content/drive/MyDrive/Brain_Tumour_AI/Dataset

"""### **Reorganize the Raw Data**

The original Kaggle Brain Tumor MRI Dataset has predefined folders for training and testing, as well as folders further dividing the MRIs into various types of Tumors. For our purposes, we only wish to determine whether a tumor is present or not, so we must reorganize our data.
"""

#reorganize brain_tumor_mri directory

def file_hash(filepath):
    """Generate MD5 hash for a file."""
    with open(filepath, 'rb') as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()

def merge_and_move_folders(src1, src2, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)

    existing_hashes = set()

    for src in [src1, src2]:
        for root, dirs, files in os.walk(src):
            for file in files:
                src_file = os.path.join(root, file)
                file_md5 = file_hash(src_file)

                if file_md5 in existing_hashes:
                    continue  # Skip this file, as it's a duplicate
                existing_hashes.add(file_md5)

                dst_file = os.path.join(dst, file)

                # If the file exists at the destination, rename the source file
                if os.path.exists(dst_file):
                    base, extension = os.path.splitext(dst_file)
                    i = 1
                    new_dst_file = f"{base}_{i}{extension}"
                    while os.path.exists(new_dst_file):
                        i += 1
                        new_dst_file = f"{base}_{i}{extension}"
                    dst_file = new_dst_file

                shutil.move(src_file, dst_file)

    # Remove the original source directories if they are empty
    if os.path.exists(src1):
        shutil.rmtree(src1)
    if os.path.exists(src2):
        shutil.rmtree(src2)

# Base paths for the Training and Testing folders
train_base_path = '/content/drive/MyDrive/Brain_Tumour_AI/Dataset/Training'
test_base_path = '/content/drive/MyDrive/Brain_Tumour_AI/Dataset/Testing'

# Paths for the combined tumor and notumor folders
combined_tumor_path = '/content/drive/MyDrive/Brain_Tumour_AI/Dataset/tumor'
combined_notumor_path = '/content/drive/MyDrive/Brain_Tumour_AI/Dataset/notumor'

# Create the combined tumor folder if it does not exist
if not os.path.exists(combined_tumor_path):
    os.makedirs(combined_tumor_path)

# List of tumor subfolders to merge
tumor_subfolders = ['glioma', 'meningioma', 'pituitary']

# Merge each tumor subfolder
for subfolder in tumor_subfolders:
    train_folder = os.path.join(train_base_path, subfolder)
    test_folder = os.path.join(test_base_path, subfolder)
    combined_folder = os.path.join(combined_tumor_path, subfolder)
    merge_and_move_folders(train_folder, test_folder, combined_folder)

# Merge notumor folders
train_notumor_folder = os.path.join(train_base_path, 'notumor')
test_notumor_folder = os.path.join(test_base_path, 'notumor')
merge_and_move_folders(train_notumor_folder, test_notumor_folder, combined_notumor_path)

# Remove the Training and Testing folders if they are empty
if os.path.exists(train_base_path):
    shutil.rmtree(train_base_path)
if os.path.exists(test_base_path):
    shutil.rmtree(test_base_path)

print("Folders merged and reorganized successfully!")

"""### **Filter out the Corrupted Images**"""

# Filter out any corrupted images
num_skipped = 0
for folder_name in ("tumor", "notumor"):
        folder_path = os.path.join("/content/drive/MyDrive/Brain_Tumour_AI/Dataset", folder_name)
        if not os.path.isdir(folder_path):
            continue
        for fname in os.listdir(folder_path):
            fpath = os.path.join(folder_path, fname)
            if os.path.isfile(fpath):
                try:
                    with open(fpath, "rb") as fobj:
                        is_jfif = b"JFIF" in fobj.peek(10)
                finally:
                    fobj.close()

                if not is_jfif:
                    num_skipped += 1
                    os.remove(fpath)

print(f"Deleted {num_skipped} images.")

"""## **Generate A Dataset**

Due to the reorganization of data from earlier, we must resplit the data into testing and training.


These datasets will be used in all future training of models.
"""

# Generate a Dataset
image_size = (180, 180)
batch_size = 32

# Define the class names
class_names = ["tumor", "notumor"]

train_ds, val_ds = keras.utils.image_dataset_from_directory(
    "/content/drive/MyDrive/Brain_Tumour_AI/Dataset",
    validation_split=0.2,
    subset="both",
    seed=1337,
    image_size=image_size,
    batch_size=batch_size,
    class_names=class_names,  # Assign class names
    label_mode='int'  # Use integer labels
)

"""### **Visualize the Dataset**"""

# Visualize the training dataset.
plt.figure(figsize=(10, 10))
for images, labels in train_ds.take(1):
    for i in range(9):
        ax = plt.subplot(3, 3, i + 1)
        plt.imshow(np.array(images[i]).astype("uint8"))
        plt.title(class_names[int(labels[i])])
        plt.axis("off")

"""### **Data Augmentation**

Due to the small size of the Brain Tumor MRI dataset, it is important to implement some artificial diversity into the training data.
"""

# Use data augmentation to enhance the training dataset.
data_augmentation_layers = [
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
]

def data_augmentation(images):
    for layer in data_augmentation_layers:
        images = layer(images)
    return images

# Apply data augmentation to the training dataset
train_ds = train_ds.map(
    lambda img, label: (data_augmentation(img), label),
    num_parallel_calls=tf_data.AUTOTUNE,
)
train_ds = train_ds.prefetch(tf_data.AUTOTUNE)
val_ds = val_ds.prefetch(tf_data.AUTOTUNE)

"""# CNN Model

## **Imports**
"""

import tensorflow as tf
# Building the model
from tensorflow import keras
from tensorflow.keras import layers
# Training the model
import os
from tensorflow import keras
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.callbacks import CSVLogger
# Graphing the model
import matplotlib.pyplot as plt
import pandas as pd
# Gradio Implementation
import gradio as gr
import numpy as np
from PIL import Image

"""## **Build the Model**

The Xception network is a deep learning model for image classification that is an extension of the Inception architecture. It stands for "Extreme Inception," and it uses depthwise separable convolutions to improve efficiency and performance. This model is designed to be both powerful and efficient, providing high accuracy on tasks such as image recognition.

We will create a simplified version of the Xception network from scratch. This smaller model will retain the core structure and functionality of the original but will be easier to work with.

The model is built using a series of Convolutional Layers and MaxPooling. A final dropout layer is included before the final classification layer.


"""

# Building a simple CNN
def make_model(input_shape, num_classes):
    inputs = keras.Input(shape=input_shape)

    # Entry block
    x = layers.Rescaling(1.0 / 255)(inputs)
    x = layers.Conv2D(128, 3, strides=2, padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)

    previous_block_activation = x  # Set aside residual

    for size in [256, 512, 728]:
        x = layers.Activation("relu")(x)
        x = layers.SeparableConv2D(size, 3, padding="same")(x)
        x = layers.BatchNormalization()(x)

        x = layers.Activation("relu")(x)
        x = layers.SeparableConv2D(size, 3, padding="same")(x)
        x = layers.BatchNormalization()(x)

        x = layers.MaxPooling2D(3, strides=2, padding="same")(x)

        # Project residual
        residual = layers.Conv2D(size, 1, strides=2, padding="same")(
            previous_block_activation
        )
        x = layers.add([x, residual])  # Add back residual
        previous_block_activation = x  # Set aside next residual

    x = layers.SeparableConv2D(1024, 3, padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)

    x = layers.GlobalAveragePooling2D()(x)
    if num_classes == 2:
        units = 1
    else:
        units = num_classes

    x = layers.Dropout(0.25)(x)
    outputs = layers.Dense(units, activation=None)(x)
    return keras.Model(inputs, outputs)

model = make_model(input_shape=image_size + (3,), num_classes=2)
keras.utils.plot_model(model, show_shapes=True)

"""## **Train the Model**

The model is trained using the MRI Brain tumor set dataset generated earlier. It saves the progress every epoch to the mounted Google drive as well as logs the validation/training accuracy and loss over the epochs.
"""

log_path = "/content/drive/MyDrive/Brain_Tumour_AI/CNN/training_log.csv"
csv_logger = CSVLogger(log_path, append=True)

# Define the checkpoint callback
checkpoint_path = "/content/drive/MyDrive/Brain_Tumour_AI/CNN/training_checkpoints/cp-{epoch:04d}.ckpt"
checkpoint_dir = os.path.dirname(checkpoint_path)

cp_callback = ModelCheckpoint(
    filepath=checkpoint_path,
    save_weights_only=True,
    verbose=1,
    save_freq='epoch'  # Save every epoch
)

# To restart training from the last checkpoint
latest_checkpoint = tf.train.latest_checkpoint(checkpoint_dir)
initial_epoch = 0
if latest_checkpoint:
    print(f"Restoring model from {latest_checkpoint}")
    model.load_weights(latest_checkpoint)
    initial_epoch = int(latest_checkpoint.split('-')[1].split('.')[0])
    print(f"Resuming training from epoch {initial_epoch}")

# Train the model
total_epochs = 15
remaining_epochs = total_epochs - initial_epoch

model.compile(
    optimizer=keras.optimizers.Adam(3e-4),
    loss=keras.losses.BinaryCrossentropy(from_logits=True),
    metrics=[keras.metrics.BinaryAccuracy(name="acc")],
)

history = model.fit(
    train_ds,
    epochs=total_epochs,
    initial_epoch=initial_epoch,
    callbacks=[cp_callback, csv_logger],
    validation_data=val_ds,
)

"""## **Graph the Training of the Model**

Visualization of the training/validation accuracy and loss over the epochs as the model was trained.
"""

log_path = "/content/drive/MyDrive/Brain_Tumour_AI/CNN/training_log.csv"
log_data = pd.read_csv(log_path)

# Extract accuracy and loss from the history object
epochs = log_data['epoch']
acc = log_data['acc']
val_acc = log_data['val_acc']
loss = log_data['loss']
val_loss = log_data['val_loss']

# Plot training & validation accuracy values
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.plot(epochs, acc, 'b', label='Training accuracy')
plt.plot(epochs, val_acc, 'r', label='Validation accuracy')
plt.title('Training and validation accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

# Plot training & validation loss values
plt.subplot(1, 2, 2)
plt.plot(epochs, loss, 'b', label='Training loss')
plt.plot(epochs, val_loss, 'r', label='Validation loss')
plt.title('Training and validation loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()

plt.tight_layout()
plt.show()

"""## **Save the Model**

The model is saved to the mounted google drive in the folder CNN under the name Model.

To call the saved model: model = tf.keras.models.load_model('modeladdress')
"""

model.save('/content/drive/MyDrive/Brain_Tumour_AI/CNN/Model', save_format="h5")

print("Model Saved Successfully")

"""## **Gradio Implementation**"""

# Load your trained Keras model
model = tf.keras.models.load_model('/content/drive/MyDrive/Brain_Tumour_AI/CNN/Model')

# Define the prediction function
def predict_image(image):

    # Convert the image to RGB and resize it to the input shape of the model
    image = Image.fromarray(image).convert("RGB").resize((180, 180))
    img_array = np.array(image)

    img_array = keras.utils.img_to_array(image)
    img_array = keras.backend.expand_dims(img_array, 0)  # Create batch axis

    predictions = model.predict(img_array)
    score = float(keras.backend.sigmoid(predictions[0][0]))
    return(f"The model predicts this image has a {100 * (1 - score):.2f}% probability of containing a tumor and a {100 * score:.2f}% probability of being tumor-free.")

# Create the Gradio interface
gr.Interface(
    fn=predict_image,
    inputs=gr.Image(),
    outputs=gr.Textbox(),
    title="Brain Tumour Classification",
    description="Upload an image to classify whether it indicates the presence of a brain tumour using the CNN Model."
).launch()

"""# Pre-trained Models

Since the dataset of MRI images we are using is relatively small, using a pre-trained model as feature extraction is an effective way of training new models. The representations learned by the pre-trained model are used to extract interesting features from new samples and build a new classifier.

We will be using three different pre-trained models to build three new classifiers. These models are:

*   VGG16
*   InceptionV3
*   ResNet50

VGG16 is a convolutional neural network model known for its simplicity and depth, consisting of 16 layers that excel in image classification tasks by using small convolutional filters.

InceptionV3 is a deep convolutional neural network designed for image classification, known for its efficiency and accuracy due to its use of inception modules, which allow for capturing features at multiple scales.

ResNet50 is a 50-layer deep convolutional neural network that utilizes residual learning, making it highly effective for image recognition tasks by addressing the vanishing gradient problem.

## **Imports**
"""

import os
import numpy as np
# Feature Extraction
from tensorflow.keras.applications import VGG16, InceptionV3, ResNet50
from tensorflow.keras.preprocessing import image_dataset_from_directory
from tensorflow.keras.applications.vgg16 import preprocess_input as vgg16_preprocess_input
from tensorflow.keras.applications.inception_v3 import preprocess_input as inceptionv3_preprocess_input
from tensorflow.keras.applications.resnet50 import preprocess_input as resnet50_preprocess_input
# Training the Classifiers
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras import layers
from tensorflow.keras import optimizers
from tensorflow.keras import models
from tensorflow.keras.callbacks import ModelCheckpoint, CSVLogger
# Graphing the Classifiers
import matplotlib.pyplot as plt
import pandas as pd
# Gradio Implementation
import gradio as gr
import numpy as np
from PIL import Image

"""## **Feature Extraction**

To begin feature extraction, we will be using the same dataset generated for the CNN model. We will then obtain the features and labels from these sets by running the predict method of the pre-trained convolutional base of each model over all of the images.

These features and labels are saved to the appropriate folders in the mounted google drive.
"""

def extract_features(name, sample, dataset, sample_count, feature_shape, base_model, preprocess_input):
    features_path = f"/content/drive/MyDrive/Brain_Tumour_AI/{name}/feature_extraction/{sample}_features.npy"
    labels_path = f"/content/drive/MyDrive/Brain_Tumour_AI/{name}/feature_extraction/{sample}_labels.npy"

    # Check if the features and labels have already been saved
    if os.path.exists(features_path) and os.path.exists(labels_path):
        print(f"Features already done, loading.")
        features = np.load(features_path)
        labels = np.load(labels_path)
        return features, labels

    # Initialize arrays to store features and labels
    features = np.zeros((sample_count, *feature_shape))
    labels = np.zeros((sample_count,))

    i = 0
    for images_batch, labels_batch in dataset:
        features_batch = base_model.predict(images_batch)
        features[i * batch_size : i * batch_size + len(images_batch)] = features_batch[:len(images_batch)]
        labels[i * batch_size : i * batch_size + len(labels_batch)] = labels_batch[:len(labels_batch)]
        i += 1
        if i * batch_size >= sample_count:
            break

    # Save features and labels
    np.save(features_path, features)
    print(f"Successfully saved {name} {sample} features to {features_path}")
    np.save(labels_path, labels)
    print(f"Successfully saved {name} {sample} labels to {labels_path}")

    return features, labels

num_train_samples = len(train_ds) * batch_size
num_val_samples = len(val_ds) * batch_size

# Extract features for each model
#VGG16
vgg16_base = VGG16(weights='imagenet', include_top=False, input_shape=image_size + (3,))
vgg16_base.summary()
print("Starting feature extraction for VGG16")
train_features_vgg16, train_labels_vgg16 = extract_features("VGG16", "train", train_ds, num_train_samples, (5, 5, 512), vgg16_base, vgg16_preprocess_input)
val_features_vgg16, val_labels_vgg16 = extract_features("VGG16", "val", val_ds, num_val_samples, (5, 5, 512), vgg16_base, vgg16_preprocess_input)

#InceptionV3
inceptionv3_base = InceptionV3(weights='imagenet', include_top=False, input_shape=image_size + (3,))
inceptionv3_base.summary()
print("Starting feature extraction for InceptionV3")
train_features_inceptionv3, train_labels_inceptionv3 = extract_features("InceptionV3", "train", train_ds, num_train_samples, (4, 4, 2048), inceptionv3_base, inceptionv3_preprocess_input)
val_features_inceptionv3, val_labels_inceptionv3 = extract_features("InceptionV3", "val", val_ds, num_val_samples, (4, 4, 2048), inceptionv3_base, inceptionv3_preprocess_input)

#ResNet50
resnet50_base = ResNet50(weights='imagenet', include_top=False, input_shape=image_size + (3,))
resnet50_base.summary()
print("Starting feature extraction for ResNet50")
train_features_resnet50, train_labels_resnet50 = extract_features("ResNet50", "train", train_ds, num_train_samples, (6, 6, 2048), resnet50_base, resnet50_preprocess_input)
val_features_resnet50, val_labels_resnet50 = extract_features("ResNet50", "val",val_ds, num_val_samples, (6, 6, 2048), resnet50_base, resnet50_preprocess_input)

"""## **Flattening The Features**

The images must be flattened so that they can be fed to the densely connected classifier of each pre-trained model.
"""

# Flatten the features
train_features_vgg16 = np.reshape(train_features_vgg16, (num_train_samples, 5 * 5 * 512))
val_features_vgg16 = np.reshape(val_features_vgg16, (num_val_samples, 5 * 5 * 512))

train_features_inceptionv3 = np.reshape(train_features_inceptionv3, (num_train_samples, 4 * 4 * 2048))
val_features_inceptionv3 = np.reshape(val_features_inceptionv3, (num_val_samples, 4 * 4 * 2048))

train_features_resnet50 = np.reshape(train_features_resnet50, (num_train_samples, 6 * 6 * 2048))
val_features_resnet50 = np.reshape(val_features_resnet50, (num_val_samples, 6 * 6 * 2048))

"""## **Train Classifiers**

Now the densely connected classifier can be created and trained based on the features extracted from the pre-trained models.

This process saves the progress every epoch to the mounted Google drive as well as logs the validation/training accuracy and loss over the epochs to the appropriate model folders.
"""

from tensorflow.keras.models import Model
from keras import layers
from keras import optimizers
from keras import models
from tensorflow.keras.callbacks import ModelCheckpoint, CSVLogger

def build_classifier(input_dim):
    model = models.Sequential()
    model.add(layers.Dense(256, activation='relu', input_dim=input_dim))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(1, activation='sigmoid'))
    return model

def train_classifier(model, train_features, train_labels, val_features, val_labels, name):
    print(f"\n Training {name} model...")

    log_path = f"/content/drive/MyDrive/Brain_Tumour_AI/{name}/training_log.csv"
    csv_logger = CSVLogger(log_path, append=True)

    checkpoint_path = f"/content/drive/MyDrive/Brain_Tumour_AI/{name}/training_checkpoints/cp-{{epoch:04d}}.ckpt"
    checkpoint_dir = os.path.dirname(checkpoint_path)
    cp_callback = ModelCheckpoint(
        filepath=checkpoint_path,
        save_weights_only=True,
        verbose=1,
        save_freq='epoch'
    )

    # To restart training from the last checkpoint
    latest_checkpoint = tf.train.latest_checkpoint(checkpoint_dir)
    initial_epoch = 0
    if latest_checkpoint:
        print(f"Restoring model from {latest_checkpoint}")
        model.load_weights(latest_checkpoint)
        initial_epoch = int(latest_checkpoint.split('-')[1].split('.')[0])
        print(f"Resuming training from epoch {initial_epoch}")

    model.compile(
        optimizer=optimizers.RMSprop(learning_rate=2e-5),
        loss='binary_crossentropy',
        metrics=['acc']
    )

    history = model.fit(
        train_features, train_labels,
        epochs=25,
        initial_epoch=initial_epoch,
        validation_data=(val_features, val_labels),
        callbacks=[cp_callback, csv_logger]
    )
    return history

# Train classifiers for each feature set
#VGG16
VGG16_savePath = '/content/drive/MyDrive/Brain_Tumour_AI/VGG16/VGG16_classifier'
if not os.path.exists(VGG16_savePath):
    vgg16_classifier = build_classifier(5 * 5 * 512)
    vgg16_classifier.summary()
    history_vgg16 = train_classifier(vgg16_classifier, train_features_vgg16, train_labels_vgg16, val_features_vgg16, val_labels_vgg16, "VGG16")
    vgg16_classifier.save('/content/drive/MyDrive/Brain_Tumour_AI/VGG16/VGG16_classifier', save_format="h5")
    print("VGG16_classifier Saved Successfully")
else:
    print("VGG16_classifier complete, loaded from memory")
    vgg16_classifier = tf.keras.models.load_model(VGG16_savePath)

#InceptionV3
InceptionV3_savePath = '/content/drive/MyDrive/Brain_Tumour_AI/InceptionV3/InceptionV3_classifier'
if not os.path.exists(InceptionV3_savePath):
    inceptionv3_classifier = build_classifier(4 * 4 * 2048)
    history_inceptionv3 = train_classifier(inceptionv3_classifier, train_features_inceptionv3, train_labels_inceptionv3, val_features_inceptionv3, val_labels_inceptionv3, "InceptionV3")
    inceptionv3_classifier.save(InceptionV3_savePath, save_format="h5")
    print("InceptionV3_classifier Saved Successfully")
else:
    print("InceptionV3_classifier complete, loaded from memory")
    inceptionv3_classifier = tf.keras.models.load_model(InceptionV3_savePath)

#ResNet50
ResNet50_savePath = '/content/drive/MyDrive/Brain_Tumour_AI/ResNet50/ResNet50_classifier'
if not os.path.exists(ResNet50_savePath):
    resnet50_classifier = build_classifier(6 * 6 * 2048)
    history_resnet50 = train_classifier(resnet50_classifier, train_features_resnet50, train_labels_resnet50, val_features_resnet50, val_labels_resnet50, "ResNet50")
    resnet50_classifier.save(ResNet50_savePath, save_format="h5")
    print("ResNet50_classifier Saved Successfully")
else:
    print("ResNet50_classifier complete, loaded from memory")
    resnet50_classifier = tf.keras.models.load_model(ResNet50_savePath)

"""## **Graph the Training of each of the Classifiers**

Visualization of the training/validation accuracy and loss over the epochs as the classifiers were trained.
"""

def plot_models(log_path, name):
    log_data = pd.read_csv(log_path)

    # Extract accuracy and loss from the history object
    epochs = log_data['epoch']
    acc = log_data['acc']
    val_acc = log_data['val_acc']
    loss = log_data['loss']
    val_loss = log_data['val_loss']

    # Plot training & validation accuracy values
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.plot(epochs, acc, 'b', label='Training accuracy')
    plt.plot(epochs, val_acc, 'r', label='Validation accuracy')
    plt.title(f'{name} Training and validation accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()

    # Plot training & validation loss values
    plt.subplot(1, 2, 2)
    plt.plot(epochs, loss, 'b', label='Training loss')
    plt.plot(epochs, val_loss, 'r', label='Validation loss')
    plt.title(f'{name} Training and validation loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()

    plt.tight_layout()
    plt.show()

print("Training of VGG16_Classifier")
log_path = "/content/drive/MyDrive/Brain_Tumour_AI/VGG16/training_log.csv"
plot_models(log_path,"VGG16_Classifier")

print("Training of InceptionV3_Classifier")
log_path = "/content/drive/MyDrive/Brain_Tumour_AI/InceptionV3/training_log.csv"
plot_models(log_path, "InceptionV3_Classifier")

print("Training of ResNet50_Classifier")
log_path = "/content/drive/MyDrive/Brain_Tumour_AI/ResNet50/training_log.csv"
plot_models(log_path, "ResNet50_Classifier")

"""## **VGG16 Gradio Implementation**"""

# Load your trained Keras model
model = tf.keras.models.load_model('/content/drive/MyDrive/Brain_Tumour_AI/VGG16/VGG16_classifier')

conv_base = VGG16(weights='imagenet', include_top=False, input_shape=(180, 180) + (3,))

# Define the prediction function
def predict_image(image):
    # Convert Image to RGB and resize it to (180, 180) to match input size
    image = Image.fromarray(image).convert("RGB").resize((180, 180))
    img_array = np.array(image)

    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)

    # Extract features using the convolutional base
    features = conv_base.predict(img_array)

    # Flatten the features
    features_flattened = np.reshape(features, (1, 5 * 5 * 512))

    # Predict with the classifier
    predictions = model.predict(features_flattened)
    score = float(predictions[0][0])

    return f"The model predicts this image has a {100 * (1 - score):.2f}% probability of containing a tumor and a {100 * score:.2f}% probability of being tumor-free."

# Create the Gradio interface
gr.Interface(
    fn=predict_image,
    inputs=gr.Image(),
    outputs=gr.Textbox(),
    title="Brain Tumour Classification",
    description="Upload an image to classify whether it indicates the presence of a brain tumour using VGG16 Feature Extraction."
).launch()

"""## **InceptionV3 Gradio Implementation**"""

# Load your trained Keras model
model = tf.keras.models.load_model('/content/drive/MyDrive/Brain_Tumour_AI/InceptionV3/InceptionV3_classifier')

conv_base = InceptionV3(weights='imagenet', include_top=False, input_shape=(180, 180) + (3,))

# Define the prediction function
def predict_image(image):
    # Convert Image to RGB and resize it to (180, 180) to match input size
    image = Image.fromarray(image).convert("RGB").resize((180, 180))
    img_array = np.array(image)

    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)

    # Extract features using the convolutional base
    features = conv_base.predict(img_array)

    # Flatten the features
    features_flattened = np.reshape(features, (1, 4 * 4 * 2048))

    # Predict with the classifier
    predictions = model.predict(features_flattened)
    score = float(predictions[0][0])

    return f"The model predicts this image has a {100 * (1 - score):.2f}% probability of containing a tumor and a {100 * score:.2f}% probability of being tumor-free."

# Create the Gradio interface
gr.Interface(
    fn=predict_image,
    inputs=gr.Image(),
    outputs=gr.Textbox(),
    title="Brain Tumour Classification",
    description="Upload an image to classify whether it indicates the presence of a brain tumour using InceptionV3 Feature Extraction."
).launch()

"""## **ResNet50 Gradio Implementation**"""

# Load your trained Keras model
model = tf.keras.models.load_model('/content/drive/MyDrive/Brain_Tumour_AI/ResNet50/ResNet50_classifier')

conv_base = ResNet50(weights='imagenet', include_top=False, input_shape=(180, 180) + (3,))

# Define the prediction function
def predict_image(image):
    # Convert Image to RGB and resize it to (180, 180) to match input size
    image = Image.fromarray(image).convert("RGB").resize((180, 180))
    img_array = np.array(image)

    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)

    # Extract features using the convolutional base
    features = conv_base.predict(img_array)

    # Flatten the features
    features_flattened = np.reshape(features, (1, 6 * 6 * 2048))

    # Predict with the classifier
    predictions = model.predict(features_flattened)
    score = float(predictions[0][0])

    return f"The model predicts this image has a {100 * (1 - score):.2f}% probability of containing a tumor and a {100 * score:.2f}% probability of being tumor-free."

# Create the Gradio interface
gr.Interface(
    fn=predict_image,
    inputs=gr.Image(),
    outputs=gr.Textbox(),
    title="Brain Tumour Classification",
    description="Upload an image to classify whether it indicates the presence of a brain tumour using ResNet50 Feature Extraction."
).launch(debug=True)