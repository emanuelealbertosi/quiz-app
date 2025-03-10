"""
Script per testare le nuove funzionalità di PathQuiz.

Questo script testa il flusso completo:
1. Login
2. Creazione di un percorso con quiz
3. Assegnazione del percorso a uno studente
4. Login come studente
5. Completamento di un quiz nel percorso
6. Verifica dei quiz completati
"""
import sys
import os
import json
import requests
from pprint import pprint

# URL base dell'API
BASE_URL = "http://localhost:9999/api/v1"

def login(username, password):
    """Effettua il login e restituisce il token di accesso."""
    # Usa form-data invece di JSON per OAuth2
    login_data = {
        "username": username,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/login", data=login_data)
    if response.status_code != 200:
        print(f"Errore di login: {response.status_code}")
        print(response.text)
        raise Exception("Login fallito")
    return response.json()["access_token"]

def create_path(token, name, description, quiz_ids, bonus_points=10):
    """Crea un nuovo percorso."""
    headers = {"Authorization": f"Bearer {token}"}
    path_data = {
        "name": name,
        "description": description,
        "quiz_ids": quiz_ids,
        "bonus_points": bonus_points
    }
    response = requests.post(f"{BASE_URL}/paths/", json=path_data, headers=headers)
    print(f"Creazione percorso risposta: {response.status_code}")
    if response.status_code != 201:
        print(response.text)
        raise Exception("Errore nella creazione del percorso")
    return response.json()

def get_quizzes(token):
    """Ottiene la lista di tutti i quiz."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/quizzes/", headers=headers)
    if response.status_code != 200:
        print(f"Errore nel recupero dei quiz: {response.status_code}")
        print(response.text)
        raise Exception("Errore nel recupero dei quiz")
    return response.json()["quizzes"]  # Estrai la lista dei quiz

def get_path_quizzes(token, path_id):
    """Ottiene tutti i quiz di un percorso specifico."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/path-quizzes/path/{path_id}", headers=headers)
    if response.status_code != 200:
        print(f"Errore nel recupero dei quiz del percorso: {response.status_code}")
        print(response.text)
        raise Exception("Errore nel recupero dei quiz del percorso")
    return response.json()

def assign_path_to_student(token, path_id, student_id):
    """Assegna un percorso a uno studente."""
    headers = {"Authorization": f"Bearer {token}"}
    assign_data = {
        "path_id": path_id,
        "user_id": student_id  # Cambiato da student_id a user_id come richiesto dall'API
    }
    response = requests.post(f"{BASE_URL}/paths/assign", json=assign_data, headers=headers)
    if response.status_code not in [200, 201]:  
        print(f"Errore nell'assegnazione del percorso: {response.status_code}")
        print(response.text)
        raise Exception("Errore nell'assegnazione del percorso")
    return response.json()

def get_path_quiz(token, path_quiz_id):
    """Ottiene un quiz specifico di un percorso."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/path-quizzes/{path_quiz_id}", headers=headers)
    if response.status_code != 200:
        print(f"Errore nel recupero del quiz: {response.status_code}")
        print(response.text)
        raise Exception("Errore nel recupero del quiz")
    return response.json()

def attempt_path_quiz(token, path_quiz_id, answer, show_explanation=True):
    """Invia un tentativo per un quiz di un percorso."""
    headers = {"Authorization": f"Bearer {token}"}
    attempt_data = {
        "path_quiz_id": path_quiz_id,
        "answer": answer,
        "show_explanation": show_explanation
    }
    response = requests.post(f"{BASE_URL}/path-quizzes/attempt", json=attempt_data, headers=headers)
    if response.status_code != 200:
        print(f"Errore nel tentativo di quiz: {response.status_code}")
        print(response.text)
        raise Exception("Errore nel tentativo di quiz")
    return response.json()

def get_completed_path_quizzes(token, path_id):
    """Ottiene gli ID dei quiz completati in un percorso."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/path-quizzes/completed/{path_id}", headers=headers)
    if response.status_code != 200:
        print(f"Errore nel recupero dei quiz completati: {response.status_code}")
        print(response.text)
        raise Exception("Errore nel recupero dei quiz completati")
    return response.json()

