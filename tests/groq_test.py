from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL
client = Groq()
completion = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "user",
            "content": "hi"
        }
    ]
)
print(completion.choices[0].message.content)