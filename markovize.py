import markovify
import json
import re
from pydub import AudioSegment
from pydub.playback import play
from pydub.silence import split_on_silence
import subprocess
import tempfile
import simpleaudio as sa
import os
import time

def run(file_name):
    # Load in the audio recording
    recording = AudioSegment.from_wav('./resources/' + file_name)
    input(file_name)

    # Get raw text as string.
    with open('transcript.txt') as f:
        text = f.read()

    # Get the clist
    with open('clist.json') as f:
        clist = json.load(f)

    # Build the model.
    text_model = markovify.Text(text)

    # Print randomly-generated sentences
    inp = ""

    while inp != "end":
        sen = text_model.make_sentence()
        input(sen)
        # Remove punctuation
        sen = re.sub(r'[^\w\s]','',sen)
        # Break our sentence into words
        words = sen.split(' ')
        # For each word, find corresponding clip in clist
        clips = []
        
        for word in words:
            for clip in clist:
                if clip['word'] == word:
                    clip['start'] = float(clip['start'])
                    clip['end'] = float(clip['end'])
                    clips.append(clip)
                    break
        # Now iterate over our clips
        for clip in clips:
            # Get audio segment
            seg = recording[clip['start']*1000-100:clip['end']*1000 + 100]
            # Split on silence
            audio_chunks = split_on_silence(seg, min_silence_len=70, silence_thresh=-40, keep_silence=20)
            print(len(audio_chunks))

            min = 1000
            sum = 0

            for chunk in audio_chunks:
                if sum >= clip['end'] - clip['start']:
                    seg = chunk
                    break
                sum += len(chunk)

            # Play audio segment
            with tempfile.NamedTemporaryFile("w+b", suffix=".wav") as f:
                fileName = f.name

            seg.export(fileName, "wav")
            wave_obj = sa.WaveObject.from_wave_file(fileName)
            duration = len(seg) / 1000
            play_obj = wave_obj.play()
            time.sleep(max(0, duration))
            os.remove(fileName)
            time.sleep(0.1)

run('mudge.wav')