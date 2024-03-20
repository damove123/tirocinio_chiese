import json

# Percorso al file JSON
file_path = "/Users/albi/Desktop/Università/tirocinio_chiese/fileExcel/RepertiPolo.json"

# Carica il JSON da file
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)  # `data` ora è una lista di dizionari

# Itera su ogni oggetto nell'array
# Itera su ogni oggetto nell'array JSON
for obj in data:
    # Controlla se la chiave "Latino" esiste nell'oggetto corrente
    if "Latino" in obj:
        # Assicurati che il valore di "Latino" sia una stringa prima di chiamare replace
        if isinstance(obj['Latino'], str):
            obj['Latino'] = obj['Latino'].replace('[ ]', '')  # Sostituisci '\n' con '\t'
        else:
            print("Il valore di 'Latino' non è una stringa", type(obj['Latino']))

# Salva il JSON modificato
with open(file_path, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print("Sostituzione completata.")
