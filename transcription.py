import io
import os

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

clip = {
    "start": 0,
    "end": 0,
    "word": ""
}

if not 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'D:\\School\\2018\\MHacks11\\MarkoVid\\Markov Chains-06f4fd5f0bf6.json'

client = speech.SpeechClient()

infile = input('Enter filename: ')

file_name = os.path.join(os.path.dirname(__file__), 'resources', infile)

with io.open(file_name, 'rb') as audio_file:
    content = audio_file.read()
    audio = types.RecognitionAudio(content=content)

config = types.RecognitionConfig(encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
                                 sample_rate_hertz=16000,
                                 language_code='en-US',
                                 enable_word_time_offsets=True,
                                 enable_automatic_punctuation=True)

response = client.recognize(config, audio)

s = ""

clist = []

for i, result in enumerate(response.results):
        alternative = result.alternatives[0]
        s += alternative.transcript

        for word_info in alternative.words:
            word = word_info.word
            start_time = word_info.start_time
            end_time = word_info.end_time
            clist.append({word_info.start_time.seconds + word_info.start_time.nanos * 1e-9,
                          word_info.end_time.seconds + word_info.end_time.nanos * 1e-9, word_info.word})
            print('Word: {}, start_time: {}, end_time: {}'.format(
                word,
                start_time.seconds + start_time.nanos * 1e-9,
                end_time.seconds + end_time.nanos * 1e-9))

print(s)
