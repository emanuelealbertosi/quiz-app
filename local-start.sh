#!/bin/bash

# Colori per i messaggi
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Funzione per avviare il backend
start_backend() {
    echo -e "${GREEN}Avvio del backend...${NC}"
    BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
    cd "$BASE_DIR/backend" && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 9999 --reload &
    echo $! > "$BASE_DIR/backend.pid"
    echo -e "${GREEN}Backend avviato su http://localhost:9999${NC}"
}

# Funzione per avviare il frontend
start_frontend() {
    echo -e "${GREEN}Avvio del frontend...${NC}"
    BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
    cd "$BASE_DIR/frontend" && npm start &
    echo $! > "$BASE_DIR/frontend.pid"
    echo -e "${GREEN}Frontend avviato su http://localhost:3000${NC}"
}

# Funzione per arrestare i processi
stop() {
    echo -e "${GREEN}Arresto dei processi...${NC}"
    BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
    
    # Arresta il backend e tutti i suoi processi figli
    if [ -f "$BASE_DIR/backend.pid" ]; then
        echo -e "${GREEN}Arresto del backend...${NC}"
        pid=$(cat "$BASE_DIR/backend.pid")
        # Termina il processo e tutti i suoi figli
        pkill -P $pid 2>/dev/null || true
        kill -15 $pid 2>/dev/null || true
        sleep 1
        # Forza la chiusura se ancora attivo
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${GREEN}Forzando chiusura del backend...${NC}"
            kill -9 $pid 2>/dev/null || true
            pkill -9 -P $pid 2>/dev/null || true
        fi
        rm "$BASE_DIR/backend.pid"
        echo -e "${GREEN}Backend arrestato${NC}"
    fi
    
    # Arresta il frontend e tutti i suoi processi figli
    if [ -f "$BASE_DIR/frontend.pid" ]; then
        echo -e "${GREEN}Arresto del frontend...${NC}"
        pid=$(cat "$BASE_DIR/frontend.pid")
        # Termina il processo e tutti i suoi figli
        pkill -P $pid 2>/dev/null || true
        kill -15 $pid 2>/dev/null || true
        sleep 1
        # Forza la chiusura se ancora attivo
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${GREEN}Forzando chiusura del frontend...${NC}"
            kill -9 $pid 2>/dev/null || true
            pkill -9 -P $pid 2>/dev/null || true
        fi
        rm "$BASE_DIR/frontend.pid"
        echo -e "${GREEN}Frontend arrestato${NC}"
    fi
    
    # Assicurarsi che non ci siano processi orfani di uvicorn o npm
    echo -e "${GREEN}Verifica processi residui...${NC}"
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "node.*frontend" 2>/dev/null || true
    
    echo -e "${GREEN}Tutti i processi arrestati${NC}"
}

# Menu principale
case "$1" in
    start)
        start_backend
        start_frontend
        echo -e "${GREEN}Applicazione avviata:${NC}"
        echo -e "  - Frontend: http://localhost:3000"
        echo -e "  - Backend API: http://localhost:9999"
        echo -e "  - Documentazione API: http://localhost:9999/docs"
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        start_backend
        start_frontend
        echo -e "${GREEN}Applicazione riavviata:${NC}"
        echo -e "  - Frontend: http://localhost:3000"
        echo -e "  - Backend API: http://localhost:9999"
        echo -e "  - Documentazione API: http://localhost:9999/docs"
        ;;
    *)
        echo "Utilizzo: $0 {start|stop|restart}"
        exit 1
        ;;
esac

exit 0
