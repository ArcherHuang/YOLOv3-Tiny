# Using YOLOv3-Tiny on Xilinx Kria KV260 Vision AI Starter Kit
## Contents
- [Folders & Files in this Repository](#folders--files-in-this-repository)
- [Convert Darknet to Tensorflow ( Colab or Azure Machine Learning )](#convert-darknet-to-tensorflow--colab-or-azure-machine-learning-)
- [Create Azure Ubuntu 22.04 VM and Upload Files](#create-azure-ubuntu-2204-vm--upload-files)
- [Logging in to Azure Ubuntu 22.04 VM](#logging-in-to-azure-ubuntu-2204-vm)
- [Install Docker Engine on Azure Ubuntu 22.04 VM](#install-docker-engine-on-azure-ubuntu-2204-vm)
- [Download xilinx/vitis-ai Docker Image on Azure Ubuntu 22.04 VM](#download-xilinxvitis-ai-docker-image-on-azure-ubuntu-2204-vm)
- [Run xilinx/vitis-ai Docker Image on Azure Ubuntu 22.04 VM](#run-xilinxvitis-ai-docker-image-on-azure-ubuntu-2204-vm)
- [Copy Files to vitis-ai:1.4.916 Container](#copy-files-to-vitis-ai14916-container)
- [Build a frozen graph](#build-a-frozen-graph)
- [Quantization](#quantization)
- [Customizing Smart Camera Application](#customizing-smart-camera-application)
- [SCP Files to KV260](#scp-files-to-kv260)
- [Run Test](#run-test)
- [License](#license)

## Folders & Files in this Repository
```
├── Config
│   ├── aiinference.json
│   ├── arch.json
│   ├── drawresult.json
│   ├── label.json
│   ├── preprocess.json
│   └── yolov3tiny.prototxt
├── LICENSE
├── Python
│   └── calibration.py
├── README.md
├── Script
│   └── gst-yolov3-tiny.sh
└── pre-trained-model
    └── yolov3-tiny.conv.11
```

## Convert Darknet to Tensorflow ( Colab or Azure Machine Learning )
* Training & Conversion Process
* After the conversion process, we get .pb and .ckpt files ( data.zip ).
  * data.zip 
    * checkpoint
    * yolov3-tiny.cfg
    * yolov3-tiny.ckpt.data-00000-of-00001
    * yolov3-tiny.ckpt.index
    * yolov3-tiny.ckpt.meta
    * yolov3-tiny.pb
    * yolov3-tiny.weights
* Download data.zip to Local

## Create Azure Ubuntu 22.04 VM & Upload Files
* Azure Portal
  * https://portal.azure.com/
* Upload data.zip from Local to Azure VM
  * sudo scp ./data.zip ACCOUNT@VM-IP:~
* Upload Datasets .zip from Local to Azure VM
  * sudo scp ./Datasets.zip ACCOUNT@VM-IP:~

## Logging in to Azure Ubuntu 22.04 VM
* on Terminal 1 & Terminal 2
  * ssh ACCOUNT@VM-IP

## Install Docker Engine on Azure Ubuntu 22.04 VM
* Download Script
```
wget https://raw.githubusercontent.com/ArcherHuang/Docker-Python-Flask/main/Script/install-docker.sh
```

* Change Mode
```
chmod 777 install-docker.sh
```

* Install
```
sudo ./install-docker.sh
```

## Download xilinx/vitis-ai Docker Image on Azure Ubuntu 22.04 VM
```
sudo docker pull xilinx/vitis-ai:1.4.916

sudo docker images
```

## Run xilinx/vitis-ai Docker Image on Azure Ubuntu 22.04 VM
* on Terminal 1
```
git clone https://github.com/Xilinx/Vitis-AI.git

cd Vitis-AI

sudo ./docker_run.sh xilinx/vitis-ai:1.4.916

conda activate vitis-ai-tensorflow
```

## Copy Files to vitis-ai:1.4.916 Container
* on Terminal 2
```
sudo apt install unzip

cd ~

unzip data.zip

unzip Datasets.zip

sudo docker ps -a

sudo docker cp ./data CONTAINER-ID:/

sudo docker cp ./Datasets CONTAINER-ID:/
```

## Build a frozen graph
* Visualizer for neural network
  * https://netron.app/
* Create a directory and name it freez_graph
  * on Container 
    ```
    cd /data

    mkdir freez_graph

    freeze_graph \
    --input_graph yolov3-tiny.pb \
    --input_checkpoint yolov3-tiny.ckpt \
    --output_graph freez_graph/frozen_graph.pb \
    --output_node_names yolov3-tiny/convolutional10/BiasAdd \
    --input_binary true


    The output file will be frozen_graph.pb
    /data/freez_graph/frozen_graph.pb
    ```

# Quantization
* Create [calibration.py](https://github.com/ArcherHuang/YOLOv3-Tiny/blob/main/Python/calibration.py)
  * on Container 
    ```
    cd ~

    vi calibration.py
    ```

* To quantize the model
  * on Container 
    ```
    vai_q_tensorflow quantize \
    --input_frozen_graph /data/freez_graph/frozen_graph.pb \
    --input_fn calibration.calib_input \
    --output_dir quantization/ \
    --input_nodes yolov3-tiny/net1 \
    --output_nodes yolov3-tiny/convolutional10/BiasAdd \
    --input_shapes ?,416,416,3 \
    --calib_iter 1


    The output file will be quantize_eval_model.pb
    /home/vitis-ai-user/quantization/quantize_eval_model.pb
    ```

* Create [arch.json](https://github.com/ArcherHuang/YOLOv3-Tiny/blob/main/Config/arch.json)
  * on Container 
    ```
    cd ~

    vi arch.json

    {
        "fingerprint":"0x1000020F6014406"
    }
    ```

* Compile model
  * on Container 
    ```
    cd ~

    vai_c_tensorflow \
    --frozen_pb quantization/quantize_eval_model.pb \
    -a arch.json \
    -o yolov3tiny \
    -n yolov3tiny


    The output file will be 
    /home/vitis-ai-user/yolov3tiny/md5sum.txt
    /home/vitis-ai-user/yolov3tiny/meta.json
    /home/vitis-ai-user/yolov3tiny/yolov3tiny.xmodel
    ```

* Copy yolov3tiny Folder to VM (/home/ACCOUNT/yolov3tiny)
  * on VM
    ```
    sudo docker ps -a

    sudo docker cp CONTAINER-ID:/home/vitis-ai-user/yolov3tiny /home/`whoami`
    ```

## Customizing Smart Camera Application
* [yolov3tiny.prototxt](https://github.com/ArcherHuang/YOLOv3-Tiny/blob/main/Config/yolov3tiny.prototxt)
* [preprocess.json](https://github.com/ArcherHuang/YOLOv3-Tiny/blob/main/Config/preprocess.json)
* [aiinference.json](https://github.com/ArcherHuang/YOLOv3-Tiny/blob/main/Config/aiinference.json)
* [label.json](https://github.com/ArcherHuang/YOLOv3-Tiny/blob/main/Config/label.json)
* [drawresult.json](https://github.com/ArcherHuang/YOLOv3-Tiny/blob/main/Config/drawresult.json)

## SCP Files to KV260
* yolov3tiny.xmodel & [yolov3tiny.prototxt](https://github.com/ArcherHuang/YOLOv3-Tiny/blob/main/Config/yolov3tiny.prototxt) & [label.json](https://github.com/ArcherHuang/YOLOv3-Tiny/blob/main/Config/label.json)
  * on Xilinx Kria KV260 Vision AI Starter Kit
    ```
    sudo chmod 777 /opt/xilinx/share/vitis_ai_library/models/kv260-smartcam

    cd /opt/xilinx/share/vitis_ai_library/models/kv260-smartcam

    mkdir yolov3tiny
    ```

  * macOS or Ubuntu
    ```
    scp yolov3tiny.xmodel petalinux@169.254.158.168:/home/petalinux/yolov3tiny

    scp yolov3tiny.prototxt petalinux@169.254.158.168:/home/petalinux/yolov3tiny

    scp label.json petalinux@169.254.158.168:/home/petalinux/yolov3tiny
    ```

* [preprocess.json](https://github.com/ArcherHuang/YOLOv3-Tiny/blob/main/Config/preprocess.json) & [drawresult.json](https://github.com/ArcherHuang/YOLOv3-Tiny/blob/main/Config/drawresult.json) & [aiinference.json](https://github.com/ArcherHuang/YOLOv3-Tiny/blob/main/Config/aiinference.json)
  * on Xilinx Kria KV260 Vision AI Starter Kit
    ```
    sudo chmod 777 /opt/xilinx/share/ivas/smartcam
  
    cd /opt/xilinx/share/ivas/smartcam
  
    mkdir yolov3tiny
  
    cd yolov3tiny
    ```
  * macOS or Ubuntu
    ```
    scp preprocess.json petalinux@169.254.158.168:/opt/xilinx/share/ivas/smartcam/yolov3tiny

    scp drawresult.json petalinux@169.254.158.168:/opt/xilinx/share/ivas/smartcam/yolov3tiny

    scp aiinference.json petalinux@169.254.158.168:/opt/xilinx/share/ivas/smartcam/yolov3tiny
    ```
## Run Test
* on Xilinx Kria KV260 Vision AI Starter Kit
  * Load App
    ```
    sudo xmutil unloadapp

    sudo xmutil listapps

    sudo xmutil loadapp kv260-smartcam
    ```
  * gst-yolov3-tiny.sh
    ```
    cd ~

    Ref https://github.com/ArcherHuang/YOLOv3-Tiny/blob/main/Script/gst-yolov3-tiny.sh
    ```
  * Change Mode
    ```
    chmod 777 gst-yolov3-tiny.sh
    ```
  * Run Script
    ```
    sh gst-yolov3-tiny.sh
    ```

## License
This sample is licensed under the [MIT](./LICENSE) license.