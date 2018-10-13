import markovify
import json
import re
from pydub import AudioSegment
from pydub.playback import play
from pydub.silence import split_on_silence
import tempfile
import simpleaudio as sa
import os
import time
from random import shuffle
import cv2

def run(file_name):
    # Load in the audio recording
    recording = AudioSegment.from_wav('resources/' + file_name)
    # Load in the video recording

    name = file_name[:-4]

    cap = cv2.VideoCapture('resources/' + name + '.mp4')
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Get raw text as string.
    with open(name + '_transcript.txt') as f:
        text = f.read()

    # Get the clist
    with open(name + '_clist.json') as f:
        clist = json.load(f)

    # Build the model.
    text_model = markovify.Text(text)

    # Store recent words
    recent_words = []

    # Print randomly-generated sentences

    while True:
        sen = text_model.make_sentence()
        # input(sen)
        # Remove punctuation
        sen = re.sub(r'[^\w\s]','',sen)
        # Break our sentence into words
        words = sen.split(' ')
        # For each word, find corresponding clip in clist
        clips = []

        for word in words:
            # Shuffle clist
            shuffle(clist)
            for clip in clist:
                if clip['word'] == word:
                    clip['start'] = float(clip['start'])
                    clip['end'] = float(clip['end'])
                    clips.append(clip)
                    break   

        # Now iterate over our clips
        for clip in clips:
            ## Add period
            if clip is clips[-1]:
                clip['word'] += '.'

            # Get audio segment
            seg = recording[clip['start']*1000-50:clip['end']*1000+100]
        
            '''
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
            '''

            # seg = seg.fade(to_gain=-50.0, end=0, duration=100)

            # Play audio segment
            with tempfile.NamedTemporaryFile("w+b", suffix=".wav") as f:
                fileName = f.name

            seg.export(fileName, "wav")


            if (cap.isOpened()== False): 
                print("Error opening video stream or file")

            wave_obj = sa.WaveObject.from_wave_file(fileName)
            duration = len(seg) - 200
            play_obj = wave_obj.play()

            # Figure out recent words
            recent_words.append(clip['word'])
            while len(' '.join(recent_words)) > 22:
                recent_words.pop(0)

            cap.set(cv2.CAP_PROP_POS_FRAMES, fps * clip['start'])

            i = 0
            # Read until video is completed
            while(i < (duration * fps / 1000.0)):
                i += 1
                # Capture frame-by-frame
                ret, frame = cap.read()
                if ret == True:
                    # Display the resulting frame
                    # UofM blue = (76,39,0)
                    cv2.putText(frame, ' '.join(recent_words), (20, 670), cv2.FONT_HERSHEY_COMPLEX, 3, (0,0,0), 12, cv2.LINE_AA, False)
                    # UofM maize = (5,203,255)
                    cv2.putText(frame, ' '.join(recent_words), (20, 670), cv2.FONT_HERSHEY_COMPLEX, 3, (0,255,0), 3, cv2.LINE_AA, False)
                    cv2.imshow('Frame',frame)
                
                    # Press Q on keyboard to  exit
                    if cv2.waitKey(25) & 0xFF == ord('q'):  
                        break
                
                # Break the loop
                else: 
                    break

            os.remove(fileName)

if __name__ == '__main__':
    run(input("Enter filename for Markovization:"))