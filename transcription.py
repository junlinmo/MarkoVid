import io
import os
import json
import re

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.cloud import storage

import markovize

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))

def delete_blob(bucket_name, blob_name):
    """Deletes a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.delete()

    print('Blob {} deleted.'.format(blob_name))


clip = {
    'start': 0,
    'end': 0,
    'word': ''
}

if not 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '.\\Markov Chains-06f4fd5f0bf6.json'

client = speech.SpeechClient()

infile = input('Enter filename for transcription: ')
name = infile[:-4]

file_name = os.path.join(os.path.dirname(__file__), 'resources', infile)

statinfo = os.stat(file_name)
if statinfo.st_size > 100000000:
    print('File too large! The limit is 100MB')
    exit()


bucketname = 'markovid-1'

upload_blob(bucketname, file_name, infile)

audio = types.RecognitionAudio(uri=('gs://' + bucketname + '/' + infile))

config = types.RecognitionConfig(encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
                                 sample_rate_hertz=16000,
                                 language_code='en-US',
                                 enable_word_time_offsets=True,
                                 enable_automatic_punctuation=True)

operation = client.long_running_recognize(config, audio)

response = operation.result(timeout=9000)
s = ''

clist = []

for i, result in enumerate(response.results):
        alternative = result.alternatives[0]
        s += alternative.transcript

        for word_info in alternative.words:
            word = re.sub(r'[^\w\s]','',word_info.word)
            start_time = word_info.start_time
            end_time = word_info.end_time
            clist.append({'start':start_time.seconds + start_time.nanos * 1e-9, 'end':end_time.seconds + end_time.nanos * 1e-9, 'word':word})


delete_blob(bucketname, infile)

# Export clist to json

with open(name + '_clist.json', 'w') as outfile:
    json.dump(clist, outfile)

# Export transcript to txt

with open(name + '_transcript.txt', 'w') as outfile:
    outfile.write(s)

# Call markovize

# input("Press any key to Markovize:")

markovize.run(infile)
