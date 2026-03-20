# AI-First CRM Module (Healthcare Professionals)

This project is an AI-first Customer Relationship Management (CRM) system tailored for Healthcare Professionals (HCPs). It features a natural language conversational interface powered by LangGraph AI agents and Groq LLMs to efficiently log and manage interactions with healthcare providers. The application supports a dual interface, allowing users to enter data through structured forms or a conversational chat interface.

The application is structured into two main parts:
- **Backend:** A Python FastAPI application featuring a PostgreSQL database (via SQLAlchemy) and a LangGraph-powered AI agent.
- **Frontend:** A React application built with Vite, utilizing Redux Toolkit for state management and modern aesthetics (Lucide React for icons).

## Prerequisites

Before you begin, ensure you have the following installed on your machine:
- **Python 3.9+**
- **Node.js (v18+ recommended) and npm**
- **PostgreSQL** (ensure the database service is running locally)
- A **Groq API Key** to interact with the chosen LLM (e.g., gemma2-9b-it)

---

## 🛠️ How to Use the AI Tools

The AI Co-Pilot chat acts as your assistant, parsing your commands into 5 specific LangGraph tool pathways:

1. **Log Interaction**: Start your message with `Met` or `Discussed` (e.g., *"Met Dr. Salt, discussed efficacy of the new trial. Gave 2 samples. Sentiment positive. Follow up tomorrow."*). The AI extracts product names, sentiment, samples, and next steps to auto-fill your log form!
2. **Edit Interaction**: Realize you made a typo? Just say *"Sorry, change sentiment to negative"* or *"Mistake, the doctor was Dr. John."* and the agent will update your most recent interaction.
3. **Show HCP Profile**: Say *"Show profile of Dr. Salt"* to retrieve a formatted history of your previous meetings and follow-ups with that person.
4. **Schedule Follow-Up**: If you forgot to include a follow-up date initially, you can issue a dedicated command like *"Schedule follow up for next Monday"* to add a reminder to an existing interaction.
5. **Find Nearby Hospitals**: Simply ask *"Show nearby hospitals in Chennai"* or *"Find cardiology clinics near me"* to receive a formatted, curated list of recommendations.

---

## 🚀 Execution Guide

Follow these steps to set up and run the application locally.

### 1. Backend Setup

The backend handles API requests, database interactions, and the LangGraph AI module.

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a Python virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - On **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Install backend dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment Variables:**
   - Copy the `.env.example` file to create a `.env` file:
     ```bash
     cp .env.example .env
     ```
   - Open the `.env` file and populate it with your specific database URL and your `GROQ_API_KEY`.

6. **Start the backend server:**
   ```bash
   uvicorn main:app --reload
   ```
   *The backend will be running at `http://127.0.0.1:8000`. You can view the automatically generated API docs at `http://127.0.0.1:8000/docs`.*

---

### 2. Frontend Setup

The frontend provides the user interface for structured logging and the AI chat assistant.

1. **Navigate to the frontend directory:**
   Open a **new terminal window/tab** and from the root project folder, navigate to the frontend:
   ```bash
   cd frontend
   ```

2. **Install frontend dependencies:**
   ```bash
   npm install
   ```

3. **Start the React development server:**
   ```bash
   npm run dev
   ```
   *The frontend will typically run at `http://localhost:5173`. Open this URL in your browser to interact with the application.*

---

## System Architecture

- **PostgreSQL**: Used for persistent storage of HCP information, interactions, and action items.
- **FastAPI Core**: Serves as the primary web framework, exposing endpoints like `/api/chat` for the LangGraph agent.
- **LangGraph Agent**: Configured to process user chat messages, extract relevant interaction context, and form responses.
- **React Frontend**: Provides a dual-column layout (Interaction Form & Chat Panel) for seamless user interaction.

# AI-First CRM HCP Module

This is the frontend for the AI-First Customer Relationship Management (CRM) module tailored for Healthcare Professionals (HCP). 
The core capability of this module is its **AI Co-Pilot Chat Panel**, a powerful LangGraph-driven interface that enables you to instantly log interactions, edit records, retrieve profiles, check hospitals, and schedule follow-ups entirely through natural language.

---

## How to Give Input to the AI Chat 💬

The Chat Panel automatically classifies your intents and auto-fills the structured logging forms on your behalf. Simply type conversational commands or specific key statements directly into the chat input.

Here are the various ways you can interact with the chat:

### 1. Logging a New Interaction
If you just finished a meeting with a doctor and want to log it, start your message with words like **"Met"**, **"Discussed"**, or **"Visited"**.

> **Example Query:**
> `"Met Dr. Salt, discussed efficacy of the new trial. Gave 2 samples. Sentiment is positive. Follow up tomorrow."`

**What happens?** The AI automatically extracts the data into the Form Fields (HCP ID, Topics, Samples, Sentiment, and Next Steps). The `follow up tomorrow` command is instantly parsed into an actual calendar date so you'll receive a notification on that day!

---

### 2. Editing an Existing Record or Correcting Details
If you made a typo or the AI extracted the wrong name, use words like **"Sorry"**, **"Update"**, **"Mistake"**, or **"Change"**.

> **Example Query:**
> `"Sorry, the name was Dr. John."`  
> `"Mistake, the sentiment was actually negative."`

**What happens?** The AI recognizes this as an Edit intent, goes to the most recent interaction in the database, and updates the necessary field seamlessly.

---

### 3. Finding Nearby Hospitals
You can ask the LangGraph system to search and recommend nearby matching hospitals.

> **Example Query:**
> `"Show nearby hospitals in Chennai"`  
> `"Find cardiology hospitals near me"`  
> `"List top 5 hospitals within 10 km"`

**What happens?** The AI bypasses structured logging and directly responds with a neatly formatted numbered list of matching hospitals and clinics.

---

### 4. Retrieving an HCP Profile
If you want to view a history of your interactions with a specific HCP, just say "Show" or "Profile".

> **Example Query:**
> `"Show profile for Dr. Salt"`  
> `"View interaction history with Dr. John"`

**What happens?** The system will fetch and list all previously logged structured records for that Healthcare Professional.

---

### UI Actions (Global State)
- **Send Arrow**: Sends your message to the AI for analysis.
- **Mail Icon (Top Right)**: Provides a quick dropdown of all the follow-ups scheduled specifically for **today**. It updates in real-time when you log interactions.