def get_current_user(token):
    """Ottiene le informazioni sull'utente corrente."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if response.status_code != 200:
        print(f"Errore nel recupero dell'utente: {response.status_code}")
        print(response.text)
        raise Exception("Errore nel recupero dell'utente")
    return response.json()

def main():
    try:
        # Dati di test
        parent_username = "parent"
        parent_password = "password"
        student_username = "student"
        student_password = "password"
        
        # Effettua il login come genitore
        print("Effettuo login come genitore...")
        parent_token = login(parent_username, parent_password)
        print(f"Login genitore successo! Token: {parent_token[:10]}...")
        
        # Ottieni le informazioni sull'utente
        parent_info = get_current_user(parent_token)
        print(f"Informazioni genitore: {parent_info['username']}, ID: {parent_info['id']}")
        
        # Ottieni alcuni quiz da includere nel percorso
        print("\nOttengo la lista dei quiz disponibili...")
        quizzes = get_quizzes(parent_token)
        print("Risposta completa dei quiz:")
        pprint(quizzes[:2])  # Mostra solo i primi 2 per brevità
        
        if not quizzes:
            print("Nessun quiz trovato! Impossibile continuare.")
            return
            
        print(f"Trovati {len(quizzes)} quiz")
        # Prendi tutti i quiz disponibili (o i primi 3 se ce ne sono più di 3)
        num_quizzes = min(len(quizzes), 3)
        quiz_ids = [q["id"] for q in quizzes[:num_quizzes]]
        print(f"Quiz selezionati: {quiz_ids}")
        
        # Crea un nuovo percorso
        print("\nCreo un nuovo percorso...")
        path_data = create_path(
            parent_token,
            "Percorso di Test PathQuiz",
            "Un percorso per testare le nuove funzionalità di PathQuiz",
            quiz_ids,
            15  # 15 punti bonus
        )
        path_id = path_data["id"]
        print(f"Percorso creato con ID: {path_id}")
        
        # Ottieni i quiz del percorso
        print("\nOttengo i quiz del percorso...")
        path_quizzes = get_path_quizzes(parent_token, path_id)
        print(f"Trovati {len(path_quizzes)} quiz nel percorso:")
        for i, pq in enumerate(path_quizzes):
            print(f"  {i+1}. ID: {pq['id']}, Question: {pq['question'][:50]}...")
        
        # Ottieni lo student_id
        # Nota: in un'applicazione reale, dovresti avere un modo per ottenere l'ID dello studente
        student_id = 3  # L'ID dello student è 3
        
        # Assegna il percorso allo studente
        print(f"\nAssegno il percorso allo studente con ID {student_id}...")
        assign_result = assign_path_to_student(parent_token, path_id, student_id)
        print("Risultato:", assign_result)
        
        # Effettua il login come studente
        print("\nEffettuo login come studente...")
        student_token = login(student_username, student_password)
        print(f"Login studente successo! Token: {student_token[:10]}...")
        
        # Ottieni i quiz del percorso come studente
        print("Ottengo i quiz del percorso come studente...")
        student_path_quizzes = get_path_quizzes(student_token, path_id)
        
        if not student_path_quizzes:
            print("Errore: lo studente non può vedere i quiz del percorso!")
            return
        
        print(f"Lo studente vede {len(student_path_quizzes)} quiz nel percorso")
        
        # Seleziona il primo quiz del percorso
        path_quiz_id = student_path_quizzes[0]["id"]
        path_quiz = get_path_quiz(student_token, path_quiz_id)
        
        print(f"\nCompletamento del quiz ID: {path_quiz_id}")
        print(f"Domanda: {path_quiz['question']}")
        print(f"Opzioni: {path_quiz['options']}")
        print(f"Risposta corretta: {path_quiz['correct_answer']}")
        
        # Completa il quiz con la risposta corretta
        print("\nInvio la risposta corretta...")
        attempt_result = attempt_path_quiz(student_token, path_quiz_id, path_quiz["correct_answer"])
        print("Risultato del tentativo:")
        pprint(attempt_result)
        
        # Verifica i quiz completati
        print("\nOttengo la lista dei quiz completati nel percorso...")
        completed_quizzes = get_completed_path_quizzes(student_token, path_id)
        print(f"Quiz completati: {completed_quizzes}")
        
        print("\nTest completato con successo!")
    except Exception as e:
        print(f"Errore durante il test: {e}")

if __name__ == "__main__":
    main()
