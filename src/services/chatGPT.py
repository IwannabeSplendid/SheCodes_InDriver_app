import whisper
from openai import AsyncOpenAI

from src.settings import get_settings

settings = get_settings()

client = AsyncOpenAI(
    api_key=settings.CHATGPT_SECRET,
)


model = whisper.load_model("base")

async def translate_voice_message(voice_message):    
    text_message = model.transcribe("audio.mp3")
    
    messages = [ {"role": "system", "content": 
                f'''Extract info about  pickup address and destination of the ride from the given text. 
                If he wants to order ride for another date, extract a date in date time and make boolean scheduled True. 
                Return json object with the following fields: pick_up_location, destination, datetime, scheduled without any comments. 
                Here is a text message: {text_message}'''} ] 
    
    chat_completion = await client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo",
    )

    reply = chat_completion.choices[0].message.content 
    print(f"ChatGPT: {reply}") 

    return reply
