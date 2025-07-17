import discord
import os
import random
import asyncio
import requests
import praw
import shutil
from discord.ext import commands
from bs4 import BeautifulSoup

# Debug: Verificar se as variáveis estão sendo lidas
print("=== DEBUG: Verificando variáveis de ambiente ===")
print(f"TOKEN: {'CONFIGURADO' if os.environ.get('TOKEN') else 'NÃO CONFIGURADO'}")
print(f"CHANNEL_ID: {os.environ.get('CHANNEL_ID', 'NÃO CONFIGURADO')}")
print(f"REDDIT_CLIENT_ID: {'CONFIGURADO' if os.environ.get('REDDIT_CLIENT_ID') else 'NÃO CONFIGURADO'}")
print(f"WALLHAVEN_API_KEY: {'CONFIGURADO' if os.environ.get('WALLHAVEN_API_KEY') else 'NÃO CONFIGURADO'}")
print("================================================")

# Insira o token do seu bot aqui
TOKEN = os.environ.get('TOKEN')
# ID do canal onde o bot vai enviar os wallpapers
CHANNEL_ID = int(os.environ.get('CHANNEL_ID', '0'))
# Intervalo em segundos entre cada envio (exemplo: 3600 = 1 hora)
INTERVALO = 3600
# Pasta onde estão os wallpapers
PASTA_WALLPAPERS = 'wallpapers'

# Credenciais do Reddit
REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET')
REDDIT_USERNAME = os.environ.get('REDDIT_USERNAME')
REDDIT_PASSWORD = os.environ.get('REDDIT_PASSWORD')
REDDIT_USER_AGENT = os.environ.get('REDDIT_USER_AGENT')

MAX_DISCORD_FILE_SIZE = 8 * 1024 * 1024  # 8 MB
MAX_TENTATIVAS = 10

if not os.path.exists(PASTA_WALLPAPERS):
    os.makedirs(PASTA_WALLPAPERS)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Lista para evitar repetição de wallpapers
ULTIMOS_WALLPAPERS = []
ULTIMOS_WALLPAPERS_ANIME = []
MAX_ULTIMOS = 20

def get_valid_posts(posts, min_width=1920, min_height=1080):
    valid = []
    for post in posts:
        try:
            if hasattr(post, 'preview'):
                images = post.preview.get('images', [])
                if images:
                    source = images[0]['source']
                    width = source['width']
                    height = source['height']
                    if width >= min_width and height >= min_height and width >= height:
                        valid.append(post)
        except Exception:
            continue
    return valid

# Função para buscar wallpaper sem repetir
def get_random_wallpaper_url(subreddit_name='wallpapers', ultimos=None):
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD
    )
    subreddit = reddit.subreddit(subreddit_name)
    posts = [post for post in subreddit.top(time_filter='month', limit=50) if post.url.endswith(('.jpg', '.png'))]
    posts = get_valid_posts(posts)
    # Evitar repetição máxima: só repetir se todos já foram usados
    if ultimos is not None:
        posts_sem_repetidos = [post for post in posts if post.url not in ultimos]
        if posts_sem_repetidos:
            posts = posts_sem_repetidos
        else:
            # Resetar lista se todos já foram usados
            ultimos.clear()
    if posts:
        post = random.choice(posts)
        return post.url
    return None

# Função para buscar wallpaper de anime sem repetir

def get_random_anime_wallpaper_url():
    subreddits = ['Animewallpaper', 'Animewallpapers']
    all_posts = []
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD
    )
    for sub in subreddits:
        subreddit = reddit.subreddit(sub)
        posts = [post for post in subreddit.top(time_filter='month', limit=30) if post.url.endswith(('.jpg', '.png'))]
        posts = get_valid_posts(posts)
        all_posts.extend(posts)
    # Evitar repetição máxima: só repetir se todos já foram usados
    posts_sem_repetidos = [post for post in all_posts if post.url not in ULTIMOS_WALLPAPERS_ANIME]
    if posts_sem_repetidos:
        posts = posts_sem_repetidos
    else:
        ULTIMOS_WALLPAPERS_ANIME.clear()
        posts = all_posts
    if posts:
        post = random.choice(posts)
        return post.url
    return None

WALLHAVEN_API_KEY = os.environ.get('WALLHAVEN_API_KEY')

def get_wallhaven_popular_wallpaper():
    url = (
        'https://wallhaven.cc/api/v1/search?'
        'categories=100&purity=100&atleast=1920x1080&ratios=16x9&sorting=toplist&order=desc'
        f'&apikey={WALLHAVEN_API_KEY}'
    )
    response = requests.get(url)
    data = response.json()
    if data['data']:
        wallpaper = random.choice(data['data'])
        return wallpaper['path']  # URL direta da imagem
    return None

