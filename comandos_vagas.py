import nextcord
from nextcord.ext import commands
from job_search import search_jobs
from bot import create_job_embed

class ComandosVagas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ajuda')
    async def help_command(self, ctx):
        """Mostra uma mensagem de ajuda com os comandos disponíveis."""
        help_text = """
            **Comandos do WorkBot:**
            `!vaga <palavra-chave>` - Busca por vagas. Ex: `!vaga Python`
            `!ajuda` - Mostra esta mensagem de ajuda.
        """
        embed = nextcord.Embed(title="Ajuda do WorkBot 🤖", description=help_text, color=nextcord.Color.green())
        await ctx.send(embed=embed)

    @commands.command(name='vaga')
    async def find_job(self, ctx, *, keyword: str):
        """Comando para buscar vagas manualmente."""
        await ctx.send(f"🔎 Buscando vagas para `{keyword}`...")
        jobs = search_jobs(keyword, limit=5)
        if not jobs:
            await ctx.send(f"Nenhuma vaga encontrada para `{keyword}`.")
            return
        for job in jobs:
            embed = create_job_embed(job)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(ComandosVagas(bot))