from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from typing import List, Dict
import re
import os


class LinkedInPostGenerator:
    def __init__(self, api_key: str):
        """
        Initialize the LinkedIn Post Generator with OpenAI API key.

        Args:
            api_key (str): OpenAI API key
        """

        self.llm = ChatGroq(
            model="gemma2-9b-it",
            api_key=os.getenv("GROQ_API_KEY"),
            max_tokens=1024,
            temperature=0.7,
        )

        # Predefined templates
        self.templates = {
            "informative": """
            Write a professional LinkedIn post about: {prompt}
            The post should be informative and provide value to the readers.
            Keep the tone {tone} and the length approximately {words} words.
            {hashtags}
            {emojis}
            Strictly output only the post content, no other text or comments and any fillers. DO NOT OUTPUT ANYTHING ELSE.
            """,
            "casual": """
            Write a casual but professional LinkedIn post about: {prompt}
            The post should be engaging and conversational.
            Keep the tone {tone} and the length approximately {words} words.
            {hashtags}
            {emojis}
            Strictly output only the post content, no other text or comments and any fillers. DO NOT OUTPUT ANYTHING ELSE.
            """,
            "inspirational": """
            Write an inspirational LinkedIn post about: {prompt}
            The post should motivate and inspire the readers.
            Keep the tone {tone} and the length approximately {words} words.
            {hashtags}
            {emojis}
            Strictly output only the post content, no other text or comments and any fillers. DO NOT OUTPUT ANYTHING ELSE.
            """,
        }

        # Tone options
        self.tones = [
            "professional",
            "friendly",
            "enthusiastic",
            "authoritative",
            "casual",
        ]

    def generate_hashtags(self, prompt: str) -> str:
        """
        Generate relevant hashtags based on the prompt.

        Args:
            prompt (str): The input prompt

        Returns:
            str: Generated hashtags
        """
        hashtag_prompt = f"Generate 5 relevant hashtags for a LinkedIn post about: {prompt}. Return only the hashtags separated by spaces."
        hashtags = self.llm.invoke(hashtag_prompt)
        return hashtags.content

    def add_emojis(self, text: str) -> str:
        """
        Add relevant emojis to the text.

        Args:
            text (str): The text to add emojis to

        Returns:
            str: Text with emojis
        """
        emoji_prompt = f"Add relevant emojis to this LinkedIn post to make it more engaging:\n\n{text}\n\nReturn the post with emojis added."
        result = self.llm.invoke(emoji_prompt)
        return result.content

    def analyze_post(self, post: str) -> Dict:
        """
        Analyze the generated post for word count, character count, and sentence count.

        Args:
            post (str): The generated post

        Returns:
            Dict: Analysis results
        """
        word_count = len(re.findall(r"\w+", post))
        char_count = len(post)
        sentence_count = len(re.findall(r"[.!?]+", post))

        return {
            "word_count": word_count,
            "char_count": char_count,
            "sentence_count": sentence_count,
        }

    def generate_post(
        self,
        prompt: str,
        words: int = 200,
        tone: str = "professional",
        template: str = "informative",
        add_hashtags: bool = False,
        add_emojis: bool = False,
        variations: int = 1,
    ) -> List[Dict]:
        """
        Generate LinkedIn post(s) based on the given parameters.

        Args:
            prompt (str): The main prompt for the post
            words (int): Approximate word count
            tone (str): Tone of the post
            template (str): Template to use
            add_hashtags (bool): Whether to add hashtags
            add_emojis (bool): Whether to add emojis
            variations (int): Number of variations to generate (1-3)

        Returns:
            List[Dict]: List of generated posts with analysis
        """
        if variations < 1 or variations > 3:
            raise ValueError("Variations must be between 1 and 3")

        if tone not in self.tones:
            raise ValueError(f"Invalid tone. Available tones: {', '.join(self.tones)}")

        if template not in self.templates:
            raise ValueError(
                f"Invalid template. Available templates: {', '.join(self.templates.keys())}"
            )

        results = []

        hashtags = self.generate_hashtags(prompt) if add_hashtags else ""
        hashtags_str = f"Include these hashtags: {hashtags}" if hashtags else ""

        for _ in range(variations):
            # Select the template
            selected_template = self.templates[template]

            # Create prompt template
            prompt_template = PromptTemplate(
                input_variables=["prompt", "tone", "words", "hashtags", "emojis"],
                template=selected_template,
            )

            # Create chain using the new pipe syntax
            chain = prompt_template | self.llm

            # Invoke the chain with parameters
            response = chain.invoke(
                {
                    "prompt": prompt,
                    "tone": tone,
                    "words": words,
                    "hashtags": hashtags_str,
                    "emojis": (
                        "Add relevant emojis to make the post more engaging."
                        if add_emojis
                        else ""
                    ),
                }
            )

            generated_post = response.content

            # Add emojis if requested
            if add_emojis:
                generated_post = self.add_emojis(generated_post)

            # Analyze the post
            analysis = self.analyze_post(generated_post)

            results.append({"post": generated_post, "analysis": analysis})

        return results


# vllm serve shuyuej/Llama-3.2-3B-Instruct-GPTQ   --task generate   --trust-remote-code   --max-model-len 120000
