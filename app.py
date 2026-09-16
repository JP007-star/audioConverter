import streamlit as st
import asyncio
import edge_tts
import os

# Page configuration
st.set_page_config(page_title="Text-to-Audio Converter", page_icon="🔊")

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

st.title("🔊 Text-to-Audio Converter")
st.markdown("Convert your text to high-quality neural speech. Supports multiple South Indian languages for free!")

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    text_input = st.text_area("Enter Text:", placeholder="Type something here...", height=200)

with col2:
    voice_choice = st.selectbox("Select Voice:", options=list(VOICE_MAPPINGS.keys()))
    speed_choice = st.selectbox("Select Speed:", options=list(SPEED_MAP.keys()), index=3)

if st.button("Convert to Audio", type="primary"):
    if not text_input:
        st.warning("Please enter some text first!")
    else:
        try:
            with st.spinner("Generating audio..."):
                # File path for the generated audio
                output_file = "output.mp3"
                voice_id = VOICE_MAPPINGS[voice_choice]
                rate = SPEED_MAP[speed_choice]

                async def generate_audio():
                    communicate = edge_tts.Communicate(text_input, voice_id, rate=rate)
                    await communicate.save(output_file)

                # Run the async function
                asyncio.run(generate_audio())

                # Display the audio player
                st.success("Conversion complete!")
                st.audio(output_file, format="audio/mp3")

                # Provide a download button
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
