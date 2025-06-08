# Varroa Detection Using Deep Learning: An Embedded Real-Time Detection System for Beekeeping

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Latest-green.svg)](https://github.com/ultralytics/ultralytics)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)]()

*Final Year Project - University of Greenwich*


## Project Overview

This project addresses the ongoing threat posed by *Varroa destructor* mites to honeybee populations by introducing a non-invasive, real-time detection system using deep learning. Traditional monitoring methods are labour-intensive, inconsistent, and delayed in response, leading to late-stage infestations and colony decline.

The proposed solution integrates a YOLOv8-based object detection model with edge AI hardware, allowing real-time processing on low-power devices in remote field environments. The system enables continuous monitoring without disrupting hive activity and provides automated alerts when infestation thresholds are exceeded.

The detection model was trained on a dataset of over 15,000 annotated images and achieves an mAP@0.5 of 89.8% on unseen test data. It is deployed on a Raspberry Pi 5 coupled with the Hailo-8L accelerator for efficient inference, with a web-based dashboard built using Flask for live visualisation and local data logging.

This approach contributes to precision beekeeping by enabling early intervention through embedded vision, enhancing colony management without the need for manual inspection.

### System Overview Animation 

![System Overview Animation](docs/images/systemoverview.png)

## Visual Demo

The following screenshots demonstrate live detection of Varroa mites within the real-time web interface. The dashboard serves as the primary user interface for monitoring colony health in real time. It provides a clear and accessible overview of key metrics derived from the detection system, supporting informed decision-making in the field. Designed with responsiveness and simplicity in mind, the interface presents detection outcomes, health indicators and system status updates in an intuitive layout.

> *Note: For best results, use a webcam or hive tunnel camera positioned at the hive entrance under stable lighting conditions.*

### Sample Detection Interface

![Detection Example](docs/images/detection_example.png)

### Real-time dynamic dashboard

![Real-time dynamic dashboard](docs/images/dashboard.png)


### Risk Classification Logic

| Risk Level | Infestation Ratio |
|------------|-------------------|
| Low        | < 5%              | 
| Moderate   | 5–10%              |
| High       | 10–15%             |
| Critical   | > 15%             |


### Summary of Key Evaluation Metrics

| Model   | Precision | Recall | F1-Score | mAP\@0.5 |
| ------- | --------- | ------ | -------- | -------- |
| YOLOv8n | 0.861     | 0.842  | 0.84     | 0.898    |


## Technology Stack

### Core Technologies
- **YOLOv8n (Ultralytics)**: Object detection model architecture
- **PyTorch**: Framework used for training and inference
- **OpenCV**: Image and video processing
- **Flask**: Backend web server for dashboard and visualisation
- **SQLite**: Lightweight local database for detection logs

### Deployment
- **Hailo-8L AI Accelerator**: Hardware-accelerated inference using compiled `.hef` model
- **Raspberry Pi 5**: Edge device running the full system (inference + dashboard)
- **Hailo Dataflow Compiler**: Used to convert ONNX model to `.hef` format

### Development Tools
- **Python 3.8+**
- **Ultralytics CLI**: For training and exporting YOLOv8 models
- **Git** and **GitHub**: Version control and project hosting
- **VNC / SSH**: Remote access during testing and deployment









