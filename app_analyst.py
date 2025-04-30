import contextlib
import io
import sys
from typing import Any, Dict, List, TypedDict
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import streamlit as st
from loguru import logger
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import Tool
from langgraph.graph import StateGraph, END

matplotlib.use("Agg")  # Use non-interactive backend
# ---------------------------------------------------------------------------
# Logging (Loguru) - Keeping DEBUG for console during development
# ---------------------------------------------------------------------------
logger.remove()

logger.add(
    sys.stderr,
    level="DEBUG",  # Set to DEBUG to see detailed logs in console
    colorize=True,
    format="{time:HH:mm:ss} | {level:<8} | {message}",
)
logger.debug("Logging initialised – bootstrap")

# ---------------------------------------------------------------------------
# Streamlit UI - Sidebar File Upload and Token Count
# ---------------------------------------------------------------------------

st.set_page_config(page_title="DataFrame QA with LangGraph", layout="wide")

PAGE_STYLES = """
<style>
       .block-container {
            padding-top: 2rem;
            padding-bottom: 0rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }
        div[class^='st-emotion-cache-a6qe2i e1dbuyne7'] {
            padding-top: 1rem;
        }
        div[class^='st-emotion-cache-kgpedg e1dbuyne10'] {
                padding-top: 1rem;
                height: 0px;
        }

        div[class^='st-emotion-cache-149h0zs eiemyj1'] {
                padding-top: 0rem;
                height: 0px;
        }

        .stAppDeployButton {
            visibility: hidden;
        }

        div[class^='st-emotion-cache-kgpedg e19011e610'] {
                padding-top: 2rem;
                height: 0px;
        }       

        [data-testid="stChatMessage"] {
            padding: 0px !important;
            margin-bottom: 0px !important;
        }

        [data-testid="stChatMessageContent"] {
            padding: -1px !important;
        }

        }
</style>
"""
st.markdown(PAGE_STYLES, unsafe_allow_html=True)

# Session‑wide token / cost counters (persist across reruns)
if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0
if "total_cost" not in st.session_state:
    st.session_state.total_cost = 0.0

# Constant pricing for gpt‑4o‑mini (USD)
_INPUT_COST_PER_TOKEN = 1.0 / 1_000_000  # $1.0 / 1M input tokens
_OUTPUT_COST_PER_TOKEN = 10.0 / 1_000_000  # $10.0 / 1M output tokens


# --- File Upload Section in Sidebar ---
with st.sidebar:
    # Display real token count in the sidebar (just a placeholder approach)
    st.sidebar.markdown("### :blue[Analysis State]")
    token_count = 10
    st.sidebar.markdown(f"Total token count: :red[{st.session_state.total_tokens:,.0f}]")
    st.sidebar.markdown(
        f"Approximate cost in USD: :red[{st.session_state.total_cost:,.4f}]"
    )

    # st.divider()
    st.sidebar.markdown("### :blue[Upload a file]")

    uploaded_file = st.file_uploader(
        "Upload a CSV or Excel file", type=["csv", "xlsx"], label_visibility="collapsed"
    )

    # Show file name once uploaded
    if uploaded_file is not None:
        st.session_state.uploaded_file_name = uploaded_file.name
        logger.info(f"File uploaded: {uploaded_file.name}")

        # Read the file into a DataFrame based on its type
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)

        logger.info(f"Loaded DataFrame with {len(df)} rows")
    else:
        df = None  # If no file is uploaded, set df to None


st.markdown("#### Analytics agent")

# ---------------------------------------------------------------------------
# Tool: python_pandas_executor
# ---------------------------------------------------------------------------

# Add a session state variable to track if we're rendering a plot
if "rendering_plot" not in st.session_state:
    st.session_state.rendering_plot = False


