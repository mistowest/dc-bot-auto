# discord-auto-slowmode by JoshSCF (joshl.io)

import config, discord, time
from datetime import datetime
from zoneinfo import ZoneInfo
from discord.ext import tasks

intents = discord.Intents.default()
client = discord.Client(intents=intents)

message_cache = {}
previous_delays = {}
last_updated = 0

# guarda o estado original da permissão send_messages (para @everyone) de cada
# canal fechado, para poder restaurar exatamente como estava ao reabrir
closed_channels_state = {}


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

    # iterate through cache and fetch new delay times
    for channel_id in message_cache.keys():
        delay = get_delay(message_cache[channel_id])

        # if delay is the same as previous delay, skip iteration
        if channel_id in previous_delays.keys():
            if previous_delays[channel_id] == delay:
                new_channel_delays[channel_id] = delay
                continue
        
        # edit channel slowmode and update new_channel_delays
        channel = client.get_channel(channel_id)
        await channel.edit(slowmode_delay=delay)
        new_channel_delays[channel_id] = delay

    
    # reset message cache and update last_updated & previous_delays
    message_cache = {}
    last_updated = time.time()
    previous_delays = new_channel_delays


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

    # guarda o valor original de send_messages para poder restaurar depois
    closed_channels_state[channel.id] = overwrite.send_messages

    overwrite.send_messages = False
    await channel.set_permissions(channel.guild.default_role, overwrite=overwrite)

    if config.auto_close_message:
        try:
            msg = config.auto_close_message.format(end_hour=config.auto_close_end_hour)
            await channel.send(msg)
        except discord.Forbidden:
            pass


async def open_channel(channel):
    global closed_channels_state
    overwrite = channel.overwrites_for(channel.guild.default_role)

    # restaura o valor original de send_messages (True/False/None)
    original_value = closed_channels_state.pop(channel.id, None)
    overwrite.send_messages = original_value

    # se o overwrite ficou vazio (todos os valores None), remove ele
    if overwrite.is_empty():
        await channel.set_permissions(channel.guild.default_role, overwrite=None)
    else:
        await channel.set_permissions(channel.guild.default_role, overwrite=overwrite)

    if config.auto_open_message:
        try:
            await channel.send(config.auto_open_message)
        except discord.Forbidden:
            pass


@tasks.loop(seconds=config.auto_close_check_frequency)
async def auto_close_task():
    should_be_closed = is_within_close_window()

    for channel_id in config.auto_close_channels:
        channel = client.get_channel(channel_id)
        if channel is None:
            continue

        is_closed = channel_id in closed_channels_state

        if should_be_closed and not is_closed:
            await close_channel(channel)
        elif not should_be_closed and is_closed:
            await open_channel(channel)


@auto_close_task.before_loop
async def before_auto_close_task():
    await client.wait_until_ready()


@client.event
async def on_ready():
    if config.auto_close_enabled and not auto_close_task.is_running():
        auto_close_task.start()
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    global last_updated, message_cache
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


if not config.i_have_read_config:
    # user has not read config file, don't start code
    print("You must modify config.py before running!")
    input("Press enter to continue...")
    exit()

client.run(config.bot_token)
