FROM python:3.11-slim

RUN apt-get update && apt-get install -y git
WORKDIR /app
COPY entrypoint.sh .
RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
