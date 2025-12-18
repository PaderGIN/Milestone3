# 🤖 Axiomus UPM Bot (Milestone 3)

> **Intelligent Question Answering System for Universidad Politécnica de Madrid (UPM).**  
> Incorporating a specialized **Retrieval-Augmented Generation (RAG)** pipeline and a fine-tuned **DistilBERT (SQuAD)** model to deliver high-precision answers.

---

## 🚀 How to Run (Cross-Platform)

### 1. Prerequisites
*   **Docker Desktop** installed and running.
*   **Git** (optional, for cloning).

### 2. Setup Guide

#### Step A: Download the Project
Clone this repository or download the ZIP file.
```bash
git clone <repository_url>
cd Milestone3
```

#### Step B: Model Installation (Critical!)

Due to GitHub file size limits, the fine-tuned model weights (**250MB+**) are not included in the repo.

1.  **Download** your fine-tuned model files (https://drive.google.com/drive/folders/1sz-7Lw-E4SOu1dtgTUxNjvAQ-KejpsrZ?usp=sharing - our model. pls paste unarchived DNN_model package and past in the project in the same named package.).
2.  **Extract** them into: `ML-Service-API/DNN_Model/`
3.  Ensure the folder contains: `config.json`, `model.safetensors`, `tokenizer.json`, etc.

#### Step C: Configure Token

Open `docker-compose.yml` and paste your Telegram Bot Token (from @BotFather):

```yaml
environment:
  - TELEGRAM_TOKEN=your_token_here
```

---

### 3. Launch Commands

Choose your operating system below to start the bot.

#### 🍎 macOS / 🐧 Linux (Terminal)

Run the following command in the root folder (where `docker-compose.yml` is):

```bash
# Build and start containers in detached mode
docker compose up --build -d

# To view logs (optional)
docker compose logs -f
```

#### 🪟 Windows (PowerShell / CMD)

Ensure Docker Desktop is running in the background.

```powershell
# Build and start
docker compose up --build -d
```

*Note for Windows users: If you see an error about "image not found" or "no such file", ensure you are in the correct directory using `ls` or `dir`.*

---

## 📸 Demo

To test the bot, send these commands:

1.  `/start` - Initialize the session.
2.  `When was UPM founded?` (Expect: "1971")
3.  `What is the minimum passing grade?` (Expect: "5")

---

**University:** Universidad Politécnica de Madrid (UPM)  
**Subject:** Deep Learning & Software Engineering