GIT_REPO_URL="https://github.com/Lu1zEdu/WorkBot.git"

if [ ! -d ".git" ]; then
  echo "Clonando o repositório pela primeira vez..."
  git clone $GIT_REPO_URL .
else
  echo "Repositório já existe. Puxando atualizações..."
  git pull origin main
fi

echo "Instalando dependências..."
pip install --no-cache-dir -r requirements.txt

echo "Iniciando o WorkBot..."
exec python bot.py
