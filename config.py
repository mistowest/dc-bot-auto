# set the following variable to True to declare that you have modified the config
i_have_read_config = True



# ============================================================
# Auto-Close-Open
# ============================================================

force_decision = False  # TODO: replace by a command
forced_decision_should_close = True  # True = Close, False = Open

# ativa/desativa a função de fechar canais automaticamente em um horário
auto_close_enabled = True

# IDs dos canais que devem ser fechados/abertos automaticamente
# (independente da lista de whitelist/blacklist do slowmode acima)
auto_close_channels = [
    1351211786371727412,
    1109300761231364277,
    667873478816301076,
    1300455918294536233,
    1421887187720474684,
    1288538597959536671,
    923302800576876584,
    1514756380568064060,
    1301562765638631504,
    1313203227541373158,
    1177926846822760458,
    1181641632681037834,
    1361443500989747240,
    1409722950059561002,
    669653822179639346,
    1491881054460706826,
    833733705351692288,
    1499858270037475440,
    1499188660883558491,
    1402727568943218689,
    1518973653956689973,
    1489617887885918288,
    1150256995945947217,
    1159941233297330319,
    1297933226169602160,
    1098020288031101028,
    1296662094078279810,
    1512075420629991564,
    791805391646228520,
    1515108140360798218,
    1418250421277036544,
    1154870678336569435,
    1518965913574052042,
    1482098935601434725,
    780522428828483634,
    766645824033652747,
    1349792875847880776,
    773573600938426420,
    1500091803838320700,
    888570531627020360,
    1405952600125472799,
    1522959178543534270,
    791357275050606623,
    777203232077512706,
    1151556517951193118,
    924713357754380298,
    1477825436783349830,
    669267607785963530,
    1111348671355834508,
    1477343234568224891,
    855903918965522433,
    1487812046685737072,
    1491404197348905142,
    1520169029065638009,
    1164533341056405524,
    1164544738364493854,
    1512489576374075605,
    1145916634742128650,
    1145916320525848596,
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
channel_to_communicate = 1351211786371727412
auto_close_message = "🔒 O servidor foi fechado durante a madrugada e será aberto novamente às {end_hour}:00. Até lá, bons sonhos!"
auto_open_message = "🔓 O servidor foi reaberto! Divirtam-se e SE COMPORTEM!"




# ============================================================
# Auto-Slowmode
# ============================================================


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
