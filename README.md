# Bot de Wallpapers para Discord

Um bot para Discord que envia wallpapers automaticamente e responde a comandos para buscar wallpapers de diferentes fontes.

## Funcionalidades

- **Envio automático**: Envia wallpapers populares do Wallhaven a cada hora
- **Comando `!aura`**: Busca wallpapers do subreddit r/wallpapers
- **Comando `!auraanime`**: Busca wallpapers de anime dos subreddits r/Animewallpaper e r/Animewallpapers
- **Comando `!engine`**: Mostra links para sites de wallpapers animados para Wallpaper Engine
- **Filtros inteligentes**: Garante resolução mínima de 1920x1080, formato horizontal e tamanho máximo de 8MB
- **Sistema anti-repetição**: Evita enviar o mesmo wallpaper repetidamente

## Configuração

### 1. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Token do bot Discord
TOKEN=seu_token_do_discord_aqui

# ID do canal onde o bot enviará wallpapers automaticamente
CHANNEL_ID=id_do_canal_aqui

# Credenciais do Reddit (para comandos !aura e !auraanime)
REDDIT_CLIENT_ID=seu_client_id_do_reddit
REDDIT_CLIENT_SECRET=seu_client_secret_do_reddit
REDDIT_USERNAME=seu_usuario_do_reddit
REDDIT_PASSWORD=sua_senha_do_reddit
REDDIT_USER_AGENT=seu_user_agent_do_reddit

# API Key do Wallhaven (para envio automático)
WALLHAVEN_API_KEY=sua_api_key_do_wallhaven
```

### 2. Como obter as credenciais

#### Discord Bot Token
1. Acesse [Discord Developer Portal](https://discord.com/developers/applications)
2. Crie uma nova aplicação
3. Vá para "Bot" e copie o token

#### Reddit API
1. Acesse [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Crie uma nova aplicação (script)
3. Copie o Client ID e Client Secret

#### Wallhaven API Key
1. Acesse [Wallhaven](https://wallhaven.cc/settings/account)
2. Vá para "API" e gere uma nova chave

### 3. Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/nome-do-repositorio.git
cd nome-do-repositorio

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
# (crie o arquivo .env conforme mostrado acima)

# Execute o bot
python bot.py
```

## Comandos

- `!aura` - Envia um wallpaper do r/wallpapers
- `!auraanime` - Envia um wallpaper de anime
- `!engine` - Mostra links para sites de wallpapers animados

## Deploy na Nuvem

### Railway (Recomendado)

1. Faça fork deste repositório
2. Acesse [Railway](https://railway.app/)
3. Conecte sua conta GitHub
4. Clique em "New Project" → "Deploy from GitHub repo"
5. Selecione o repositório
6. Configure as variáveis de ambiente no painel do Railway
7. O bot será deployado automaticamente

### Outras opções
- **Heroku**: Use o Procfile fornecido
- **Replit**: Importe o repositório e configure as variáveis
- **VPS**: Execute diretamente no servidor

## Estrutura do Projeto

```
├── bot.py              # Código principal do bot
├── requirements.txt    # Dependências Python
├── README.md          # Este arquivo
├── .gitignore         # Arquivos ignorados pelo Git
├── .env               # Variáveis de ambiente (não commitado)
└── wallpapers/        # Pasta para wallpapers temporários
```

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## Suporte

Se você encontrar algum problema ou tiver dúvidas, abra uma issue no GitHub. 