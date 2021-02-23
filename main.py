import discord
import os
from opus_aduio_source import OggOpusAudioSource
f = open('sound-mono.opus', 'rb')
d = f.read()
f.close()


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        voice_client = await self.get_channel(724182853633703986).connect()
        voice_client.play(OggOpusAudioSource(d))


client = MyClient()
client.run(os.getenv('DISCORD_BOT_TOKEN'))
