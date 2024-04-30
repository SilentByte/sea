#!/usr/bin/env bash

# SEA DataBricks Cluster Initialization Script.

sudo rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*
sudo apt-get purge
sudo apt-get clean
sudo apt-get update
sudo apt-get install -y \
  poppler-utils \
  tesseract-ocr