async def enviar_wallpaper_periodicamente():
    await bot.wait_until_ready()
    canal = bot.get_channel(CHANNEL_ID)
    if canal is None:
        print('Canal não encontrado!')
        return
    while not bot.is_closed():
        tentativas = 0
        enviada = False
        while not enviada and tentativas < MAX_TENTATIVAS:
            image_url = get_wallhaven_popular_wallpaper()
            if image_url:
                image_name = f"wallhaven_popular_{random.randint(1, 1000)}.jpg"
                temp_path = os.path.join(PASTA_WALLPAPERS, image_name)
                image_response = requests.get(image_url, stream=True)
                if image_response.status_code == 200:
                    with open(temp_path, 'wb') as f:
                        shutil.copyfileobj(image_response.raw, f)
                    file_size = os.path.getsize(temp_path)
                    if file_size <= MAX_DISCORD_FILE_SIZE:
                        print(f"Imagem {image_name} baixada com sucesso!")
                        with open(temp_path, 'rb') as img:
                            await canal.send(file=discord.File(img, filename=image_name))
                        print(f"Imagem {image_name} enviada para o canal!")
                        enviada = True
                    else:
                        print(f"Imagem {image_name} é muito grande para o Discord ({file_size / (1024*1024):.2f} MB). Tentando outra...")
                    os.remove(temp_path)
                else:
                    print(f"Erro ao baixar a imagem: {image_response.status_code}")
                    enviada = True  # Para não travar em erro de download
            else:
                print("Não foi possível encontrar uma imagem popular no Wallhaven.")
                enviada = True  # Para não travar em erro de busca
            tentativas += 1
        if not enviada:
            print("Não foi possível encontrar um wallpaper popular com as especificações desejadas no momento.")
        await asyncio.sleep(INTERVALO)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    bot.loop.create_task(enviar_wallpaper_periodicamente())

@bot.command()
async def aura(ctx):
    tentativas = 0
    enviada = False
    while not enviada and tentativas < MAX_TENTATIVAS:
        image_url = get_random_wallpaper_url('wallpapers', ULTIMOS_WALLPAPERS)
        if image_url:
            image_name = f"wallpaper_{random.randint(1, 1000)}.jpg"
            temp_path = os.path.join(PASTA_WALLPAPERS, image_name)
            image_response = requests.get(image_url, stream=True)
            if image_response.status_code == 200:
                with open(temp_path, 'wb') as f:
                    shutil.copyfileobj(image_response.raw, f)
                file_size = os.path.getsize(temp_path)
                if file_size <= MAX_DISCORD_FILE_SIZE:
                    with open(temp_path, 'rb') as img:
                        await ctx.send(file=discord.File(img, filename=image_name))
                    ULTIMOS_WALLPAPERS.append(image_url)
                    if len(ULTIMOS_WALLPAPERS) > MAX_ULTIMOS:
                        ULTIMOS_WALLPAPERS.pop(0)
                    enviada = True
                else:
                    await ctx.send("A imagem encontrada é muito grande para enviar no Discord. Tentando outra...")
                os.remove(temp_path)
            else:
                await ctx.send("Erro ao baixar a imagem.")
                enviada = True
        else:
            await ctx.send("Não foi possível encontrar uma imagem no Reddit.")
            enviada = True
        tentativas += 1
    if not enviada:
        await ctx.send("Não foi possível encontrar um wallpaper com as especificações desejadas no momento.")

@bot.command()
async def auraanime(ctx):
    tentativas = 0
    enviada = False
    while not enviada and tentativas < MAX_TENTATIVAS:
        image_url = get_random_anime_wallpaper_url()
        if image_url:
            image_name = f"anime_wallpaper_{random.randint(1, 1000)}.jpg"
            temp_path = os.path.join(PASTA_WALLPAPERS, image_name)
            image_response = requests.get(image_url, stream=True)
            if image_response.status_code == 200:
                with open(temp_path, 'wb') as f:
                    shutil.copyfileobj(image_response.raw, f)
                file_size = os.path.getsize(temp_path)
                if file_size <= MAX_DISCORD_FILE_SIZE:
                    with open(temp_path, 'rb') as img:
                        await ctx.send(file=discord.File(img, filename=image_name))
                    enviada = True
                else:
                    await ctx.send("A imagem encontrada é muito grande para enviar no Discord. Tentando outra...")
                os.remove(temp_path)
            else:
                await ctx.send("Erro ao baixar a imagem.")
                enviada = True
        else:
            await ctx.send("Não foi possível encontrar um wallpaper de anime no Reddit.")
            enviada = True
        tentativas += 1
    if not enviada:
        await ctx.send("Não foi possível encontrar um wallpaper de anime com as especificações desejadas no momento.")

@bot.command()
async def engine(ctx):
    msg = (
        '**Sites para encontrar wallpapers animados para Wallpaper Engine:**\n'
        '- [Steam Workshop - Wallpaper Engine](https://steamcommunity.com/app/431960/workshop/)\n'
        '- [Wallpaper Engine Hub](https://wallpaperengine.io/en)\n'
        '- [SteamGridDB Wallpapers](https://steamgriddb.com/wallpapers)\n'
        '- [Wallhaven Anime Wallpapers](https://wallhaven.cc/search?q=anime&categories=100&purity=100&atleast=1920x1080&ratios=16x9)\n'
        '\nAcesse esses sites para baixar e importar wallpapers animados ou estáticos no Wallpaper Engine!'
    )
    await ctx.send(msg)

# Verificar se o token está configurado antes de tentar conectar
if not TOKEN:
    print("ERRO: TOKEN não configurado! Verifique a variável de ambiente TOKEN no Railway.")
    exit(1)

print(f"Tentando conectar com token: {TOKEN[:10]}...")
bot.run(TOKEN) 