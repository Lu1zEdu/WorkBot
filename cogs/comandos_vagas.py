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
        """Mostra uma mensagem de ajuda com os comandos disponíveis."""
        help_text = (
            "**Bem-vindo ao WorkBot! 🤖**\n\n"
            "Eu sou seu assistente para encontrar vagas de emprego em diversas fontes.\n\n"
            "--- \n\n"
            "### `/vaga`\n"
            "Busca vagas com filtros avançados. Combine várias opções para refinar sua busca.\n\n"
            "**Opções de Filtro:**\n"
            "🔹 **`cargo_ou_tecnologia` (Obrigatório)**: A palavra-chave da sua busca.\n"
            "   *Ex: `Python`, `Desenvolvedor React`, `UX Designer`*\n\n"
            "🔹 **`empresa` (Opcional)**: Filtra por uma empresa específica.\n"
            "   *Ex: `Google`, `Toptal`*\n\n"
            "🔹 **`tipo_de_trabalho` (Opcional)**: Filtra pelo tipo de contrato.\n"
            "   *Opções: `Full-Time`, `Contract`*\n\n"
            "🔹 **`publicado_nas_ultimas_horas` (Opcional)**: Mostra apenas vagas recentes.\n"
            "   *Ex: `24` (último dia), `168` (última semana)*\n\n"
        )
        embed = nextcord.Embed(title="Ajuda do WorkBot", description=help_text, color=nextcord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @nextcord.slash_command(name="vaga", description="Busca vagas de emprego com filtros avançados.")
    async def find_job(self, 
                       interaction: nextcord.Interaction,
                       cargo_ou_tecnologia: str,
                       empresa: str = None,
                       tipo_de_trabalho: str = nextcord.SlashOption(choices={"Tempo Integral": "full-time", "Contrato": "contract"}, required=False),
                       publicado_nas_ultimas_horas: int = None):
        """Comando para buscar vagas manualmente com filtros."""
        await interaction.response.defer(ephemeral=True)

        jobs = search_all_sources(keyword=cargo_ou_tecnologia)
        filtered_jobs = jobs
        
        if empresa:
            filtered_jobs = [j for j in filtered_jobs if empresa.lower() in j.get('company_name', '').lower()]
            
        if tipo_de_trabalho:
            filtered_jobs = [j for j in filtered_jobs if j.get('job_type', '').lower() == tipo_de_trabalho]

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

        await interaction.followup.send(f"🔎 Encontrei {len(filtered_jobs)} vaga(s). As 5 melhores são:", ephemeral=True)
        
        for job in filtered_jobs[:5]:
            embed = create_job_embed(job)
            await interaction.channel.send(embed=embed)

def setup(bot):
    """Função que o Nextcord usa para carregar o Cog."""
    bot.add_cog(ComandosVagas(bot))
