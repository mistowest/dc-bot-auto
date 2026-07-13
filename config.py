# set the following variable to True to declare that you have modified the config
i_have_read_config = False

# replace with the private token of your bot, do not share this with anyone
bot_token = "###########################################################"

# minimum amount of seconds between check
# e.g. compare amount of messages sent in channel within past 30 seconds
check_frequency = 30

# determine amount of messages per check_frequency required for each slowmode band
# slowmode_delay must be an integer ranging from 0-21600 seconds
time_configs = {
    # message_frequency: slowmode_delay
    0: 0,
    30: 1,
    60: 3,
    90: 5,
    120: 10
}

# choose whether channels must be whitelisted for auto-slowmode to run there
channel_whitelisting_enabled = True

# ids of channels that auto slowmode will run in
# ignored if channel whitelisting is disabled
whitelisted_channels = [
    00000000000000000,
    00000000000000000
]

# blacklisted channels ids
# if whitelisting is disabled, the bot will ignore channels with these ids
blacklisted_channels = [
    00000000000000000,
    00000000000000000
]


# ============================================================
# Fechamento automático de canais (auto close/open)
# ============================================================

# ativa/desativa a função de fechar canais automaticamente em um horário
auto_close_enabled = True

# IDs dos canais que devem ser fechados/abertos automaticamente
# (independente da lista de whitelist/blacklist do slowmode acima)
auto_close_channels = [
    00000000000000000,
    00000000000000000
]

# hora em que os canais listados acima devem FECHAR (0 a 23)
# 0 = meia-noite (00:00)
auto_close_start_hour = 0

# hora em que os canais listados acima devem ABRIR novamente (0 a 23)
# 6 = 06:00
auto_close_end_hour = 6

# fuso horário usado para calcular o horário atual
# lista de nomes válidos: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
auto_close_timezone = "America/Sao_Paulo"

# frequência (em segundos) com que o bot verifica se deve fechar/abrir os canais
auto_close_check_frequency = 30

# mensagens enviadas no canal quando ele é fechado/aberto
# defina como None para não enviar nenhuma mensagem
auto_close_message = "🔒 Este canal foi fechado automaticamente e será reaberto às {end_hour}:00."
auto_open_message = "🔓 Este canal foi reaberto automaticamente."
