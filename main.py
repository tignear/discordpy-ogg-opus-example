import itertools
import discord
import os
from itertools import chain
from pyogg import OpusFileStream
from opusbuf import OpusBufferStream
import time
f = open('sound-mono.opus', 'rb')
d = f.read()
f.close()

class ShortItr():
    def __init__(self,data):
        self.data = data
        self.idx = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.idx == len(self.data):
            raise StopIteration()
        idx = self.idx
        self.idx+=2
        return (self.data[idx],self.data[idx+1])
class OggOpusAudioSource(discord.AudioSource):
    """

    Args:
        data (bytes): Must be binary data by bytes of ogg opus 48kHz(this class will not convert sampling rate).
    """

    def __init__(self, data):
        self.stream = OpusBufferStream(data)
        self.buf = bytearray()
        # 48000hz*2bytes*(channel_count=mono or stereo)*(20ms=20/1000s)
        print(self.stream.channels)
        self.output_size = 48000*2*self.stream.channels*20//1000

    def _load(self):
        if self.stream is None:
            return None
        buf = self.stream.get_buffer()
        if buf is None:
            return None
        self.buf += buf

    def read(self):
        s = time.perf_counter()
        while len(self.buf) < self.output_size:
            if self._load() is None:
                break
        r = self.buf[:self.output_size]
        del self.buf[:self.output_size]
        m = time.perf_counter()
        if self.stream.channels == 2:
            x = bytes(r)
        else:
            x = bytes(chain.from_iterable([[a,b,a,b] for a,b in ShortItr(r)]))
        e = time.perf_counter()
        print(e-s,e-m,m-s)
        return x
    def close(self):
        if self.stream is not None:
            self.stream.close()

    def is_opus(self):
        return False


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        voice_client = await self.get_channel(724182853633703986).connect()
        voice_client.play(OggOpusAudioSource(d))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))


client = MyClient()
client.run(os.getenv('DISCORD_BOT_TOKEN'))
