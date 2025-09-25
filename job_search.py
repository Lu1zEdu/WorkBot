import os
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

load_dotenv()
JOOBLE_API_KEY = os.getenv('JOOBLE_API_KEY')

def search_remotive_jobs(keyword: str):
    print(f"Buscando no Remotive por: {keyword}")
    API_URL = "https://remotive.com/api/remote-jobs"
    params = {'search': keyword, 'limit': 200}
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json(); jobs = data.get('jobs', [])
        formatted_jobs = []
        for job in jobs:
            formatted_jobs.append({
                'id': f"remotive_{job.get('id')}", 'title': job.get('title'),
                'company_name': job.get('company_name'), 'url': job.get('url'),
                'publication_date': job.get('publication_date'), 'tags': job.get('tags', []),
                'location': job.get('candidate_required_location', 'Remoto Global'),
                'salary': job.get('salary', ''), 'source': 'Remotive'
            })
        return formatted_jobs
    except Exception as e:
        print(f"Erro ao buscar no Remotive: {e}"); return []

def search_jooble_jobs(keyword: str):
    if not JOOBLE_API_KEY:
        print("AVISO: Chave da API do Jooble não encontrada."); return []
    print(f"Buscando no Jooble por: {keyword}")
    API_URL = f"https://jooble.org/api/{JOOBLE_API_KEY}"
    body = {"keywords": keyword}
    try:
        response = requests.post(API_URL, json=body, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        data = response.json(); jobs = data.get('jobs', [])
        formatted_jobs = []
        for job in jobs:
            try: pub_date_iso = datetime.strptime(job.get('updated'), "%Y-%m-%d %H:%M:%S").isoformat() + "Z"
            except (ValueError, TypeError): pub_date_iso = None
            formatted_jobs.append({
                'id': f"jooble_{job.get('id')}", 'title': job.get('title'),
                'company_name': job.get('company'), 'url': job.get('link'),
                'publication_date': pub_date_iso, 'tags': [tag['value'] for tag in job.get('keywords', [])],
                'location': job.get('location', 'N/A'), 'salary': job.get('salary', ''), 'source': 'Jooble'
            })
        return formatted_jobs
    except Exception as e:
        print(f"Erro ao buscar no Jooble: {e}"); return []

def search_all_sources(keyword: str):
    all_jobs = []
    search_functions = [search_remotive_jobs, search_jooble_jobs]
    with ThreadPoolExecutor(max_workers=len(search_functions)) as executor:
        results = executor.map(lambda f: f(keyword), search_functions)
        for job_list in results: all_jobs.extend(job_list)
    print(f"Total de {len(all_jobs)} vagas encontradas de todas as fontes.")
    all_jobs.sort(key=lambda x: x.get('publication_date') or '', reverse=True)
    return all_jobs