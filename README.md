# discord-auto-slowmode
A customisable bot that automatically enables slowmode in individual channels if they see an influx in activity.

## Fechamento automático de canais

Além do slowmode automático, o bot agora também pode **fechar** (impedir o envio de mensagens)
canais específicos durante um horário definido, e reabri-los automaticamente depois.

Isso é feito editando a permissão `send_messages` do cargo `@everyone` no canal — ou seja, o canal
continua visível, mas ninguém consegue mandar mensagem nele até o horário de reabertura.

### Como configurar

No `config.py`, na seção `Fechamento automático de canais`:

```python
# ativa/desativa a função
auto_close_enabled = True

# IDs dos canais que serão fechados/abertos automaticamente
# (essa lista é separada da whitelist/blacklist do slowmode)
auto_close_channels = [
    123456789012345678,
    987654321098765432
]

# hora que os canais fecham (0 a 23) — 0 = meia-noite
auto_close_start_hour = 0

# hora que os canais abrem novamente (0 a 23) — 6 = 06:00
auto_close_end_hour = 6

# fuso horário usado para calcular a hora atual
auto_close_timezone = "America/Sao_Paulo"

# frequência (segundos) de verificação
auto_close_check_frequency = 30
```

Apenas os canais listados em `auto_close_channels` são afetados por essa função — os demais
canais do servidor continuam funcionando normalmente, mesmo durante o horário de fechamento.

### Requisitos

O bot precisa da permissão **Gerenciar Canais / Manage Channels** no servidor para poder alterar
as permissões dos canais listados.

Instale as dependências com:

```bash
pip install -r requirements.txt
```
