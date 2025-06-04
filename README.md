# bee-mite-detector  
# **Real-Time Varroa Detection Using YOLOv8 and Edge AI**

This project implements a **real-time Varroa mite detection system** to assist beekeepers in monitoring honeybee health using computer vision. *Varroa destructor* is one of the leading causes of honeybee colony loss worldwide, and traditional detection methods are invasive, slow, and often unreliable.

The system leverages a **custom-trained YOLOv8n model** to detect Varroa mites on bees as they pass through a camera-monitored hive entrance. It runs entirely on a **Raspberry Pi 5** with a **Hailo-8L AI accelerator**, enabling **offline, low-power, real-time inference** in field conditions.

A lightweight **Flask-based web dashboard** visualises live detection results, tracks infestation metrics, and optionally sends email alerts based on predefined risk thresholds. All detections are logged locally for further analysis.

This solution contributes to **precision beekeeping** by offering a non-invasive, automated, and scalable approach to early Varroa detection.

