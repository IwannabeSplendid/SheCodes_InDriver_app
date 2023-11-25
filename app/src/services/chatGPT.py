# import whisper
from openai import OpenAI

from src.settings import get_settings


settings = get_settings()


client = OpenAI(
    api_key= settings.CHATGPT_SECRET,
)

# model = whisper.load_model("base")

# def voice2message(path):
#     audio = whisper.load_audio(path)
#     audio = whisper.pad_or_trim(audio)

#     mel = whisper.log_mel_spectrogram(audio).to(model.device)

#     options = whisper.DecodingOptions(fp16 = False)
#     result = whisper.decode(model, mel, options)

#     return result.text

async def translate_voice_message(text_message):
    messages = [ {"role": "system", "content": 
                f'''Extract info about  pickup address and destination of the ride from the given text. 
                If he wants to order ride for specific time, extract a date in datetime format and make boolean scheduled True. If no time information is provided, set it to false. In case of True, add all such dates into a list.
                Also, from the message, try to understand if the person is a regular client or one who has disabilities, in which case, add is_inclusive as boolean true. Also, fetch car type if exists in the message, if doesn't, make it "econom". These are econom, comfort, elite, business.
                Return json object with the following fields: pick_up_location, destination, datetime, car_type, is_inclusive, scheduled without any comments. 
                Here is a text message:: {text_message}'''} ]

    chat_completion = client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo",
    )
    reply = chat_completion.choices[0].message.content

    return reply
