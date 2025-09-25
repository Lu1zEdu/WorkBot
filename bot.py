import os
import json
import nextcord
from nextcord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime
from job_search import search_all_sources

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
TARGET_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
DB_FILE = "posted_jobs.json"

def load_posted_ids():
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            return set(data.get("posted_ids", []))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_posted_id(job_id):
    posted_job_ids.add(job_id)
    with open(DB_FILE, "w") as f:
        json.dump({"posted_ids": list(posted_job_ids)}, f, indent=4)

posted_job_ids = load_posted_ids()

intents = nextcord.Intents.default()
bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'WorkBot conectado como: {bot.user.name}')
    print(f'ID do Bot: {bot.user.id}')
    print('------')
    check_new_jobs.start()

@tasks.loop(hours=2)
async def check_new_jobs():
    print("Executando verificação agendada de vagas...")
    jobs = search_all_sources("Software Engineer")
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        print(f"ERRO: Canal com ID {TARGET_CHANNEL_ID} não encontrado.")
        return
    new_jobs_found = 0
    for job in reversed(jobs):
        job_id = job.get('id')
        if job_id not in posted_job_ids:
            new_jobs_found += 1
            try:
                embed = create_job_embed(job)
                await channel.send(embed=embed)
                save_posted_id(job_id)
                print(f"Nova vaga publicada: {job.get('title')}")
            except Exception as e:
                print(f"Erro ao publicar vaga {job_id}: {e}")
    if new_jobs_found == 0:
        print("Nenhuma nova vaga encontrada na verificação agendada.")

@check_new_jobs.before_loop
async def before_check_new_jobs():
    await bot.wait_until_ready()

def create_job_embed(job: dict):
    title = job.get('title', 'N/A')
    company = job.get('company_name', 'N/A')
    url = job.get('url', '#')
    location = job.get('location', 'N/A')
    salary = job.get('salary', '')
    source = job.get('source', 'Desconhecida')
    tags = job.get('tags', [])
    try:
        pub_date_str = job.get('publication_date', '')
        date_formatted = datetime.fromisoformat(pub_date_str.replace('Z', '')).strftime('%d/%m/%Y') if pub_date_str else "N/A"
    except:
        date_formatted = "N/A"
    embed = nextcord.Embed(
        title=f"💼 {title}",
        url=url,
        description=f"**Empresa:** {company}\n**📍 Localização:** {location}",
        color=nextcord.Color.dark_green()
    )
    if salary:
        embed.add_field(name="💰 Salário", value=f"`{salary}`", inline=True)
    embed.add_field(name="📅 Publicação", value=date_formatted, inline=True)
    if tags:
        embed.add_field(name="⚙️ Tecnologias", value=", ".join(f"`{t}`" for t in tags[:7]), inline=False)
    embed.set_footer(text=f"Fonte: {source}")
    return embed

if __name__ == "__main__":
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"Cog '{filename}' carregado.")
            except Exception as e:
                print(f"Falha ao carregar Cog '{filename}': {e}")
    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN)
    else:
        print("ERRO CRÍTICO: Token do Discord não encontrado.")