def python_pandas_executor(code: str) -> str:
    """Execute *trusted* Python that can access `df`, `pd`, `plt`, and `st`."""
    logger.debug(f"Executor received code:\n{code}")
    # Clear any existing figures to prevent interference
    plt.close("all")

    allowed_globals: Dict[str, Any] = {
        "df": df,
        "pd": pd,
        "plt": plt,  # Add matplotlib.pyplot
        "np": np,  # Often needed for data analysis
        "st": st,  # Add streamlit for plotting
        "io": io,  # Added for BytesIO
        "__builtins__": __builtins__,
    }
    local_vars: Dict[str, Any] = {}
    stdout_buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout_buffer):
            exec(compile(code, "<agent-code>", "exec"), allowed_globals, local_vars)
        stdout_val = stdout_buffer.getvalue()
        last_val = local_vars.get("result")

        # Special handling for plot results
        if isinstance(last_val, dict) and last_val.get("type") == "plot":
            # Generate a unique ID for this plot
            import uuid

            plot_id = str(uuid.uuid4())
            # Store the plot data in session state
            st.session_state.plots[plot_id] = last_val["data"]
            # Return a reference to the plot that can be used to display it later
            return f"PLOT:{plot_id}"

        outs: List[str] = []
        if stdout_val:
            outs.append(stdout_val.strip())
        if last_val is not None:
            outs.append(str(last_val))
        payload = "\n".join(outs) if outs else "<no output>"
        logger.debug(f"Executor success – payload {payload[:60]}…")
        return payload
    except Exception as exc:
        logger.exception(f"Executor raised: {exc}")
        return f"ERROR: {type(exc).__name__}: {exc}"


python_executor_tool = Tool(
    name="python_pandas_executor",
    description=(
        "Executes Python against the DataFrame `df` and returns stdout or the "
        "variable `result`. Always reference the DataFrame as `df`. "
        "For plots, save the figure to a bytes buffer and return it as "
        "{'type': 'plot', 'data': buffer} instead of using st.pyplot()."
    ),
    func=python_pandas_executor,
    infer_schema=True,
)
TOOLS_RUNTIME: Dict[str, Any] = {python_executor_tool.name: python_pandas_executor}

# ---------------------------------------------------------------------------
# LLM with bound tools
# ---------------------------------------------------------------------------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=False).bind_tools(
    [python_executor_tool]
)
logger.info("ChatOpenAI initialised and tools bound")


# ---------------------------------------------------------------------------
# LangGraph definitions
# ---------------------------------------------------------------------------
class AgentState(TypedDict):
    messages: List[HumanMessage | AIMessage | ToolMessage | SystemMessage]
    tool_calls: List[Dict[str, Any]] | None


def agent_node(state: AgentState) -> AgentState:
    logger.debug(f"agent_node → history size {len(state['messages'])}")
    response = llm.invoke(state["messages"])
    logger.debug("agent_node → LLM raw: %s", response)
    tool_calls = getattr(response, "tool_calls", None)
    logger.debug(f"agent_node → tool_calls present: {bool(tool_calls)}")
    return {"messages": [*state["messages"], response], "tool_calls": tool_calls}


def _extract_args(call: Dict[str, Any]) -> Dict[str, Any]:
    return call.get("arguments") or call.get("args") or {}


def tool_node(state: AgentState) -> AgentState:
    if not state[
        "tool_calls"
    ]:  # Should not happen based on graph logic, but safe check
        logger.warning("tool_node called without tool_calls in state.")
        return state
    # Handle multiple tool calls if the LLM generates them, although usually it's one
    tool_messages = []
    for call in state["tool_calls"]:
        name = call["name"]
        args = _extract_args(call)
        logger.debug(f"tool_node → executing {name} with args={args}")
        # Log the code being executed if it's our tool
        if name == "python_pandas_executor" and "code" in args:
            logger.debug(f"CODE TO EXECUTE:\n---\n{args['code']}\n---")

        fn = TOOLS_RUNTIME.get(name)
        result = fn(**args) if fn else f"ERROR: unknown tool '{name}'"

        # Process the result for AI message
        # If it's a plot reference, keep it as is for later processing
        # (The plot_id will be used when rendering the chat history)
        tool_message = ToolMessage(tool_call_id=call["id"], name=name, content=result)
        tool_messages.append(tool_message)

    return {"messages": [*state["messages"], *tool_messages]}  # Append all tool results


