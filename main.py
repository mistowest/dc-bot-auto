# pip install discord
# pip install tzdata
import config, discord, time
import json
import os
import sys

from datetime import datetime
from zoneinfo import ZoneInfo
from discord.ext import tasks

intents = discord.Intents.default()
client = discord.Client(intents=intents)

message_cache = {}
previous_delays = {}
last_updated = 0

is_closed = False


# ============================================================
# Auto-close-open
# ============================================================

STATE_FILE = "closed_channels_state.json"

def load_closed_channels_state():
    if not os.path.exists(STATE_FILE):
        return {}

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # JSON stores dict keys as strings
        return {int(k): v for k, v in data.items()}

    except (OSError, json.JSONDecodeError):
        return {}


def save_closed_channels_state():
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(closed_channels_state, f, indent=4)
    except OSError as e:
        print(f"Failed to save channel state: {e}")


# guarda o estado original da permissão send_messages (para @everyone) de cada
# canal fechado, para poder restaurar exatamente como estava ao reabrir
closed_channels_state = load_closed_channels_state()


def is_within_close_window():
    # determina se o horário atual (no fuso configurado) está dentro da
    # janela de fechamento definida em config.py, tratando corretamente
    # o caso de a janela cruzar a meia-noite (ex: 22h às 6h)
    tz = ZoneInfo(config.auto_close_timezone)
    now_hour = datetime.now(tz).hour

    start = config.auto_close_start_hour
    end = config.auto_close_end_hour

    if start == end:
        # janela de 24h (sempre fechado) se start == end
        return True
    elif start < end:
        return start <= now_hour < end
    else:
        # janela cruza a meia-noite, ex: 22 -> 6
        return now_hour >= start or now_hour < end


async def close_channel(channel):
    global closed_channels_state
    overwrite = channel.overwrites_for(channel.guild.default_role)

    if isinstance(channel, discord.VoiceChannel):
        new_state = {"connect": overwrite.connect, "send_messages": overwrite.send_messages}
        overwrite.connect = False
        overwrite.send_messages = False
    elif isinstance(channel, (discord.TextChannel, discord.ForumChannel)):
        new_state = {"send_messages": overwrite.send_messages}
        overwrite.send_messages = False
    else:
        print("unsupported: ", channel)
        return

    try:
        await channel.set_permissions(channel.guild.default_role, overwrite=overwrite)
    except (discord.Forbidden, discord.HTTPException) as e:
        print(f"Failed to close channel {channel.id}: {e}")
        return  # don't record state for a change that didn't happen

    closed_channels_state[channel.id] = new_state
    save_closed_channels_state()


async def open_channel(channel):
    global closed_channels_state

    overwrite = channel.overwrites_for(channel.guild.default_role)
    original = closed_channels_state.get(channel.id, {})

    if isinstance(channel, discord.VoiceChannel):
        overwrite.connect = original.get("connect")
        overwrite.send_messages = original.get("send_messages")
    elif isinstance(channel, (discord.TextChannel, discord.ForumChannel)):
        overwrite.send_messages = original.get("send_messages")
    else:
        print("unsupported: ", channel)
        return

    try:
        if overwrite.is_empty():
            await channel.set_permissions(channel.guild.default_role, overwrite=None)
        else:
            await channel.set_permissions(channel.guild.default_role, overwrite=overwrite)
    except (discord.Forbidden, discord.HTTPException) as e:
        print(f"Failed to reopen channel {channel.id}: {e}")
        return  # state is untouched, will retry next loop

    closed_channels_state.pop(channel.id, None)
    save_closed_channels_state()


@tasks.loop(seconds=config.auto_close_check_frequency)
async def auto_close_task():
    global is_closed

    previous_closed_state = is_closed

    if config.force_decision:
        should_be_closed = config.forced_decision_should_close
    else:
        should_be_closed = is_within_close_window()

    for channel_id in config.auto_close_channels:
        channel = client.get_channel(channel_id)
        if channel is None:
            continue

        if config.force_decision:
            if should_be_closed:
                await close_channel(channel)
            else:
                await open_channel(channel)
        else:
            currently_closed = channel_id in closed_channels_state
            if should_be_closed and not currently_closed:
                await close_channel(channel)
            elif not should_be_closed and currently_closed:
                await open_channel(channel)
    
    # NOTIFY ON ONE CHANNEL
    is_closed = should_be_closed
    if previous_closed_state != is_closed: # State changed
        channel_to_msg = client.get_channel(config.channel_to_communicate)
        try:
            if should_be_closed:
                msg = config.auto_close_message.format(
                    end_hour=config.auto_close_end_hour
                )
                await channel_to_msg.send(msg)
            else:
                await channel_to_msg.send(config.auto_open_message)
        except discord.Forbidden:
            pass

    if config.force_decision:
        await client.close()
        sys.exit()


@auto_close_task.error
async def auto_close_task_error(error):
    print(f"auto_close_task crashed: {error}")
    # optional: restart it
    if not auto_close_task.is_running():
        auto_close_task.restart()

@auto_close_task.before_loop
async def before_auto_close_task():
    await client.wait_until_ready()


@client.event
async def on_ready():
    if config.auto_close_enabled and not auto_close_task.is_running():
        auto_close_task.start()
    print(f"Logged in as {client.user}")



# ============================================================
# Auto-slowmode
# ============================================================

def get_delay(message_count):
    # get message limits in descending order, compare with message count
    message_limits = sorted(config.time_configs.keys(), reverse=True)

    for limit in message_limits:
        if message_count >= limit:
            # return delay determined in config
            return config.time_configs[limit]
    
    # if nothing already returned, return a slowmode delay of 0
    return 0


async def update_slowmode():
    global last_updated, message_cache, previous_delays
    new_channel_delays = {}

    for channel_id in message_cache.keys():
        delay = get_delay(message_cache[channel_id])
        if previous_delays.get(channel_id) == delay:
            new_channel_delays[channel_id] = delay
            continue

        channel = client.get_channel(channel_id)
        if channel is None:
            continue
        try:
            await channel.edit(slowmode_delay=delay)
            new_channel_delays[channel_id] = delay
        except (discord.Forbidden, discord.HTTPException) as e:
            print(f"Failed to set slowmode on {channel_id}: {e}")
            new_channel_delays[channel_id] = previous_delays.get(channel_id, 0)

    
    # reset message cache and update last_updated & previous_delays
    message_cache = {}
    last_updated = time.time()
    previous_delays = new_channel_delays


@client.event
async def on_message(message):
    global last_updated, message_cache
    if message.author.bot:
        return

    channel_id = message.channel.id

    # update slowmode if it has been x seconds since last update
    if time.time() >= last_updated + config.check_frequency:
        await update_slowmode()
    
    # ignore message if channel blacklisted or not whitelisted
    if config.channel_whitelisting_enabled:
        if channel_id not in config.whitelisted_channels:
            return
    else:
        if channel_id in config.blacklisted_channels:
            return

    # add channel id to cache if not already added
    if message.channel.id not in message_cache.keys():
        message_cache[channel_id] = 1
        return
    
    # increase message count by 1 for channel if cache exists
    message_cache[channel_id] += 1


# ============================================================
# Init
# ============================================================

if not config.i_have_read_config:
    # user has not read config file, don't start code
    print("You must modify config.py before running!")
    input("Press enter to continue...")
    exit()


if len(sys.argv) < 2:
    print("Usage: python bot.py <bot_token>")
    sys.exit(1)

bot_token = sys.argv[1]

client.run(bot_token)
