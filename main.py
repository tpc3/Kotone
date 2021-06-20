import asyncio
import configparser
import re
import traceback
import threading

import discord
import redis

import voice
import strings

# Text channels
on_vc = {}
# Queues per guild
queue = {}
# Lock
lock = {}

# Config
config = configparser.ConfigParser()
config.read(strings.config_ini)
redis_config = redis.Redis(host=config[strings.Configs.System.system]["db"], port=int(config[strings.Configs.System.system][strings.Configs.System.db_port]),
                           decode_responses=True, db=int(config[strings.Configs.System.system][strings.Configs.System.db_num]))

if config[strings.Configs.System.system]["dev"].lower() in ("true", "yes"):
    print(strings.Messages.dev)
    redis_config.config_set("save", "")
    redis_config.config_set("appendonly", "no")
    dev = True
else:
    redis_config.config_set("save", "60 1")
    redis_config.config_set("appendonly", "yes")
    dev = False
emoji = re.compile("<:.*?:.*?>", flags=re.M)
voice_obj = voice.Voice(config, dev)

# Force-ignore dict
ignore = []
for i in [r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", r"\|\|.*?\|\|"]:
    ignore.append(re.compile(i, flags=re.M))


def db_config(gid, key):
    r = redis_config.get(str(gid) + "_" + key)
    if r is None:
        return config["default"][key]
    else:
        return r


def msg(locale, message, color=discord.Colour.dark_blue()):
    return discord.Embed(title=message.capitalize(), description=get_str(locale, message), color=color)


def msg_conf(gid, lang):
    embed = discord.Embed(title="Config", description=get_str(lang, strings.Configs.Lang.config_list), color=discord.Colour.dark_blue())
    for i in ["prefix", "lang", "limit", "voice", "bots", "default"]:
        embed.add_field(name=get_str(lang, i), value=db_config(gid, i))
    return embed


def msg_dict(title, lang, gid, page):
    embed = discord.Embed(title=title.capitalize(), description=get_str(lang, title), color=discord.Colour.dark_blue())
    scope = (page - 1) * 10
    for k, v in list(redis_config.hgetall(str(gid) + "_" + title).items())[scope:scope + 10]:
        embed.add_field(name=k, value=v)
    return embed


def msg_help(lang, prefix):
    embed = discord.Embed(title="help", description=get_str(lang, "help"), color=discord.Colour.dark_blue())
    embed.set_author(name=client.user.display_name, url=config[strings.Configs.System.system]["url"], icon_url=str(client.user.avatar_url))
    for i in ["join", "leave", "ping"]:
        embed.add_field(name=prefix + i, value=get_str(lang, i), inline=False)
    embed.add_field(name=prefix + "config", value=get_str(lang, strings.Configs.Lang.help_config).replace("PREFIX ", prefix), inline=False)
    return embed


def get_str(locale, message):
    try:
        c = config[locale][message]
    except KeyError:
        c = config["en"][message]
    return c


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        await client.change_presence(activity=discord.Game(name='.help'))

    async def on_guild_remove(self, guild):
        for i in ["prefix", "lang", "replace", "limit", "voice", "bots", "list", "default"]:
            redis_config.delete(str(guild.id) + "_" + i)

    async def on_voice_state_update(self, member, before, after):
        global on_vc
        if member.guild.voice_client is not None:
            if (member == client.user) and before.channel and after.channel and (before.channel != after.channel):
                await member.guild.voice_client.move_to(None)
                del on_vc[member.guild.id]
            elif len(member.guild.voice_client.channel.members) == 1:
                await member.guild.voice_client.disconnect()
                del on_vc[member.guild.id]
            elif len(member.guild.voice_client.channel.members) != 0:
                allbot = True
                for i in member.guild.voice_client.channel.members:
                    if not i.bot:
                        allbot = False
                        break
                if allbot:
                    await member.guild.voice_client.disconnect()
                    del on_vc[member.guild.id]

    async def on_message(self, message):
        global on_vc
        global queue
        if message.author == client.user or message.guild is None or message.content == "":
            return
        prefix = db_config(message.guild.id, "prefix")
        if message.channel.id not in on_vc.values():
            if not message.content.startswith(prefix):
                return
        elif message.guild.voice_client is None:
            # ?????
            del on_vc[message.guild.id]
            queue[message.guild.id] = [[]]
        lang = db_config(message.guild.id, "lang")
        if message.content == prefix + "join":
            if (not message.author.voice) or (not message.author.voice.channel) or (message.guild.voice_client):
                return
            await message.author.voice.channel.connect()
            await message.guild.change_voice_state(channel=message.author.voice.channel, self_deaf=True, self_mute=True)
            on_vc[message.guild.id] = message.channel.id
            await message.add_reaction("✋")
            return

        if message.content == prefix + "leave":
            if message.guild.voice_client is None or message.channel.id not in on_vc.values():
                return
            await message.guild.voice_client.disconnect()
            del on_vc[message.guild.id]
            await message.add_reaction("👋")
            return

        if message.content == prefix + "ping":
            await message.channel.send(embed=msg(lang, "ping"))
            await message.add_reaction("🏓")
            return

        if message.content == prefix + "help":
            await message.channel.send(embed=msg_help(lang, prefix))
            return

        if message.content == prefix + "skip":
            if message.guild.voice_client.is_playing():
                message.guild.voice_client.stop()
                await message.add_reaction("⏩")
            return

        if message.content.startswith(prefix + "config"):
            req = message.content.split()
            if len(req) == 1:
                await message.channel.send(embed=msg_conf(message.guild.id, lang))
            elif len(req) == 3 and req[1] in ["prefix", "lang", "limit", "voice", "bots", "default"]:
                key = str(message.guild.id) + "_" + req[1]
                # Check config
                if req[1] == "lang" and not voice_obj.check(db_config(message.guild.id, "voice"), req[2],message.guild.id):
                    await message.channel.send(embed=msg(lang, strings.Configs.Lang.config_error, color=discord.Colour.red()))
                elif req[1] == "voice":
                    try:
                        result = voice_obj.check(req[2], db_config(message.guild.id, "lang"),message.guild.id)
                    # gTTS error
                    except (ValueError, AttributeError):
                        await message.channel.send(embed=msg(lang, strings.Configs.Lang.error_voice, color=discord.Colour.red()))
                        return
                    if result:
                        redis_config.set(key, req[2])
                        await message.add_reaction("👍")
                    else:
                        await message.channel.send(embed=msg(lang, strings.Configs.Lang.config_error, color=discord.Colour.red()))
                elif req[1] == "bots" and req[2] not in ["true", "false"]:
                    await message.channel.send(embed=msg(lang, strings.Configs.Lang.config_error, color=discord.Colour.red()))
                elif req[1] == "default" and req[2] not in ["allow", "deny"]:
                    await message.channel.send(embed=msg(lang, strings.Configs.Lang.config_error, color=discord.Colour.red()))
                elif req[1] == "limit":
                    try:
                        i = int(req[2])
                        if i < 0 or i > 2000:
                            raise ValueError
                        else:
                            redis_config.set(key, req[2])
                            await message.channel.send(embed=msg(lang, "config"))
                    except:
                        await message.channel.send(embed=msg(lang, strings.Configs.Lang.config_error, color=discord.Colour.red()))
                else:
                    redis_config.set(key, req[2])
                    await message.add_reaction("👍")

            elif req[1] == "replace":
                if len(req) == 4:
                    key = str(message.guild.id) + "_" + req[1]
                    if req[2] == "del":
                        redis_config.hdel(key, req[3])
                    else:
                        redis_config.hset(key, req[2], req[3])
                    await message.add_reaction("👍")
                elif len(req) == 2:
                    await message.channel.send(embed=msg_dict(req[1], lang, message.guild.id, 1))
                elif len(req) == 3:
                    try:
                        page = int(req[2])
                    except ValueError:
                        page = 1
                    await message.channel.send(embed=msg_dict(req[1], lang, message.guild.id, page))

            if len(req) >= 2 and req[1] == "list":
                if len(message.mentions) == 1:
                    key = str(message.guild.id) + "_" + req[1]
                    if len(req) == 4:
                        if req[2] == "del":
                            redis_config.hdel(key, message.mentions[0].id)
                            await message.add_reaction("👍")
                    elif len(req) == 3:
                        redis_config.hset(key, message.mentions[0].id, message.mentions[0].name)
                        await message.add_reaction("👍")
                elif len(req) == 2:
                    await message.channel.send(embed=msg_dict(req[1], lang, message.guild.id, 1))
                elif len(req) == 3:
                    try:
                        page = int(req[2])
                    except ValueError:
                        page = 1
                    await message.channel.send(embed=msg_dict(req[1], lang, message.guild.id, page))
            return

        # Early return if bots
        if db_config(message.guild.id, "bots") == "false" and message.author.bot or message.content.startswith(prefix):
            return

        if db_config(message.guild.id, "default") == "allow":
            for k, v in redis_config.hgetall(str(message.guild.id) + "_" + "list").items():
                if k == str(message.author.id):
                    return
        if db_config(message.guild.id, "default") == "deny":
            allow = False
            for k, v in redis_config.hgetall(str(message.guild.id) + "_" + "list").items():
                if k == str(message.author.id):
                    allow = True
                    break
            if not allow:
                return

        if message.channel.id in on_vc.values():
            content = discord.utils.escape_mentions(message.clean_content)
            limit = int(db_config(message.guild.id, "limit"))
            for k, v in redis_config.hgetall(str(message.guild.id) + "_" + "replace").items():
                content = re.sub(k, v, content)
            if emoji.search(content) is not None:
                content = re.sub(emoji, "", content)
                await message.channel.send(embed=msg(lang, strings.Configs.Lang.warn_emoji, color=discord.Colour.red()))
            for i in ignore:
                content = re.sub(i, "", content)
            content = content.strip()[:limit]
            if message.guild.id not in queue:
                queue[message.guild.id] = [[content, message.author.id]]
            else:
                queue[message.guild.id].append([content, message.author.id])
            if message.guild.id not in lock:
                lock[message.guild.id] = threading.Lock()
            if not lock[message.guild.id].locked():
                lock[message.guild.id].acquire()
                while queue[message.guild.id]:
                    await message.guild.change_voice_state(channel=message.guild.voice_client.channel, self_mute=False,
                                                           self_deaf=True)
                    try:
                        if queue[message.guild.id][0][0] != "":
                            message.guild.voice_client.play(
                                await voice_obj.get(queue[message.guild.id][0][0], lang, db_config(message.guild.id, "voice"),
                                              queue[message.guild.id][0][1]))
                    except:
                        traceback.print_exc(chain=True)
                        await message.channel.send(embed=msg(lang, strings.Configs.Lang.error_voice, color=discord.Colour.red()))
                    finally:
                        del queue[message.guild.id][0]
                        while message.guild.voice_client.is_playing():
                            await asyncio.sleep(1)
                        await message.guild.change_voice_state(channel=message.guild.voice_client.channel,
                                                               self_mute=True, self_deaf=True)
                lock[message.guild.id].release()


intents = discord.Intents.default()
intents.members = True
client = MyClient(intents=intents)
try:
    client.run(config["system"]["token"])
except:
    traceback.print_exc(chain=True)
finally:
    voice_obj.close_session()
    if not dev:
        print("Stopped server,Saving configs in background...")
        redis_config.bgsave()
