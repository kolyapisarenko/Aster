# Aster: Personal Productivity Ecosystem

**Aster** is a modular digital ecosystem designed to streamline daily routines and personal finance management. The project aims to consolidate various utility tools into a single, private, and self-hosted environment.

Named after the Latin word for "star," Aster serves as a central point for organizing data and automating repetitive tasks. This project is my primary environment for experimenting with modern software architecture and containerization.

---

## Current Modules (Phase 1: MVP)

Aster currently consists of three core modules:

* **Savings Tracker (Piggy Bank):** A financial tool to monitor savings, calculate passive income based on APY, and visualize progress via activity calendars.
* **Utility Calculator:** A simplified interface for calculating domestic utility costs (electricity, water, etc.) based on custom consumption rates.
* **Habit Tracker:** A system for monitoring daily activities and maintaining consistency in long-term goals.

---

## Technical Stack

The ecosystem is built using a "container-first" approach to ensure environment parity and ease of deployment:

* **Language:** Python 3.10+
* **Web Interface:** Streamlit
* **Telegram Interface:** Aiogram 3.x
* **Database:** SQLite
* **Infrastructure:** Docker & Docker Compose

---

## Getting Started

Aster is fully containerized. You can deploy the entire stack without manually installing Python dependencies on your host machine.

### Prerequisites

* **Docker & Docker Compose**
* **Git** (to clone the repository)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/kolyapisarenko/Aster](https://github.com/kolyapisarenko/Aster)
    cd aster
    ```

2.  **Configure Environment Variables:**
    Create a `.env` file in the root directory and provide your Telegram Bot token:
    ```env
    TELEGRAM_BOT_TOKEN=your_bot_father_token
    DB_PATH=data/aster_database.db
    ```

3.  **Deploy with Docker:**
    ```bash
    docker-compose up --build -d
    ```

Once the containers are running, the Web UI will be accessible at `http://localhost:8501`, and the Telegram bot will be active.

---

## Build in Public

I am developing Aster as part of a "build in public" initiative, documenting the technical challenges and architectural decisions. You can follow the development progress and updates here:

**[X (Twitter) Profile](https://x.com/NicholaDevua)**

---

*Developed with a focus on clean code and self-hosted infrastructure.*