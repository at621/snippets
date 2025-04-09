**Project:** Single Factor Analysis Agent (Streamlit Application)

**Goal:** Implement a specialized agent as a **modular** Streamlit web application. This agent focuses on macroeconomic data ingestion, preparation, and initial analysis through a conversational interface using a CSV file provided via URL. The application state and conversation flow will be managed directly using **Streamlit session state (`st.session_state`) and the agent's logic**, without a separate orchestrator component. The implementation **must be structured across a maximum of 5 Python files**.

**Core Technologies:**
*   **Language:** Python
*   **LLM/Agent:** OpenAI `gpt-4o` (via the `openai` library)
*   **UI Framework:** Streamlit
*   **Logging:** Loguru (Strictly **no** `print` statements; all output/diagnostics must use Loguru)
*   **Data Handling:** Pandas
*   **HTTP Requests:** `requests` (or similar) for fetching data from URL

**Specific Concise Summary:** Macroeconomic Data Preparation Agent (Streamlit Interface)

**Context:** This agent handles the initial data ingestion and preparation stage for macroeconomic data. It operates as a standalone Streamlit application where users interact conversationally to load, prepare, and analyze data provided via a URL. **State management is handled within the Streamlit session.**

**Primary Objective:** This Streamlit application guides a user interactively through loading (from a CSV URL), cleaning, transforming, and performing initial exploratory analysis on macroeconomic time series data. It ensures data quality and suitability via conversation. **Session state (`st.session_state`) is used to maintain context, data, and conversation history throughout the user's interaction.**

**Key Responsibilities & Specifics:**

1.  **Code Structure & Modularity:**
    *   **Modular Design:** The codebase must be designed with modularity in mind. Separate concerns like UI presentation, agent logic, data handling, and analysis functions into distinct components/modules.
    *   **File Organization:** The entire implementation must be contained within **a maximum of 5 Python files** (e.g., `app.py`, `agent_logic.py`, `data_handler.py`, `analysis_engine.py`, `utils.py` or `config.py`). Clearly define the responsibility of each file.

2.  **Application Interface & State Management (Streamlit - primarily in `app.py`):**
    *   The entire user interaction must occur within a Streamlit application.
    *   Use Streamlit's chat elements (`st.chat_message`, `st.chat_input`) for the conversation.
    *   **Use `st.session_state` extensively** to initialize and manage all application state across reruns within a single user session. This includes:
        *   Conversation history (`messages`).
        *   Loaded data (original and potentially transformed pandas DataFrames).
        *   Data loaded status flag and the source URL/identifier.
        *   Running total token count.
    *   Implement a sidebar (`st.sidebar`) to display:
        *   **Token Count:** The running total token count stored in `st.session_state`.
        *   **Context Data Status:** The data loading status stored in `st.session_state`.
    *   The main `app.py` script will handle the primary interaction loop, render the UI based on `st.session_state`, and trigger agent logic processing.

3.  **Interaction Flow & Conversation Management (handled between `app.py` and `agent_logic.py` using `st.session_state`):**
    *   **Introduction:** Upon starting the Streamlit app or initializing a new session (checked via `st.session_state`), the agent introduces itself.
    *   **File Input via URL:** Prompt the user for the URL of the macroeconomic CSV data file.
    *   **Conversational History:** Store and retrieve the conversation history from `st.session_state` to pass to the LLM for context.
    *   **Natural Language Interaction:** Handle user input via the chat interface.
    *   **Structured Outputs:** Present information clearly in the chat.
    *   **Feedback:** Provide clear success/failure feedback.

4.  **Logging (configured once, used across all files):**
    *   Implement logging using the `loguru` library. Initialize and configure Loguru (e.g., in `app.py` or a dedicated `utils.py/config.py`).
    *   **No `print` statements allowed.**
    *   Import and use the configured logger instance (`from loguru import logger`) in all relevant files.
    *   Log key events: application start/stop, session initialization, user interactions, URL processing, function calls, LLM interactions (including tokens), data operations, errors, state changes.

5.  **Data Ingestion & Validation (likely in `data_handler.py`):**
    *   Define functions to load data from a URL.
    *   Include basic validation.
    *   These functions will be called by the agent logic, and the resulting DataFrame (or error status) will likely be stored in `st.session_state`.

6.  **User-Guided Transformation (function definitions likely in `data_handler.py` or `analysis_engine.py`):**
    *   Define functions for transformations.
    *   These functions will operate on the DataFrame retrieved from `st.session_state` and potentially update the DataFrame stored in `st.session_state`.

7.  **Exploratory Data Analysis (EDA) (function definitions likely in `analysis_engine.py`):**
    *   Define functions for EDA tasks.
    *   These functions will operate on the DataFrame retrieved from `st.session_state` and return results to be displayed.

8.  **Agent Logic & Function Calling (likely in `agent_logic.py`):**
    *   Define the structure for interacting with the OpenAI API (`gpt-4o`).
    *   Access conversation history from `st.session_state`.
    *   Define function schemas for OpenAI function calling.
    *   Process user input, make API calls (passing history from session state), handle function call requests, invoke backend functions (passing data retrieved from session state if needed), process function results, and formulate the LLM's final response.
    *   **Extract token usage** (`response.usage.total_tokens`) from API responses and update the token count in `st.session_state`.
    *   Update `st.session_state` with any relevant changes resulting from agent actions (e.g., updating the stored DataFrame after transformation).

9.  **Error Handling (within relevant functions across files):**
    *   Implement `try...except` blocks.
    *   Log errors thoroughly using `loguru`.
    *   Return appropriate error indicators/messages to the calling logic, which updates the user via the chat interface and logs the details.

**Simplified Core Architectural Elements (Conceptual):**

1.  **`app.py`:** Main Streamlit application script. Handles UI rendering, `st.session_state` initialization and management, main interaction loop, calls `agent_logic`.
2.  **`agent_logic.py`:** Interacts with OpenAI API, manages conversation flow logic (using history from `st.session_state`), handles function calling, updates `st.session_state` (token count, potentially data state flags).
3.  **`data_handler.py`:** Functions for data loading from URL and potentially transformations. Operates on data passed as arguments or retrieved/updated from `st.session_state`.
4.  **`analysis_engine.py`:** Functions for EDA. Operates on data passed as arguments or retrieved from `st.session_state`.
5.  **`utils.py` (or `config.py`):** Optional, for shared utilities, constants, logging setup.

**Output:**
*   A running, **modular** Streamlit application (max 5 Python files) where **state is managed via `st.session_state`**.
*   Interactive chat interface for loading (URL), transforming, and analyzing data.
*   Sidebar showing running token count and data status (both sourced from `st.session_state`).
*   Loguru logs detailing execution.
*   Internal state (data, history) maintained within the Streamlit session.

**Implementation Notes:**
*   Ensure all state persistence relies on `st.session_state`. Check for variable existence in `st.session_state` at the start of `app.py` to handle initialization correctly on first run and persistence across reruns within a session.
*   Adhere strictly to the 5-file limit and modular design.
*   Use environment variables for the OpenAI API key.
