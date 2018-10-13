import io
import os

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.cloud import storage


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
    "start": 0,
    "end": 0,
    "word": ""
}

if not 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '.\\Markov Chains-06f4fd5f0bf6.json'

client = speech.SpeechClient()

infile = input('Enter filename: ')

file_name = os.path.join(os.path.dirname(__file__), 'resources', infile)


bucketname = 'markovid-1'

upload_blob(bucketname, file_name, infile)

audio = types.RecognitionAudio(uri=("gs://" + bucketname + "/" + infile))

config = types.RecognitionConfig(encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
                                 sample_rate_hertz=16000,
                                 language_code='en-US',
                                 enable_word_time_offsets=True,
                                 enable_automatic_punctuation=True)

operation = client.long_running_recognize(config, audio)

response = operation.result(timeout=90)
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

delete_blob(bucketname, infile)

