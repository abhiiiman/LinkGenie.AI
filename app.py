from flask import Flask, request, jsonify
from linkedin_generator import LinkedInPostGenerator
import streamlit as st
import os

# Flask API
app = Flask(__name__)


@app.route("/generate", methods=["POST"])
def generate_post():
    data = request.json

    try:
        generator = LinkedInPostGenerator(api_key=st.secrets["GROQ_API_KEY"])
        results = generator.generate_post(
            prompt=data["prompt"],
            words=data.get("words", 200),
            tone=data.get("tone", "professional"),
            template=data.get("template", "informative"),
            add_hashtags=data.get("add_hashtags", False),
            add_emojis=data.get("add_emojis", False),
            variations=data.get("variations", 1),
        )
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# Streamlit App
def streamlit_app():
    st.set_page_config(page_title="LinkGenie.AI", page_icon="🪄")

    st.markdown(
        "<h1 style='text-align: center;'>🪄 LinkGenie.AI <span style='font-size:1.5em;'>✨</span></h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='text-align: center; font-size:1.2em;'>"
        "🚀 <b>Generate professional LinkedIn posts with AI</b> 🤖<br>"
        "Unleash your creativity and boost your LinkedIn presence! 🌟"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    with st.form("post_generator"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📝 Your Prompt")
            prompt = st.text_area(
                "What do you want to post about? 💡",
                placeholder="E.g. Share your thoughts on AI in 2025... 🤔",
            )
            st.markdown("### 🔢 Word Count")
            words = st.slider("Approx. Words ✍️", min_value=50, max_value=500, value=200)
            st.markdown("### 🎤 Voice Tone")
            tone = st.selectbox(
                "Choose a tone 🎭",
                [
                    "professional 🧑‍💼",
                    "friendly 😊",
                    "enthusiastic 🤩",
                    "authoritative 🦸‍♂️",
                    "casual 😎",
                ],
            )

        with col2:
            st.markdown("### 🏗️ Template")
            template = st.selectbox(
                "Select a template 🧩",
                [
                    "informative 📚",
                    "casual 🥳",
                    "inspirational 🌈",
                ],
            )
            st.markdown("### 🔄 Variations")
            variations = st.selectbox("How many variations? 🔢", [1, 2, 3])
            st.markdown("### #️⃣ Hashtags & Emojis")
            add_hashtags = st.checkbox("Generate Hashtags #️⃣", value=True)
            add_emojis = st.checkbox("Include Emojis 😃", value=True)

        submitted = st.form_submit_button("✨ Generate Post! ✨")

    if submitted and prompt:
        with st.spinner("🪄 Generating your LinkedIn post... Please wait! ⏳"):
            try:
                # Remove emojis from tone and template for backend
                tone_clean = tone.split(" ")[0]
                template_clean = template.split(" ")[0]
                generator = LinkedInPostGenerator(api_key=st.secrets["GROQ_API_KEY"])
                results = generator.generate_post(
                    prompt=prompt,
                    words=words,
                    tone=tone_clean,
                    template=template_clean,
                    add_hashtags=add_hashtags,
                    add_emojis=add_emojis,
                    variations=variations,
                )

                st.success("🎉 Your LinkedIn post(s) are ready! 🚀")
                for i, result in enumerate(results, 1):
                    st.markdown(f"---\n### ✨ Variation {i} ✨")
                    st.write(f"{result['post']}")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📝 Words", result["analysis"]["word_count"])
                    with col2:
                        st.metric("🔠 Characters", result["analysis"]["char_count"])
                    with col3:
                        st.metric("🔢 Sentences", result["analysis"]["sentence_count"])

                st.balloons()

            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")


if __name__ == "__main__":
    # To run the Streamlit app: streamlit run app.py
    # To run the Flask API: flask run or python app.py
    # For this example, we'll default to Streamlit
    streamlit_app()
