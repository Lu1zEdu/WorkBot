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
    """Carrega os IDs de vagas já postadas do arquivo JSON."""
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            return set(data.get("posted_ids", []))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_posted_id(job_id):
    """Adiciona um novo ID de vaga ao arquivo JSON."""
    posted_job_ids.add(job_id)
    with open(DB_FILE, "w") as f:
        json.dump({"posted_ids": list(posted_job_ids)}, f, indent=4)

posted_job_ids = load_posted_ids()

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    """Evento acionado quando o WorkBot se conecta com sucesso ao Discord."""
    print(f'WorkBot conectado como: {bot.user.name}')
    print(f'ID do Bot: {bot.user.id}')
    print('------')
    check_new_jobs.start()

@tasks.loop(hours=2)
async def check_new_jobs():
    """Tarefa agendada que busca novas vagas e as posta no canal definido."""
    print("Executando verificação agendada de vagas...")
    keyword_to_search = "Desenvolvedor Python"
    jobs = search_all_sources(keyword_to_search)
    
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
                print(f"Nova vaga postada: {job.get('title')}")
            except Exception as e:
                print(f"Erro ao postar vaga {job_id}: {e}")
    
    if new_jobs_found == 0:
        print("Nenhuma nova vaga encontrada na verificação agendada.")


@check_new_jobs.before_loop
async def before_check_new_jobs():
    await bot.wait_until_ready()

def create_job_embed(job: dict):
    """Cria uma mensagem bonita (Embed) para uma vaga de emprego."""
    title = job.get('title', 'N/A')
    company = job.get('company_name', 'N/A')
    url = job.get('url', '#')
    job_type = job.get('job_type', 'N/A').replace('_', ' ').title()
    source = job.get('source', 'Desconhecida')
    
    try:
        pub_date_str = job.get('publication_date', '')
        pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
        date_formatted = pub_date.strftime('%d/%m/%Y')
    except:
        date_formatted = "N/A"

    embed = nextcord.Embed(
        title=f"💼 {title}",
        url=url,
        description=f"**Empresa:** {company}\n**Tipo:** {job_type}",
        color=nextcord.Color.dark_green()
    )
    embed.add_field(name="📅 Publicação", value=date_formatted, inline=True)
    embed.set_footer(text=f"Fonte: {source}")
    return embed

if __name__ == "__main__":
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"Cog '{filename}' carregado com sucesso.")
            except Exception as e:
                print(f"Falha ao carregar o Cog '{filename}': {e}")

    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN)
    else:
        print("ERRO CRÍTICO: O token do Discord não foi encontrado. Verifique seu arquivo .env")
