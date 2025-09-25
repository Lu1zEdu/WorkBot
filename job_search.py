import requests

API_URL = "https://remotive.com/api/remote-jobs"

def search_jobs(keyword: str, limit: int = 5):
    """
    Busca vagas de emprego na API do Remotive com base em uma palavra-chave.
    """
    params = {'search': keyword, 'limit': limit}
    
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        jobs = data.get('jobs', [])
        print(f"Encontradas {len(jobs)} vagas para '{keyword}'.")
        return jobs
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar vagas: {e}")
        return []
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return []