# Build LangGraph
graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tool", tool_node)
graph.set_entry_point("agent")
graph.add_conditional_edges(
    "agent", lambda s: bool(s.get("tool_calls")), {True: "tool", False: END}
)
graph.add_edge("tool", "agent")
agent_executor = graph.compile()
logger.info("LangGraph compiled – ready")

# ---------------------------------------------------------------------------
# Streamlit UI - MODIFIED LAYOUT
# ---------------------------------------------------------------------------

# Add session state variables for plots
if "messages" not in st.session_state:
    system_prompt = (
        "You are a data assistant.\n"
        "* If you can answer without code, do so.\n"
        "* Otherwise call `python_pandas_executor` with JSON like:\n"
        '  {"code": "result = df[\'age\'].mean()"}.\n'
        "* For creating plots, DO NOT use st.pyplot(). Instead, save the figure and return it:\n"
        '  {"code": "# Clear any previous plots and set a reasonable figure size\n'
        "plt.figure(figsize=(6, 3))  # Use smaller figure size\n"
        "plt.hist(df['age'], bins=5)\n"
        "plt.title('Age Distribution')\n"
        "plt.tight_layout()\n"
        "# Save the figure to a buffer instead of displaying it\n"
        "import io\n"
        "buf = io.BytesIO()\n"
        "plt.savefig(buf, format='png')\n"
        "buf.seek(0)\n"
        "# Return the buffer as result\n"
        "result = {'type': 'plot', 'data': buf}"
        '"}\n'
        "* When a plot is generated using the tool (which returns 'PLOT:<id>'), simply present the plot. Do **not** add extra text telling the user how to download or save the plot."
        "Return the answer as plain text once you have a result, including the 'PLOT:<id>' marker on its own line if a plot was generated."
        "Return the answer as plain text once you have a result."
        "Do not format tabular data as text unless requested by user."
        "When you comments on the graph or table complete the sentence with a dot, NEVER colon."
    )
    # Start with only the system prompt; user/AI messages will be added
    st.session_state.messages = [SystemMessage(content=system_prompt)]
    st.session_state.plots = {}  # Storage for plots
    logger.debug("Session started with system prompt")

# --- Scrollable Chat History Section ---
# Use st.container with a defined height to make the chat history scrollable
# Adjust the height as needed for your screen layout
chat_container = st.container()


def _extract_usage(ai_msg: AIMessage) -> Dict[str, int]:
    """Return {'prompt_tokens':..,'completion_tokens':..,'total_tokens':..} or {}."""
    # Newer langchain versions → response_metadata.token_usage
    meta = getattr(ai_msg, "response_metadata", None)
    if meta and "token_usage" in meta:
        return meta["token_usage"]
    # Older experimental field → usage_metadata
    meta2 = getattr(ai_msg, "usage_metadata", None)
    if meta2:
        return {
            "prompt_tokens": meta2.get("input_tokens", 0),
            "completion_tokens": meta2.get("output_tokens", 0),
            "total_tokens": meta2.get("total_tokens", 0),
        }
    return {}


def display_plot_from_id(plot_id):
    """Safely displays a plot from session state using its ID."""
    if plot_id in st.session_state.plots:
        st.image(st.session_state.plots[plot_id], use_container_width=False)
    else:
        logger.warning(f"Plot ID {plot_id} referenced but not found in state.")
        st.error(f"Error: Plot data for ID {plot_id} not found.")


