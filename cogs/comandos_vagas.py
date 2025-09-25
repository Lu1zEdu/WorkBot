# cogs/comandos_vagas.py
import nextcord
from nextcord.ext import commands
from job_search import search_all_sources
from bot import create_job_embed
from datetime import datetime, timedelta, timezone
import re

class ComandosVagas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_last_search = {}

    @nextcord.slash_command(name="ajuda", description="Explica como usar todos os comandos do WorkBot.")
    async def help_command(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Ajuda do WorkBot 🤖", color=nextcord.Color.green())
        embed.description = "Eu sou o seu assistente para encontrar vagas de emprego em múltiplas fontes!\n\nUse os comandos abaixo para encontrar a vaga perfeita para si."
        embed.add_field(name="`/vaga`", value="O comando principal para buscar vagas. Ele possui vários filtros para refinar a sua busca e encontrar exatamente o que procura.", inline=False)
        embed.add_field(name="`/mais_vagas`", value="Se a sua última busca encontrou mais de 5 resultados, use este comando para ver os próximos 5, sem precisar de preencher os filtros novamente.", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @nextcord.slash_command(name="mais_vagas", description="Mostra mais resultados da sua última busca.")
    async def more_jobs(self, interaction: nextcord.Interaction):
        user_id = interaction.user.id
        if user_id not in self.user_last_search or not self.user_last_search[user_id]['results']:
            await interaction.response.send_message("Você precisa fazer uma busca com `/vaga` primeiro.", ephemeral=True)
            return
        await interaction.response.defer()
        search_data = self.user_last_search[user_id]
        results = search_data['results']
        offset = search_data['offset']
        if offset >= len(results):
            await interaction.followup.send("Não há mais vagas para mostrar desta busca.", ephemeral=True)
            return
        next_jobs = results[offset : offset + 5]
        await interaction.followup.send(f"Mostrando mais {len(next_jobs)} vagas da sua última busca:", ephemeral=False)
        for job in next_jobs:
            embed = create_job_embed(job)
            await interaction.channel.send(embed=embed)
        self.user_last_search[user_id]['offset'] += len(next_jobs)

    @nextcord.slash_command(name="vaga", description="Busca vagas de emprego com filtros avançados e inteligentes.")
    async def find_job(self, 
        interaction: nextcord.Interaction,
        cargo: str = nextcord.SlashOption(description="Escolha uma área geral ou digite um cargo específico.", required=True, choices={"Engenheiro(a) de Software": "Software Engineer", "Desenvolvedor(a) Frontend": "Frontend Developer", "Desenvolvedor(a) Backend": "Backend Developer", "Analista de Dados": "Data Analyst", "Gestor(a) de Produto": "Product Manager"}),
        tecnologia: str = nextcord.SlashOption(description="Filtre por uma linguagem ou tecnologia específica (ex: Python, React, AWS).", required=False),
        senioridade: str = nextcord.SlashOption(description="Filtre pelo seu nível de experiência profissional.", choices={"Assistente / Estágio": "assistant", "Júnior": "junior", "Pleno / Mid": "mid", "Sênior": "senior", "Especialista / Lead": "lead"}, required=False),
        localizacao: str = nextcord.SlashOption(description="Busque por país, cidade ou estado (ex: Brazil, Lisbon, USA).", required=False),
        salario_anual_minimo_usd: int = nextcord.SlashOption(description="Filtre por um salário anual mínimo desejado (em dólares). Ex: 50000", required=False)
    ):
        await interaction.response.defer(ephemeral=True)
        jobs = search_all_sources(keyword=cargo)
        filtered_jobs = jobs
        
        if tecnologia: filtered_jobs = [j for j in filtered_jobs if tecnologia.lower() in [tag.lower() for tag in j.get('tags', [])]]
        if senioridade:
            keywords = {"assistant": ["assistant", "estágio", "intern"],"junior": ["junior", "entry"],"mid": ["mid", "pleno"],"senior": ["senior", "sr"],"lead": ["lead", "principal"]}.get(senioridade, [])
            filtered_jobs = [j for j in filtered_jobs if any(kw in tag.lower() for kw in keywords for tag in j.get('tags', [])) or any(kw in j.get('title', '').lower() for kw in keywords)]
        if localizacao: filtered_jobs = [j for j in filtered_jobs if localizacao.lower() in j.get('location', '').lower()]
        if salario_anual_minimo_usd:
            temp = []
            for j in filtered_jobs:
                s = j.get('salary', ''); n = re.findall(r'\d{1,3}(?:,\d{3})*', s)
                if n:
                    try:
                        if int(n[0].replace(',', '')) >= salario_anual_minimo_usd: temp.append(j)
                    except: continue
            filtered_jobs = temp

        self.user_last_search[interaction.user.id] = {'results': filtered_jobs, 'offset': 5}
        
        if not filtered_jobs:
            await interaction.followup.send("Nenhuma vaga encontrada com os seus filtros.", ephemeral=True)
            return

        message = f"🔎 {interaction.user.mention} encontrou **{len(filtered_jobs)}** vaga(s) para si!"
        if len(filtered_jobs) > 5: message += f"\nMostrando as 5 primeiras. Use `/mais_vagas` para ver o resto."
        
        await interaction.followup.send(message, ephemeral=False)
        for job in filtered_jobs[:5]:
            embed = create_job_embed(job)
            await interaction.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(ComandosVagas(bot))