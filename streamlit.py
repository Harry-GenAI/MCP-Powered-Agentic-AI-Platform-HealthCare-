import uuid
import requests
import streamlit as st

DEFAULT_API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="MCP-Powered Healthcare Agentic AI",
    page_icon="🏥",
    layout="wide",
)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🏥 MCP-Powered Healthcare Agentic AI")
st.caption("Agentic AI • LangGraph • RAG • MCP • Human-in-the-Loop")

with st.sidebar:
    st.header("⚙️ Configuration")

    api_url = st.text_input(
        "FastAPI URL",
        value=DEFAULT_API_URL,
    ).rstrip("/")

    st.divider()

    st.write("**Session ID**")
    st.code(st.session_state.session_id)

    if st.button("🔄 New Conversation", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.markdown(
        """
        **Architecture**

        User Query → FastAPI → Query Rewriter
        → LangGraph Orchestrator → Conditional Routing
        → RAG / MCP / Appointment
        → Validation / Human Review → Response
        """
    )

with st.sidebar:
    try:
        health_response = requests.get(
            f"{api_url}/",
            timeout=5,
        )

        if health_response.ok:
            st.success("API connected")
        else:
            st.warning(f"API returned {health_response.status_code}")

    except requests.RequestException:
        st.error("API unavailable")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant" and message.get("sources"):
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.write(f"• {source}")

query = st.chat_input("Ask a healthcare question...")

if query:
    st.session_state.messages.append(
        {"role": "user", "content": query}
    )

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Processing through agentic workflow..."):
            try:
                response = requests.post(
                    f"{api_url}/chat",
                    json={
                        "query": query,
                        "session_id": st.session_state.session_id,
                    },
                    timeout=300,
                )

                response.raise_for_status()
                data = response.json()

                answer = data.get(
                    "answer",
                    "No answer returned by the API.",
                )

                returned_session_id = data.get("session_id")
                if returned_session_id:
                    st.session_state.session_id = returned_session_id

                st.markdown(answer)

                sources = data.get("sources", [])
                if sources:
                    with st.expander("📚 Sources"):
                        for source in sources:
                            st.write(f"• {source}")

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                )

            except requests.exceptions.Timeout:
                message = (
                    "⏳ The request timed out. "
                    "The agentic workflow may still be processing."
                )
                st.error(message)
                st.session_state.messages.append(
                    {"role": "assistant", "content": message}
                )

            except requests.exceptions.ConnectionError:
                message = (
                    "❌ Could not connect to FastAPI. "
                    "Make sure the FastAPI server is running."
                )
                st.error(message)
                st.session_state.messages.append(
                    {"role": "assistant", "content": message}
                )

            except requests.exceptions.HTTPError as e:
                message = f"❌ FastAPI returned an error: {e}"
                st.error(message)
                st.session_state.messages.append(
                    {"role": "assistant", "content": message}
                )

            except (ValueError, requests.RequestException) as e:
                message = f"❌ Request failed: {e}"
                st.error(message)
                st.session_state.messages.append(
                    {"role": "assistant", "content": message}
                )

            except Exception as e:
                message = f"❌ Unexpected error: {e}"
                st.error(message)
                st.session_state.messages.append(
                    {"role": "assistant", "content": message}
                )
