FROM python:3.9-slim

# Installare tkinter e altre dipendenze di sistema necessarie per la GUI
RUN apt-get update && apt-get install -y \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Impostare la directory di lavoro
WORKDIR /app

# Impostare variabile ambiente per indicare che è in Docker
ENV DOCKER_CONTAINER=true

# Copiare il codice sorgente
COPY src/ .

# Comando per eseguire l'applicazione (accetta argomenti da riga di comando)
CMD ["python", "mbox_to_eml_gui.py"]