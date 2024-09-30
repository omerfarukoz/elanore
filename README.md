--- English

# Elanore

### Web Client for Ollama - Llama LLM

**Elanore** is a web client built to interact with the **Ollama - Llama Large Language Model** (LLM). It uses a combination of Python (Flask framework), HTML, CSS, and JavaScript to deliver a simple but effective interface for real-time LLM queries.

## Features
- Flask-based backend.
- Frontend designed with HTML and JavaScript for responsiveness.
- Real-time LLM query handling and response rendering.
- Error handling and user feedback mechanisms.

## Key Components
1. **main.py**: This file contains the core Flask application, handling HTTP routes, and interaction with the Llama LLM.
2. **templates/**: Contains HTML files for the frontend, defining the structure of the user interface.
3. **static/**: This folder holds CSS and JavaScript files that style the interface and manage real-time interactions.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/omerfarukoz/elanore
   ```
2. Install required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Flask server:
   ```bash
   python main.py
   ```

## How it Works
- Users interact with the web client via a simple form.
- The client sends requests to the Flask server, which communicates with the Ollama Llama API.
- Real-time results are displayed on the frontend.

--- Turkish

# Elanore

### Ollama - Llama LLM için Web İstemcisi

**Elanore**, **Ollama - Llama Büyük Dil Modeli** ile etkileşim sağlayan bir web istemcisidir. Python (Flask), HTML, CSS ve JavaScript kullanılarak oluşturulmuştur ve gerçek zamanlı LLM sorguları için basit ve etkili bir arayüz sunar.

## Özellikler
- Flask tabanlı backend.
- HTML ve JavaScript ile duyarlı arayüz.
- Gerçek zamanlı LLM sorgulama ve yanıt gösterimi.
- Hata yönetimi ve kullanıcı geri bildirimi.

## Temel Bileşenler
1. **main.py**: HTTP rotalarını ve Llama LLM ile etkileşimleri yöneten ana Flask uygulamasını içerir.
2. **templates/**: Kullanıcı arayüzünün yapısını tanımlayan HTML dosyalarını barındırır.
3. **static/**: Arayüzü stillendiren ve gerçek zamanlı etkileşimleri yöneten CSS ve JavaScript dosyalarını içerir.

## Kurulum

1. Depoyu klonlayın:
   ```bash
   git clone https://github.com/omerfarukoz/elanore
   ```
2. Gerekli Python bağımlılıklarını yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
3. Flask sunucusunu başlatın:
   ```bash
   python main.py
   ```

## Nasıl Çalışır?
- Kullanıcılar basit bir form aracılığıyla web istemcisiyle etkileşim kurar.
- İstemci, Flask sunucusuna istek gönderir ve Ollama Llama API ile iletişim kurar.
- Gerçek zamanlı sonuçlar ön yüzde görüntülenir