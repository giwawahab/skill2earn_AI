from openai import OpenAI
from .prompt_context import SKILL_TO_EARN_SYSTEM_PROMPT
from .tools import tools, handle_tool_calls
from .styles import CSS, JS, EXAMPLES
from dotenv import load_dotenv
import os
import gradio as gr

load_dotenv(override=True)

MODEL_NAME = "openai/gpt-oss-20b"

# openai = OpenAI()
openai = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

system = [{"role": "system", "content": SKILL_TO_EARN_SYSTEM_PROMPT}]


def chat(message, history):
    history = [{"role": h["role"], "content": h["content"]} for h in history]
    messages = system + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=MODEL_NAME, messages=messages, tools=tools)
    while response.choices[0].finish_reason == "tool_calls":
        message = response.choices[0].message
        tool_calls = message.tool_calls
        results = handle_tool_calls(tool_calls)
        messages.append(message)
        messages.extend(results)
        response = openai.chat.completions.create(model=MODEL_NAME, messages=messages, tools=tools)
    return response.choices[0].message.content


if __name__ == "__main__":
    gr.ChatInterface(
        chat,
        examples=EXAMPLES,
        title="Skill2earn Idea 🤗",
        description="Find your way to the paying job that match your skill set",
        chatbot=gr.Chatbot(show_label=False),
    ).launch(
    css=CSS,
    js=JS,
    theme=gr.themes.Base(),
    server_name="127.0.0.1",
    server_port=int(os.environ.get("PORT", 7860)),
    share=False
)