with chat_container:
    logger.debug(
        f"Rendering chat history ({len(st.session_state.messages)} total messages in state)"
    )

    messages_to_render = st.session_state.messages  # Get a reference

    for i, msg in enumerate(messages_to_render):
        # Skip initial system message
        if isinstance(msg, SystemMessage) and i == 0:
            continue

        content = getattr(msg, "content", "")
        # Basic skip for fundamentally empty messages
        if not content or not content.strip():
            # Allow AIMessages that might become non-empty after filtering later
            if not isinstance(msg, AIMessage):
                continue

        # --- User Message ---
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.write(content)

        # --- Assistant Message (Handles Text and Looks Ahead for Plot) ---
        elif isinstance(msg, AIMessage):
            # Filter out any PLOT:id lines from the AI's text response
            text_to_display = "\n".join(
                line
                for line in content.splitlines()
                if not line.strip().startswith("PLOT:")
            ).strip()

            plot_id_to_render_after_text = None

            # Look ahead: Check if the *next* message is a ToolMessage with a plot
            if i + 1 < len(messages_to_render):
                next_msg = messages_to_render[i + 1]
                if isinstance(next_msg, ToolMessage) and getattr(
                    next_msg, "content", ""
                ).strip().startswith("PLOT:"):
                    # Found the plot tool message, extract its ID
                    plot_id_to_render_after_text = next_msg.content.strip()[5:]
                    # Optional: Could add validation here, e.g., check tool_call_id if needed

            # Render the assistant bubble only if there's text OR a plot found by lookahead
            if text_to_display or plot_id_to_render_after_text:
                with st.chat_message("assistant"):
                    # 1. Render the text part (if any)
                    if text_to_display:
                        st.write(text_to_display)
                    # 2. Render the plot (if found by lookahead)
                    if plot_id_to_render_after_text:
                        display_plot_from_id(plot_id_to_render_after_text)

# --- Chat Input Section (Streamlit places this at the bottom) ---
question = st.chat_input("Ask about the data …")
if question:
    logger.info(f"User: {question}")
    # Append the new user question to the state
    st.session_state.messages.append(HumanMessage(content=question))

    # Display the user message *immediately* in the container by rerunning
    # (Streamlit reruns automatically after chat_input)
    # We trigger the agent *after* adding the user message.
    # The results will be available on the *next* rerun cycle.
    with st.spinner("Thinking..."):  # Show a spinner while waiting for the agent
        logger.debug("Invoking agent executor...")
        state_out = agent_executor.invoke({"messages": st.session_state.messages})
        # Update the session state with the new messages from the agent
        st.session_state.messages = state_out["messages"]
        logger.debug(
            f"Agent finished. Messages in state: {len(st.session_state.messages)}"
        )

        # ---- Token accounting ---------------------------------------------
        # Find last AIMessage that contains usage info
        last_ai_msg = next(
            (
                m
                for m in reversed(st.session_state.messages)
                if isinstance(m, AIMessage)
            ),
            None,
        )
        if last_ai_msg is not None:
            usage = last_ai_msg.additional_kwargs.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

            logger.debug(st.session_state.messages)

            # ---- TOKEN ACCOUNTING (fixed) ------------------------------------
            last_ai = next(
                (
                    m
                    for m in reversed(st.session_state.messages)
                    if isinstance(m, AIMessage)
                ),
                None,
            )
            if last_ai:
                usage = _extract_usage(last_ai)
                st.session_state.total_tokens += usage.get("total_tokens", 0)
                st.session_state.total_cost += (
                    usage.get("prompt_tokens", 0) * _INPUT_COST_PER_TOKEN
                    + usage.get("completion_tokens", 0) * _OUTPUT_COST_PER_TOKEN
                )

    # Trigger an explicit rerun to display the new assistant/tool messages
    # immediately within the chat_container. Without this, you might have to
    # interact again to see the response.
    st.rerun()

# Final log after potential rerun
logger.debug(
    f"Finished Streamlit script run. Final messages count: {len(st.session_state.messages)}"
)
