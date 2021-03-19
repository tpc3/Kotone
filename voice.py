import asyncio
import io
import subprocess
import tempfile
import zlib

import aiohttp
import discord
import gtts
import pymemcache
import ibm_watson
import ibm_cloud_sdk_core.authenticators

import kana

voice_aques = "aques"
voice_gtts = "gtts"
voice_watson = "watson"

# Load libs
kanaconv = kana.AllHiragana()


class Voice:
    def __init__(self, config, dev):
        self.config = config
        self.dev = dev
        self.cache_cli = pymemcache.client.base.Client(self.config["system"]["cache"])
        self.watson = ibm_watson.text_to_speech_v1.TextToSpeechV1(
            authenticator=ibm_cloud_sdk_core.authenticators.IAMAuthenticator(self.config["system"]["watson_api"]))
        self.watson.set_service_url(self.config["system"]["watson_url"])
        self.aiosession = aiohttp.ClientSession()

    async def get(self, message, lang, voice, uid):
        vtype = ""
        if voice == voice_aques:
            vtype = str(uid)[0]
        crc = zlib.crc32((message + lang + voice + vtype).encode("utf-8"))
        cache = self.cache_cli.get(str(crc))
        if cache is None:
            fp = io.BytesIO()
            fail = False
            audio_type = "mp3"
            if voice == voice_aques:
                fp.write(await self.send_request(self.config["system"]["aques_api"] + str(kana.uid_voice[int(vtype)]),
                                           kanaconv.tokana(message)))
                audio_type = "wav"
            elif voice == voice_gtts or fail is True:
                audio_type = "mp3"
                try:
                    gtts.gTTS(message, lang=lang).write_to_fp(fp)
                except gtts.gTTSError:
                    # Maybe 404. Just ignore
                    pass
            elif voice.startswith(voice_watson):
                audio_type = "ogg"
                fp.write(self.watson.synthesize(message, voice=voice.replace(voice_watson + "_", "")).get_result().content)
            fp.seek(0)
            r = ['ffmpeg', '-f', audio_type, '-i', 'pipe:', '-f', 'opus', '-application', 'voip', '-b:a', '32K', 'pipe:']
            process = subprocess.run(r, input=fp.read(), stderr=subprocess.PIPE if self.dev else subprocess.DEVNULL, stdout=subprocess.PIPE)
            if self.dev:
                print(process.stderr.decode("utf8"))
            if not self.dev:
                self.cache_cli.set(str(crc), process.stdout, 3600)
            cache = process.stdout
        with tempfile.TemporaryFile() as fp:
            fp.write(cache)
            fp.seek(0)
            t = discord.FFmpegOpusAudio(fp, pipe=True, bitrate=32, codec="copy")
        return t

    def check(self, voice, lang, id):
        if voice == voice_aques:
            if lang != "ja":
                return False
            else:
                return True
        elif voice == voice_gtts:
            if lang in gtts.tts.tts_langs():
                return True
            else:
                return False
        elif voice.startswith(voice_watson + "_"):
            l = voice.replace(voice_watson + "_", "")
            for i in self.watson.list_voices().get_result()["voices"]:
                if l == i["name"]:
                    return True
            return False

    async def send_request(self, url, data):
        request_body = {"text": data}
        async with self.aiosession.post(url, data=request_body) as response:
            if response.status == 200:
                return await response.read()
            else:
                raise RuntimeError("Server returned status " + str(response.status) + " with data '" + data + "'")

    def close_session(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.aiosession.close())