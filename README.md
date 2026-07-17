# 📖 Hikma Project

An integrated application containing a **Discord Bot** and a **Telegram Bot** designed to retrieve and display Arabic poetry. The project connects asynchronously to the **Kather API** to fetch lines, poems, and poets, with full support for advanced filtering and autocomplete features.

---

## ✨ Features

- **Fetch Poetry Lines:** Retrieve random or specific poetic lines filtered by era, country, topic, quafia, sea, and poem type.
- **Complete Poems:** Search for and display full poems along with their metadata.
- **Poet Profiles:** View poet information and search the catalog of poets.
- **Autocomplete Support:** Interactive autocomplete options for eras, countries, seas, quafias, and poets directly within chat prompts.

---

## 📁 Project Structure

This is a monorepo containing two main parts:

- **`discord/`**: The Discord bot written in **JavaScript (Node.js)**.
- **`telegram/`**: The Telegram bot written in **Python**.

---

## 🚀 Setup and Installation

### 1️⃣ Environment Variables (`.env`)

Before running either application, create a `.env` file in the root of each bot's folder using the provided `.env.example` templates, and fill in your respective API keys and bot tokens.

---

### 2️⃣ Running the Discord Bot (Node.js)

The Discord bot runs on Node.js.

```bash
# Navigate to the discord folder
cd discord

# Install dependencies
npm install

# Start the bot
npm start
```

---

### 3️⃣ Running the Telegram Bot (Python)

The Telegram bot relies on Python 3 and uses `httpx` for fast, asynchronous API communication.

```bash
# Navigate to the telegram folder
cd telegram

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt

# Run the bot
python main.py
```

---

## 🛠️ Technologies Used

- **Python 3** — Handles the Telegram bot client asynchronously using `httpx`.
- **Node.js** — Powers the Discord bot with full API integrations.
- **Kather API** — The core data source for all Arabic poetry metadata.