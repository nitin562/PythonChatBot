from openai import OpenAI,OpenAIError
from Bot.responses import success,error
import os

client = OpenAI(
    base_url="https://api.groq.com/openai/v1", api_key=os.getenv("groq_api_key")
)


def askToGroq(content,query):
    try:
        payload=f"Context:\n${content}\n\nUser Query: ${query}. If you Know some links that can help me, then also show them"
        response=client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a Chat Bot. you must answer the questions on the basis of details provided but you must provide answer like human. If You find query is not belongs to detail then you can ask to refraim the question but dont provide information outside details.",
            },
            {
                "role": "user",
                "content": payload,
            },
        ],
        model="llama3-8b-8192",
        max_tokens=500,
        )
        print(response)
        return success(200,"message",response.choices[0].message.content)
    except OpenAIError as e:
        print("groq",e)
        return error(500,"server",str(e))
