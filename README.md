![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

# 🔐 EncryptTool

A lightweight tool that provides secure file encryption, decryption, and media playback capabilities.

## 🚀 Features

### 1. 📁 File Encryption  
Encrypts all files within a specified folder path.

### 2. 🔓 File Decryption  
Decrypts all previously encrypted files within a specified folder path.

### 3. 🖼️ Slideshow  
Displays encrypted images from a specified folder in a slideshow format (switches images every 3 seconds).  
> **Note:** The folder must contain image files only.

### 4. 🎞️ Play Video  
Decrypts a video file, writes it to disk temporarily, and launches it with the system's default media player.  
After playback, the file is **automatically deleted** after a short delay.

Supported media players:
- `Microsoft.Media.Player.exe`
- `vlc.exe`
- `PotPlayerMini64.exe`

---

## ⚠️ Warning!

**Important:** Please save `key.bin` carefully.  
If this file is lost, **any encrypted data will be permanently unrecoverable.**

---

## 🌐 Language Support

You can modify the language in `language.txt` before launching the program.  
The default is `en_US`.

Supported languages:
1. English (`en_US`)
2. 日本語 (`ja_JP`)
3. 简体中文 (`zh_CN`)
4. 繁體中文 (`zh_TW`)

---
## 📦 Installation

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

## 🛠️ Build Executable with PyInstaller
```bash
pyinstaller -F -w your_dir/encrypt_tool.py
```

## 📷 Example
![](example.PNG)
