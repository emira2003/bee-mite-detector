# bee-mite-detector  

**Real-Time Varroa Detection Using YOLOv8 and Edge AI**

This project implements a **real-time Varroa mite detection system** to assist beekeepers in monitoring honeybee health using computer vision. *Varroa destructor* is one of the leading causes of honeybee colony loss worldwide, and traditional detection methods are invasive, slow, and often unreliable.

The system leverages a **custom-trained YOLOv8n model** to detect Varroa mites on bees as they pass through a camera-monitored hive entrance. It runs entirely on a **Raspberry Pi 5** with a **Hailo-8L AI accelerator**, enabling **offline, low-power, real-time inference** in field conditions.

A lightweight **Flask-based web dashboard** visualises live detection results, tracks infestation metrics, and optionally sends email alerts based on predefined risk thresholds. All detections are logged locally for further analysis.

This solution contributes to **precision beekeeping** by offering a non-invasive, automated, and scalable approach to early Varroa detection.


## Features

- **Real-time detection of Varroa mites** using a custom-trained YOLOv8n model
- **Camera-based hive monitoring** with automatic object detection on live video
- **Runs entirely on Raspberry Pi 5 + Hailo-8L**, enabling efficient edge AI deployment
- **Web-based dashboard** for live visualisation, metrics display, and session summaries
- **Local data logging** of infestation ratios and detection statistics using SQLite
- **Visual risk classification** based on infestation thresholds (low, moderate, high, critical)
- **Email alert system** (optional) when critical infestation levels are detected
- **Tested and validated** with unit, integration, and performance testing


