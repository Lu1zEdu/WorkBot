# bot.py
import os
import nextcord
from nextcord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime

# Importa nossa função de busca de vagas
from job_search import search_jobs

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
TARGET_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

# --- Configuração do WorkBot ---
intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Armazena os IDs das vagas já postadas para evitar duplicatas
posted_job_ids = set()

# --- Eventos do WorkBot ---
@bot.event
async def on_ready():
    """
    Evento acionado quando o WorkBot se conecta com sucesso ao Discord.
    """
    print(f'WorkBot conectado como: {bot.user.name}')
    print(f'ID do Bot: {bot.user.id}')
    print('------')
    # Inicia a tarefa agendada
    check_new_jobs.start()

# NOVO COMANDO DE AJUDA
@bot.command(name='ajuda')
async def help_command(ctx):
    """
    Comando que mostra uma mensagem de ajuda com os comandos disponíveis.
    """
    # Usamos aspas triplas para criar um texto com várias linhas
    help_text = """
        **Comandos do WorkBot:**

        `!vaga <palavra-chave>`
        Busca por vagas de emprego com a palavra-chave que você escolher.
        *Exemplo: `!vaga Python`*

        `!ajuda`
        Mostra esta mensagem de ajuda.
    """
    # Cria um Embed para a mensagem ficar mais bonita
    embed = nextcord.Embed(
        title="Ajuda do WorkBot 🤖",
        description=help_text,
        color=nextcord.Color.green()
    )
    await ctx.send(embed=embed)


def search_linkedin_jobs(keyword: str):
    print(f"Buscando vagas para '{keyword}' no LinkedIn...")

    # A URL de busca do LinkedIn é complexa. Este é um exemplo simplificado.
    url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}"

    # LinkedIn bloqueia requisições simples, então precisamos simular um navegador.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # --- AQUI ESTÁ A PARTE DIFÍCIL E FRÁGIL ---
        # Você precisaria inspecionar o HTML do LinkedIn para encontrar as tags
        # e classes corretas para as vagas. Exemplo hipotético:
        # job_cards = soup.find_all('div', class_='base-search-card__info')

        # ... aqui viria o código para extrair título, empresa, link de cada "card" ...

        # Por enquanto, retornamos uma lista vazia como exemplo
        print("AVISO: A implementação real do scraping do LinkedIn é complexa e requer análise detalhada do site.")
        return []

    except Exception as e:
        print(f"Erro ao fazer scraping do LinkedIn: {e}")
        return []

# --- Comandos do WorkBot ---
@bot.command(name='vaga')
async def find_job(ctx, *, keyword: str):
    """
    Comando para buscar vagas manualmente. Ex: !vaga Python
    """
    await ctx.send(f"🔎 Buscando vagas para `{keyword}`...")
    
    jobs = search_jobs(keyword, limit=5)
    
    if not jobs:
        await ctx.send(f"Nenhuma vaga encontrada para `{keyword}`.")
        return
        
    for job in jobs:
        embed = create_job_embed(job)
        await ctx.send(embed=embed)

# --- Tarefas Agendadas (Tasks) ---
@tasks.loop(minutes=60)
async def check_new_jobs():
    """
    Tarefa agendada que busca novas vagas e as posta no canal definido.
    """
    print("Executando verificação agendada de vagas...")
    
    keyword_to_search = "software engineer" 
    jobs = search_jobs(keyword_to_search, limit=10)
    
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        print(f"ERRO: Canal com ID {TARGET_CHANNEL_ID} não encontrado.")
        return
        
    for job in reversed(jobs):
        job_id = job.get('id')
        if job_id not in posted_job_ids:
            try:
                embed = create_job_embed(job)
                await channel.send(embed=embed)
                posted_job_ids.add(job_id)
                print(f"Nova vaga postada: {job.get('title')}")
            except Exception as e:
                print(f"Erro ao postar vaga {job_id}: {e}")

@check_new_jobs.before_loop
async def before_check_new_jobs():
    await bot.wait_until_ready()

# --- Funções Auxiliares ---
def create_job_embed(job: dict):
    """
    Cria uma mensagem bonita (Embed) para uma vaga de emprego.
    """
    title = job.get('title', 'N/A')
    company = job.get('company_name', 'N/A')
    url = job.get('url', '#')
    
    try:
        pub_date_str = job.get('publication_date', '')
        pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
        date_formatted = pub_date.strftime('%d/%m/%Y')
    except:
        date_formatted = "N/A"

    job_type = job.get('job_type', 'N/A').replace('_', ' ').title()

    embed = nextcord.Embed(
        title=f"💼 {title}",
        url=url,
        description=f"**Empresa:** {company}\n**Tipo:** {job_type}",
        color=nextcord.Color.dark_green() # Mudei a cor para combinar com o nome "WorkBot"
    )
    embed.add_field(name="📅 Data de Publicação", value=date_formatted, inline=True)
    embed.set_footer(text=f"WorkBot - ID da Vaga: {job.get('id')}")
    
    return embed

# --- Inicia o WorkBot ---
if __name__ == "__main__":
    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN)
    else:
        print("ERRO: O token do Discord não foi encontrado. Verifique seu arquivo .env")