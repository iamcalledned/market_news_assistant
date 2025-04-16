import openai
from config import OPENAI_API_KEY, MODEL_NAME

openai.api_key = OPENAI_API_KEY

def summarize_headlines(prompt, headlines):
    formatted = "\n\n".join(
        [f"- {item['title']}: {item['snippet']}" for item in headlines]
    )

    system_msg = (
        "You are a seasoned equity strategist. Based on the provided headlines, "
        "determine the current market sentiment and outlook. Summarize key risks and "
        "trader sentiment. Be direct and opinionated."
    )

    user_msg = f"{prompt}\n\nHeadlines:\n{formatted}"

    response = openai.ChatCompletion.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        temperature=0.7,
        max_tokens=500
    )

    return response.choices[0].message["content"]
