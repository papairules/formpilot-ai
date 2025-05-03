import streamlit as st
import pandas as pd
import json
import openai
import streamlit as st
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]

# -------------------------------
# 🔐 API Setup
# -------------------------------
openai.api_key = OPENAI_API_KEY  # Or use: st.secrets["OPENAI_API_KEY"]

# -------------------------------
# 🤖 LLM Extractor Logic
# -------------------------------
def extract_fields_from_transcript(transcript):
    system_prompt = """
You are an expert mortgage assistant.
Your job is to extract standardized 1003 mortgage application form fields from transcripts.

For each field, return:
- field_name (string)
- field_value (string)
- confidence_score (float from 0 to 1)
- short_explanation (max 20 words explaining how you found it)

⚠️ Return ONLY a valid JSON array like this:

[
  {
    "field_name": "Borrower Name",
    "field_value": "Michael Harris",
    "confidence_score": 0.95,
    "short_explanation": "Introduced himself clearly by name."
  },
  {
    "field_name": "Loan Amount",
    "field_value": "$400,000",
    "confidence_score": 0.90,
    "short_explanation": "Said 'I'd like to borrow around $400,000'."
  }
]
    """

    user_prompt = f"""Transcript:\n\"\"\"{transcript}\"\"\"\n\nExtract the fields as per instructions above. Do not return anything else."""

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )

    try:
        raw = response["choices"][0]["message"]["content"]
        return json.loads(raw)
    except:
        return []

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
st.image("background.jpg", width=180)
st.markdown('<div class="title">FormPilot</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1], gap="large")

if "transcript" not in st.session_state:
    st.session_state["transcript"] = ""

with col2:
    st.markdown('<div class="section-label">Upload a text file</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Drag and Drop a file", type=["txt"], label_visibility="collapsed")

    st.markdown('<div class="section-label" style="margin-top: 30px;">Test Cases</div>', unsafe_allow_html=True)
    selected = st.selectbox("Choose a test case", [""] + all_transcripts, label_visibility="collapsed")

    if uploaded_file:
        st.session_state["transcript"] = uploaded_file.read().decode("utf-8")
    elif selected:
        idx = int(selected.split(" ")[1]) - 1
        st.session_state["transcript"] = transcripts_data["positive"][idx] if "Positive" in selected else transcripts_data["negative"][idx]

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
                    result = extract_fields_from_transcript(st.session_state["transcript"])
                    if not result:
                        st.warning("Empty or invalid result. Try a better transcript.")
                    else:
                        df = pd.DataFrame(result)

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
