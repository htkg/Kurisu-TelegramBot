from pydub import AudioSegment
import os
import openai

def ogg2wav(filename):
    AudioSegment.from_ogg(filename).export(filename.replace('.ogg','.wav'), format='wav')    # maybe use original resolution to make smaller
    os.remove(filename)
    
async def whisper_predict(filename):
    audio_file= open(filename, "rb")
    transcript = await openai.Audio.atranscribe("whisper-1", audio_file)
    audio_file.close()
    return transcript['text']

async def v2t(filename):
    if filename.endswith('.ogg'):
        ogg2wav(filename)
        filename = filename.replace('.ogg','.wav')
    
    transcript = await whisper_predict(filename)
    return transcript