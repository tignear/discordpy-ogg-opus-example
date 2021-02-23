import discord
from opus_buffer_stream import OpusBufferStream
from itertools import chain


class _ShortItr():
    def __init__(self, data):
        self.data = data
        self.idx = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.idx == len(self.data):
            raise StopIteration()
        idx = self.idx
        self.idx += 2
        return (self.data[idx], self.data[idx+1])


class OggOpusAudioSource(discord.AudioSource):
    """

    Args:
        data (bytes): Must be binary data by bytes of ogg opus 48kHz(this class will not convert sampling rate).
    """

    def __init__(self, data):
        self.stream = OpusBufferStream(data)
        self.buf = bytearray()
        # 48000hz*2bytes*(channel_count=mono or stereo)*(20ms=20/1000s)
        self.output_size = 48000*2*self.stream.channels*20//1000

    def _load(self):
        if self.stream is None:
            return None
        buf = self.stream.get_buffer()
        if buf is None:
            return None
        self.buf += buf

    def read(self):
        while len(self.buf) < self.output_size:
            if self._load() is None:
                break
        r = self.buf[:self.output_size]
        del self.buf[:self.output_size]
        if self.stream.channels == 2:
            x = bytes(r)
        else:
            x = bytes(chain.from_iterable(
                [[a, b, a, b] for a, b in _ShortItr(r)]))
        return x

    def close(self):
        if self.stream is not None:
            self.stream.close()

    def is_opus(self):
        return False
