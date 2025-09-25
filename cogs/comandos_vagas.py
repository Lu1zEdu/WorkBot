import nextcord
from nextcord.ext import commands
from job_search import search_all_sources
from bot import create_job_embed
from datetime import datetime, timedelta, timezone

class ComandosVagas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="ajuda", description="Mostra a mensagem de ajuda com todos os comandos.")
    async def help_command(self, interaction: nextcord.Interaction):
        help_text = (
            "**Bem-vindo ao WorkBot! 🤖**\n\n"
            "Eu sou seu assistente para encontrar vagas de emprego em diversas fontes.\n\n"
            "--- \n\n"
            "### `/vaga`\n"
            "Busca vagas com filtros avançados. Combine várias opções para refinar sua busca.\n\n"
            "**Opções de Filtro:**\n"
            "🔹 **`cargo` (Obrigatório)**: A palavra-chave principal da sua busca.\n"
            "   *Ex: `Software Engineer`, `Product Manager`*\n\n"
            "🔹 **`linguagem_ou_tecnologia` (Opcional)**: Filtra por uma tecnologia específica.\n"
            "   *Ex: `Python`, `React`, `AWS`*\n\n"
            "🔹 **`senioridade` (Opcional)**: Filtra pelo nível de experiência.\n"
            "   *Opções: Júnior, Pleno, Sênior, Especialista*\n\n"
            "🔹 **`empresa` (Opcional)**: Filtra por uma empresa específica.\n"
            "   *Ex: `Google`, `Toptal`*\n\n"
            "🔹 **`tipo_de_trabalho` (Opcional)**: Filtra pelo tipo de contrato.\n"
            "   *Opções: `Tempo Integral`, `Contrato`*\n\n"
            "🔹 **`publicado_nas_ultimas_horas` (Opcional)**: Mostra apenas vagas recentes.\n"
            "   *Ex: `24` (último dia), `168` (última semana)*\n\n"
        )
        embed = nextcord.Embed(title="Ajuda do WorkBot", description=help_text, color=nextcord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @nextcord.slash_command(name="vaga", description="Busca vagas de emprego com filtros avançados.")
    async def find_job(self, 
                       interaction: nextcord.Interaction,
                       cargo: str,
                       linguagem_ou_tecnologia: str = None,
                       senioridade: str = nextcord.SlashOption(
                           choices={"Júnior": "junior", "Pleno / Mid": "mid", "Sênior": "senior", "Especialista / Lead": "lead"},
                           required=False
                       ),
                       empresa: str = None,
                       tipo_de_trabalho: str = nextcord.SlashOption(
                           choices={"Tempo Integral": "full_time", "Contrato": "contract"}, 
                           required=False
                       ),
                       publicado_nas_ultimas_horas: int = None):
        await interaction.response.defer(ephemeral=True)

        jobs = search_all_sources(keyword=cargo)
        filtered_jobs = jobs
        
        if linguagem_ou_tecnologia:
            filtered_jobs = [j for j in filtered_jobs if linguagem_ou_tecnologia.lower() in [tag.lower() for tag in j.get('tags', [])]]

        if senioridade:
            keywords_map = {
                "junior": ["junior", "entry", "estágio", "intern"],
                "mid": ["mid", "pleno", "intermediate"],
                "senior": ["senior", "sr"],
                "lead": ["lead", "principal", "specialist", "especialista", "architect"]
            }
            keywords_to_check = keywords_map.get(senioridade, [])
            filtered_jobs = [
                j for j in filtered_jobs 
                if any(keyword in tag.lower() for keyword in keywords_to_check for tag in j.get('tags', []))
            ]

        if empresa:
            filtered_jobs = [j for j in filtered_jobs if empresa.lower() in j.get('company_name', '').lower()]
            
        if tipo_de_trabalho:
            filtered_jobs = [j for j in filtered_jobs if j.get('job_type', '').replace('_', ' ').lower() == tipo_de_trabalho.replace('_', ' ').lower()]

        if publicado_nas_ultimas_horas:
            time_limit = datetime.now(timezone.utc) - timedelta(hours=publicado_nas_ultimas_horas)
            temp_jobs = []
            for job in filtered_jobs:
                try:
                    pub_date = datetime.fromisoformat(job['publication_date'].replace('Z', '+00:00'))
                    if pub_date >= time_limit:
                        temp_jobs.append(job)
                except (KeyError, ValueError):
                    continue
            filtered_jobs = temp_jobs
        
        if not filtered_jobs:
            await interaction.followup.send("Nenhuma vaga encontrada com os filtros especificados.", ephemeral=True)
            return

        await interaction.followup.send(f"🔎 {interaction.user.mention} encontrou {len(filtered_jobs)} vaga(s). As 5 melhores são:", ephemeral=False)
        
        for job in filtered_jobs[:5]:
            embed = create_job_embed(job)
            await interaction.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(ComandosVagas(bot))