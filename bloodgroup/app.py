import streamlit as st
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image

# Page config
st.set_page_config(page_title="Blood Dashboard", layout="wide")

# 🔥 DARK PREMIUM CSS
st.markdown("""
<style>
body {
    background-color: #0f172a;
}
.main {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}
.card {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    text-align: center;
    color: white;
}
.title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: #38bdf8;
}
.subtitle {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 20px;
}
.stButton>button {
    background: linear-gradient(90deg, #38bdf8, #6366f1);
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# Load model
model = load_model("blood_group_model.h5")

# Session state
if "history" not in st.session_state:
    st.session_state.history = []

# Title
st.markdown('<div class="title">🩸 Blood Group Detection</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Real-time AI Dashboard</div>', unsafe_allow_html=True)

# Metrics
col1, col2, col3 = st.columns(3)

total = len(st.session_state.history)
last = st.session_state.history[-1].get("Result", st.session_state.history[-1].get("result", "N/A")) if total > 0 else "N/A"
avg = np.mean([x.get("Confidence", x.get("confidence", 0)) for x in st.session_state.history]) if total > 0 else 0

col1.markdown(f'<div class="card">📊 Total<br><h2>{total}</h2></div>', unsafe_allow_html=True)
col2.markdown(f'<div class="card">🧬 Last<br><h2>{last}</h2></div>', unsafe_allow_html=True)
col3.markdown(f'<div class="card">🎯 Confidence<br><h2>{avg:.2f}</h2></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Layout
col1, col2 = st.columns([1,1])

# LEFT - Upload
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    patient_name = st.text_input("👤 Patient Name", placeholder="Enter patient name...")
    uploaded_file = st.file_uploader("📤 Upload Image", type=["jpg", "png", "jpeg", "bmp"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        if image.mode != "RGB":
            image = image.convert("RGB")

        st.image(image, width=350)

    st.markdown('</div>', unsafe_allow_html=True)

# RIGHT - Prediction
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    if uploaded_file:
        if st.button("🔍 Predict"):

            with st.spinner("Analyzing..."):

                # Preprocess
                img = image.resize((224, 224))
                img = np.array(img) / 255.0
                img = np.expand_dims(img, axis=0)

                # Predict
                prediction = model.predict(img)

                # ✅ FIXED CLASS ORDER (Standard Alphabetical for Keras)
                classes = ['A+', 'A-', 'AB+', 'AB-', 'B+', 'B-', 'O+', 'O-']

                pred_index = np.argmax(prediction)
                result = classes[pred_index]
                confidence = float(np.max(prediction))

                # Save history
                st.session_state.history.append({
                    "Patient Name": patient_name if patient_name.strip() else "Unknown",
                    "Result": result,
                    "Confidence": confidence
                })

                # Output
                st.success(f"🧬 Blood Group: {result}")
                st.progress(confidence)
                st.write(f"Confidence: {confidence:.2f}")

                # 🔍 DEBUG (optional - remove later)
                st.write("Prediction Array:", prediction)
                st.write("Predicted Index:", pred_index)

    else:
        st.info("Upload image to start")

    st.markdown('</div>', unsafe_allow_html=True)

# History
st.markdown("### 📊 Prediction History")

if st.session_state.history:
    st.dataframe(st.session_state.history, use_container_width=True)
else:
    st.info("No predictions yet")