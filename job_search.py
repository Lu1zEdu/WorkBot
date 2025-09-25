import requests
from concurrent.futures import ThreadPoolExecutor

def search_remotive_jobs(keyword: str):
    """Busca vagas na API do Remotive."""
    print(f"Buscando no Remotive por: {keyword}")
    API_URL = "https://remotive.com/api/remote-jobs"
    params = {'search': keyword, 'limit': 50}
    
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        jobs = data.get('jobs', [])
        
        formatted_jobs = []
        for job in jobs:
            formatted_jobs.append({
                'id': f"remotive_{job.get('id')}",
                'title': job.get('title'),
                'company_name': job.get('company_name'),
                'url': job.get('url'),
                'publication_date': job.get('publication_date'),
                'job_type': job.get('job_type'),
                'source': 'Remotive'
            })
        return formatted_jobs
    except Exception as e:
        print(f"Erro ao buscar no Remotive: {e}")
        return []

def search_linkedin_jobs(keyword: str):
    """Placeholder para a busca de vagas no LinkedIn via scraping."""
    print(f"Buscando no LinkedIn por: {keyword} (implementação pendente)")

    return []


def search_all_sources(keyword: str):
    """
    Executa todas as funções de busca em paralelo e agrega os resultados.
    """
    all_jobs = []
    
    search_functions = [search_remotive_jobs, search_linkedin_jobs]
    
    with ThreadPoolExecutor() as executor:
        results = executor.map(lambda f: f(keyword), search_functions)
        
        for job_list in results:
            all_jobs.extend(job_list)
            
    print(f"Total de {len(all_jobs)} vagas encontradas de todas as fontes.")
    return all_jobs
