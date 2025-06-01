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
    st.set_page_config(page_title="LinkedIn Post Generator", page_icon="📝")

    st.title("LinkedIn Post Generator")
    st.write("Generate professional LinkedIn posts with AI")

    with st.form("post_generator"):
        col1, col2 = st.columns(2)

        with col1:
            prompt = st.text_area(
                "Your Prompt", placeholder="What do you want to post about?"
            )
            words = st.slider("Approx. Words", min_value=50, max_value=500, value=200)
            tone = st.selectbox(
                "Voice Tone",
                ["professional", "friendly", "enthusiastic", "authoritative", "casual"],
            )

        with col2:
            template = st.selectbox(
                "Template", ["informative", "casual", "inspirational"]
            )
            variations = st.selectbox("Number of Variations", [1, 2, 3])
            add_hashtags = st.checkbox("Generate Hashtags", value=True)
            add_emojis = st.checkbox("Include Emojis", value=True)

        submitted = st.form_submit_button("Generate")

    if submitted and prompt:
        with st.spinner("Generating your LinkedIn post..."):
            try:
                generator = LinkedInPostGenerator(api_key=st.secrets["GROQ_API_KEY"])
                results = generator.generate_post(
                    prompt=prompt,
                    words=words,
                    tone=tone,
                    template=template,
                    add_hashtags=add_hashtags,
                    add_emojis=add_emojis,
                    variations=variations,
                )

                for i, result in enumerate(results, 1):
                    st.subheader(f"Variation {i}")
                    st.write(result["post"])

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Words", result["analysis"]["word_count"])
                    with col2:
                        st.metric("Characters", result["analysis"]["char_count"])
                    with col3:
                        st.metric("Sentences", result["analysis"]["sentence_count"])

                    st.divider()

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    # To run the Streamlit app: streamlit run app.py
    # To run the Flask API: flask run or python app.py
    # For this example, we'll default to Streamlit
    streamlit_app()
