import streamlit as st
import asyncio
import edge_tts
import os

# Page configuration
st.set_page_config(page_title="Text-to-Audio Converter", page_icon="🔊", layout="centered")

# Voice mappings including all South Indian and Hindi neural voices
VOICE_MAPPINGS = {
    "English (Male)": "en-US-ChristopherNeural",
    "English (Female)": "en-US-JennyNeural",
    "Spanish (Male)": "es-ES-AlvaroNeural",
    "Spanish (Female)": "es-ES-ElviraNeural",
    "French (Male)": "fr-FR-HenriNeural",
    "French (Female)": "fr-FR-DeniseNeural",
    "German (Male)": "de-DE-JonasNeural",
    "German (Female)": "de-DE-KatjaNeural",
    "Tamil India (Male)": "ta-IN-ValluvarNeural",
    "Tamil India (Female)": "ta-IN-PallaviNeural",
    "Tamil Sri Lanka (Male)": "ta-LK-KumarNeural",
    "Tamil Sri Lanka (Female)": "ta-LK-SaranyaNeural",
    "Tamil Malaysia (Male)": "ta-MY-SuryaNeural",
    "Tamil Malaysia (Female)": "ta-MY-KaniNeural",
    "Tamil Singapore (Male)": "ta-SG-AnbuNeural",
    "Tamil Singapore (Female)": "ta-SG-VenbaNeural",
    "Telugu (Male)": "te-IN-MohanNeural",
    "Telugu (Female)": "te-IN-ShrutiNeural",
    "Kannada (Male)": "kn-IN-GaganNeural",
    "Kannada (Female)": "kn-IN-SapnaNeural",
    "Malayalam (Male)": "ml-IN-MidhunNeural",
    "Malayalam (Female)": "ml-IN-SobhanaNeural",
    "Hindi (Male)": "hi-IN-MadhurNeural",
    "Hindi (Female)": "hi-IN-SwararaNeural",
    "Japanese (Male)": "ja-JP-KeitaNeural",
    "Japanese (Female)": "ja-JP-NanamiNeural",
    "Korean (Male)": "ko-KR-InJoonNeural",
    "Korean (Female)": "ko-KR-SunHiNeural",
    "Chinese (Simplified) Male": "zh-CN-YunxiNeural",
    "Chinese (Simplified) Female": "zh-CN-XiaoxiaoNeural",
    "Russian (Male)": "ru-RU-DmitryNeural",
    "Russian (Female)": "ru-RU-SvetlanaNeural",
}

SPEED_MAP = {
    "0.25x": "-75%",
    "0.5x": "-50%",
    "0.75x": "-25%",
    "1x": "+0%",
    "1.25x": "+25%",
    "1.5x": "+50%",
    "2x": "+100%"
}

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("about.png"):
        st.image("about.png", caption="Developer", width=150)
    st.markdown("### About")
    st.write("This application provides high-quality neural text-to-speech conversion for various languages, with a special focus on South Indian languages.")

# --- MAIN PAGE ---
# Center the logo
col_logo_l, col_logo_m, col_logo_r = st.columns([1, 2, 1])
with col_logo_m:
    if os.path.exists("jp.png"):
        st.image("jp.png", width=200)
    st.markdown("<h1 style='text-align: center;'>Text-to-Audio Converter</h1>", unsafe_allow_html=True)

st.markdown("<p style='text-align: center;'>Convert your text to high-quality neural speech for free!</p>", unsafe_allow_html=True)
st.divider()

# Layout for inputs
col1, col2 = st.columns([2, 1])

with col1:
    text_input = st.text_area("Enter Text:", placeholder="Type something here...", height=200)

with col2:
    voice_choice = st.selectbox("Select Voice:", options=list(VOICE_MAPPINGS.keys()))
    speed_choice = st.selectbox("Select Speed:", options=list(SPEED_MAP.keys()), index=3)

if st.button("Convert to Audio", type="primary", use_container_width=True):
    if not text_input:
        st.warning("Please enter some text first!")
    else:
        try:
            with st.spinner("Generating audio..."):
                output_file = "output.mp3"
                voice_id = VOICE_MAPPINGS[voice_choice]
                rate = SPEED_MAP[speed_choice]

                async def generate_audio():
                    communicate = edge_tts.Communicate(text_input, voice_id, rate=rate)
                    await communicate.save(output_file)

                asyncio.run(generate_audio())

                st.success("Conversion complete!")
                st.audio(output_file, format="audio/mp3")

                with open(output_file, "rb") as f:
                    st.download_button(
                        label="Download MP3",
                        data=f,
                        file_name="converted_audio.mp3",
                        mime="audio/mp3"
                    )

        except Exception as e:
            st.error(f"An error occurred: {e}")

st.divider()
st.caption("Powered by edge-tts and Streamlit Cloud")
