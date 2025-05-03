import streamlit as st
import requests
import pandas as pd
import json

# -------------------------------
# 🎨 Custom Style
# -------------------------------
def apply_custom_style():
    style = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Freestyle+Script&family=Montserrat:wght@400;700&display=swap');

    body, .stApp {
        background-color: #009BC3;
        font-family: 'Montserrat', sans-serif;
    }

    .title {
        font-family: 'Freestyle Script', cursive;
        font-size: 72px;
        color: white;
        text-align: center;
        margin-top: -30px;
        margin-bottom: 30px;
    }

    .section-label {
        font-size: 24px;
        color: white;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .block-container {
        padding-top: 2rem;
        padding-left: 5rem;
        padding-right: 5rem;
        max-width: 100% !important;
    }
    </style>
    """
    st.markdown(style, unsafe_allow_html=True)

apply_custom_style()

# -------------------------------
# 📁 Load Test Transcripts
# -------------------------------
with open("synthetic_transcripts.json", "r", encoding="utf-8") as f:
    transcripts_data = json.load(f)

all_transcripts = [f"Positive {i+1}" for i in range(len(transcripts_data["positive"]))] + \
                  [f"Negative {i+1}" for i in range(len(transcripts_data["negative"]))]

# -------------------------------
# 🧾 Page Layout
# -------------------------------
st.markdown('<div style="margin-top: 40px;">', unsafe_allow_html=True)
st.image("background.jpg", width=180)  # Mr. Cooper logo
st.markdown('<div class="title">FormPilot</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1], gap="large")

# -------------------------------
# 🧠 Session State for Transcript
# -------------------------------
if "transcript" not in st.session_state:
    st.session_state["transcript"] = ""

# -------------------------------
# 📥 Right Column - File Upload & Test Case
# -------------------------------
with col2:
    st.markdown('<div class="section-label">Upload a text file</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Drag and Drop a file", type=["txt"], label_visibility="collapsed")

    st.markdown('<div class="section-label" style="margin-top: 30px;">Test Cases</div>', unsafe_allow_html=True)
    selected = st.selectbox("Choose a test case", [""] + all_transcripts, label_visibility="collapsed")

    # Update session state if new file or dropdown is selected
    if uploaded_file:
        st.session_state["transcript"] = uploaded_file.read().decode("utf-8")
    elif selected:
        idx = int(selected.split(" ")[1]) - 1
        st.session_state["transcript"] = transcripts_data["positive"][idx] if "Positive" in selected else transcripts_data["negative"][idx]

# -------------------------------
# 📝 Left Column - Transcript Input + Extract
# -------------------------------
with col1:
    st.markdown('<div class="section-label">Transcript</div>', unsafe_allow_html=True)
    st.text_area(label="", value=st.session_state["transcript"], height=250, key="transcript", label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Extract Fields"):
        if st.session_state["transcript"].strip() == "":
            st.warning("Please enter a transcript or upload a file.")
        else:
            with st.spinner("Extracting fields..."):
                try:
                    url = "http://127.0.0.1:8000/extract-fields"
                    res = requests.post(url, json={"transcript": st.session_state["transcript"]})
                    data = res.json()

                    # ✅ Correct handling for raw list response
                    if not isinstance(data, list):
                        st.error("No fields returned or response is invalid.")
                        st.json(data)  # show raw result for debugging
                    elif len(data) == 0:
                        st.warning("The model returned an empty list. Try a longer or clearer transcript.")
                    else:
                        df = pd.DataFrame(data)

                        def color_conf(val):
                            if val >= 0.9:
                                return "background-color: #d0f0c0;"
                            elif val >= 0.7:
                                return "background-color: #fff8b3;"
                            else:
                                return "background-color: #f8d7da;"

                        st.subheader("🧾 Extracted Fields")
                        st.dataframe(df.style.applymap(color_conf, subset=["confidence_score"]))

                        csv = df.to_csv(index=False).encode("utf-8")
                        st.download_button("📥 Download CSV", csv, "extracted_fields.csv", "text/csv")

                except Exception as e:
                    st.error(f"Error: {e}")
