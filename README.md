# Brain Tumour Detection AI Project

This project utilizes pre-trained deep convolutional neural network models to detect brain tumours in MRI images. The models used are VGG16, InceptionV3, and ResNet50, implemented using TensorFlow and Keras, and hosted on Google Colaboratory.

## Steps to Download, Configure, Train, and Test Pre-trained Models

### 1. Setup Environment

**Google Colab and Gradio**
- Open Google Colaboratory: [Google Colaboratory](https://colab.research.google.com/)
- Install Gradio:
  ```python
  !pip install gradio
  ```

**Kaggle Dataset Setup**
- Install Kaggle API and download the dataset:
  ```python
  !pip install kaggle
  from google.colab import files
  files.upload()
  !mkdir -p ~/.kaggle
  !cp kaggle.json ~/.kaggle/
  !chmod 600 ~/.kaggle/kaggle.json
  !kaggle datasets download -d masoudnickparvar/brain-tumor-mri-dataset
  !unzip -q brain-tumor-mri-dataset.zip -d /content/drive/MyDrive/Brain_Tumour_AI/Dataset
  ```

### 2. Data Preprocessing

**Reorganize Data**
- Merge training and testing data into tumour and notumour folders.

**Filter Corrupted Images**
- Remove corrupted images.

**Generate and Augment Dataset**
- Create training and validation datasets, and apply data augmentation.

### 3. Feature Extraction and Training

**Feature Extraction with Pre-trained Models**
- Extract features using VGG16, InceptionV3, and ResNet50.

**Flatten Features and Train Classifiers**
- Flatten the features and train classifiers.

### 4. Testing with Gradio

**Gradio Implementation**
- Create Gradio interfaces for testing VGG16, InceptionV3, and ResNet50 models.

## Deliverables
- iPython notebook showing the implementation
- Video showing model outputs

For detailed code, refer to the provided [Jupyter notebook](https://github.com/manhamalik/Brain_Tumour_Detection_AI).

