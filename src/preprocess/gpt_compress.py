# gpt_compress.py

import os
import openai

# Set your API key via an environment variable: export OPENAI_API_KEY="YOUR_KEY"
# or hard-code it here (not recommended).
openai.api_key = os.getenv("OPENAI_API_KEY")

def gpt_compress_chunk(chunk: str, model="gpt-3.5-turbo") -> str:
    """
    Calls GPT (new openai>=1.0.0 API) to compress/clean each chunk,
    removing filler words, sponsor blurbs, and irrelevant fluff.
    
    :param chunk: The transcript chunk to summarize.
    :param model: The GPT model name, e.g., "gpt-3.5-turbo".
    :return: A cleaned, concise version of the chunk.
    """

    prompt = (
        "You are an expert content editor. "
        "Remove irrelevant fluff, filler words, disclaimers, or sponsor messages, "
        "and keep the trading context. Make the text concise:\n\n"
        f"{chunk}"
    )

    response = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    # The new openai>=1.0.0 returns .choices[0].message.content
    compressed_text = response.choices[0].message.content.strip()
    return compressed_text