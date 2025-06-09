import torch_patch
import streamlit as st
from modules.router import route_query 
import traceback
import io
import pandas as pd

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.set_page_config(page_title="TariffBot", layout="centered")
with st.sidebar:
    st.markdown("### System Info")
    st.markdown("- **Model**: Hugging Face - `google/flan-t5-base`")
    st.markdown("- **System**: 32GB RAM, 4GB VRAM")
    st.markdown("### BY PAULINUS JUA")

st.title("TariffBot: HTS Tariff Tool & RAG Agent")

query = st.text_area("Enter your question or HTS duty details:", height=100)

if st.button("Get Answer") and query.strip():
    try:
        response = route_query(query, st.session_state.chat_history)
        st.markdown("### Response:")
        st.success(response)
        if "Duties Breakdown" in response:
            table_start = response.split("Duties Breakdown:")[1].strip()
            df_lines = table_start.split("\n")[2:]  

            data = [line.strip("| ").split("|") for line in df_lines if line.startswith("|")]
            df = pd.DataFrame(data, columns=["Duty Type", "Rate", "Amount"])

            # Download button
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="Download HTS Duties Results CSV",
                data=csv_buffer.getvalue(),
                file_name="hts_duties_.csv",
                mime="text/csv"
                )

    except Exception:
        st.markdown("### Error:")
        st.code(traceback.format_exc())  

if st.checkbox("Show chat history"):
    for i, (q, a) in enumerate(st.session_state.chat_history):
        st.markdown(f"**Q{i+1}:** {q}")
        st.markdown(f"**A{i+1}:** {a}")


#streamlit run app.py