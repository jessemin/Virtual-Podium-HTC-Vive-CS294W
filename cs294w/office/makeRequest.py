import json
from io import BytesIO
from contextlib import closing

import wave
import pyaudio

import sys
sys.path.append('houndipy')

from houndipy import Client


class SendStream:

    def __init__(self, stream, rate, chunk_size, seconds):
        self.chunk_size = chunk_size
        self.seconds = seconds
        self.stream = stream
        self.rate = rate

    def __iter__(self):
        return iter(self.gen())

    def gen(self):
        print('starting')
        for i in range(0, int(self.rate / self.chunk_size * self.seconds)):
            yield self.stream.read(self.chunk_size)
        print('stopping')


def trim(snd_data):
    "Trim the blank spots at the start and end"
    def _trim(snd_data):
        snd_started = False
        r = array('h')

        for i in snd_data:
            if not snd_started and abs(i)>THRESHOLD:
                snd_started = True
                r.append(i)

            elif snd_started:
                r.append(i)
        return r

    # Trim to the left
    snd_data = _trim(snd_data)

    # Trim to the right
    snd_data.reverse()
    snd_data = _trim(snd_data)
    snd_data.reverse()
    return snd_data

def is_silent(snd_data):
    "Returns 'True' if below the 'silent' threshold"
    return max(snd_data) < THRESHOLD


def get_recording(seconds):
    CHUNK = 1024
    WIDTH = 2
    CHANNELS = 1
    RATE = 16000

    p = pyaudio.PyAudio()
    FORMAT = p.get_format_from_width(WIDTH)

    with closing(p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)) as stream:

        print("* recording")

        frames = [
            stream.read(CHUNK)
            for _ in range(0, int(RATE / CHUNK * seconds))
        ]
        print("* done recording")

    p.terminate()

    file = BytesIO()
    wf = wave.open(file, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))

    return file.getvalue()


def main():
    with open('auth.json') as fh:
        auth = json.load(fh)
    client = Client(
        auth['client_id'],
        auth['client_key']
    )

    #r = client.text('how old is chad reed')
    data = get_recording(seconds=10)
    print('sending')
    r = client.speech(data)
    print('sent')

    if not r.ok:
        print(r.text)

    r.raise_for_status()

    res = r.json()

    try:
        for sres in res['AllResults']:
            print(sres['NativeData']['LongResult'])
    except KeyError:
        from pprint import pprint
        pprint(res)

if __name__ == '__main__':
    main()
