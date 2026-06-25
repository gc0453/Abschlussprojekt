import json
import os
from datetime import date


def load_person_db(path: str = "data/person_db.json") -> list:
    """Lädt die Personen-Datenbank aus der JSON-Datei.

    Args:
        path: Pfad zur JSON-Datei

    Returns:
        Liste aller Personen-Dictionaries
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_person_db(data: list, path: str = "data/person_db.json") -> None:
    """Speichert die Personen-Datenbank in die JSON-Datei.

    Args:
        data: Liste aller Personen-Dictionaries
        path: Pfad zur JSON-Datei
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent="\t", ensure_ascii=False)


def get_next_person_id(persons: list) -> int:
    """Gibt die nächste freie Personen-ID zurück.

    Args:
        persons: Liste aller bestehenden Personen-Dictionaries

    Returns:
        Nächste freie ID als Integer
    """
    if not persons:
        return 1
    return max(p["id"] for p in persons) + 1


def get_next_ekg_id(persons: list) -> int:
    """Gibt die nächste freie EKG-Test-ID zurück.

    Args:
        persons: Liste aller bestehenden Personen-Dictionaries

    Returns:
        Nächste freie EKG-ID als Integer
    """
    all_ekg_ids = [
        test["id"]
        for p in persons
        for test in p.get("ekg_tests", [])
    ]
    if not all_ekg_ids:
        return 1
    return max(all_ekg_ids) + 1


def add_person_with_ekg(
    firstname: str,
    lastname: str,
    date_of_birth: int,
    gender: str,
    ekg_file_bytes: bytes,
    ekg_filename: str,
    ekg_date: str,
    picture_bytes: bytes = None,
    picture_filename: str = None,
) -> str:
    """Fügt eine neue Person mit einem EKG-Test zur Datenbank hinzu.

    Speichert die EKG-Datei in data/ekg_data/ mit dem Format nachname_id.txt,
    das Profilbild (falls vorhanden) in data/pictures/ und aktualisiert die person_db.json.

    Args:
        firstname: Vorname der Person
        lastname: Nachname der Person
        date_of_birth: Geburtsjahr als Integer
        gender: Geschlecht ('male' oder 'female')
        ekg_file_bytes: Inhalt der EKG-Textdatei als Bytes
        ekg_filename: Originaldateiname der EKG-Datei
        ekg_date: Datum des EKG-Tests (z.B. '24.6.2026')
        picture_bytes: Inhalt des Profilbilds als Bytes (optional)
        picture_filename: Originaldateiname des Profilbilds (optional)

    Returns:
        Erfolgsmeldung als String
    """
    persons = load_person_db()

    person_id = get_next_person_id(persons)
    ekg_id = get_next_ekg_id(persons)

    # ── EKG-Datei speichern (Format: nachname_id.txt) ─────────────────────
    os.makedirs("data/ekg_data", exist_ok=True)
    ext = os.path.splitext(ekg_filename)[1]
    ekg_save_path = f"data/ekg_data/{lastname.lower()}_{person_id}{ext}"
    with open(ekg_save_path, "wb") as f:
        f.write(ekg_file_bytes)

    # ── Profilbild speichern ──────────────────────────────────────────────
    if picture_bytes and picture_filename:
        os.makedirs("data/pictures", exist_ok=True)
        pic_ext = os.path.splitext(picture_filename)[1]
        picture_save_path = f"data/pictures/{lastname.lower()}_{person_id}{pic_ext}"
        with open(picture_save_path, "wb") as f:
            f.write(picture_bytes)
    else:
        picture_save_path = "data/pictures/default.jpg"

    # ── Neuen Eintrag erstellen ───────────────────────────────────────────
    new_person = {
        "id": person_id,
        "date_of_birth": date_of_birth,
        "firstname": firstname,
        "lastname": lastname,
        "picture_path": picture_save_path,
        "gender": gender,
        "ekg_tests": [
            {
                "id": ekg_id,
                "date": ekg_date,
                "result_link": ekg_save_path
            }
        ]
    }

    persons.append(new_person)
    save_person_db(persons)

    return f"{firstname} {lastname} wurde erfolgreich hinzugefügt (ID {person_id})."


def update_person(
    person_id: int,
    firstname: str,
    lastname: str,
    date_of_birth: int,
    gender: str,
    picture_bytes: bytes = None,
    picture_filename: str = None,
) -> str:
    """Aktualisiert die persönlichen Daten einer bestehenden Person.

    Überschreibt Vorname, Nachname, Geburtsjahr und Geschlecht in der
    person_db.json. EKG-Tests bleiben unverändert. Falls ein neues Bild
    hochgeladen wird, wird das alte überschrieben.

    Args:
        person_id: ID der zu aktualisierenden Person
        firstname: Neuer Vorname
        lastname: Neuer Nachname
        date_of_birth: Neues Geburtsjahr
        gender: Neues Geschlecht ('male' oder 'female')
        picture_bytes: Neues Profilbild als Bytes (optional)
        picture_filename: Dateiname des neuen Profilbilds (optional)

    Returns:
        Erfolgsmeldung als String
    """
    persons = load_person_db()

    for person in persons:
        if person["id"] == person_id:

            # ── Profilbild ersetzen falls neues hochgeladen ───────────────
            if picture_bytes and picture_filename:
                os.makedirs("data/pictures", exist_ok=True)
                pic_ext = os.path.splitext(picture_filename)[1]
                picture_save_path = f"data/pictures/person{person_id}{pic_ext}"
                with open(picture_save_path, "wb") as f:
                    f.write(picture_bytes)
                person["picture_path"] = picture_save_path

            # ── Persönliche Daten aktualisieren ───────────────────────────
            person["firstname"] = firstname
            person["lastname"] = lastname
            person["date_of_birth"] = int(date_of_birth)
            person["gender"] = gender

            save_person_db(persons)
            return f"{firstname} {lastname} wurde erfolgreich aktualisiert."

    return f"Person mit ID {person_id} nicht gefunden."


def delete_person(person_id: int) -> str:
    """Löscht eine Person samt EKG-Dateien und Profilbild aus der Datenbank.

    Entfernt den Eintrag aus person_db.json und löscht alle zugehörigen
    EKG-Dateien aus data/ekg_data/ sowie das Profilbild aus data/pictures/.

    Args:
        person_id: ID der zu löschenden Person

    Returns:
        Erfolgsmeldung als String
    """
    persons = load_person_db()

    person_to_delete = next((p for p in persons if p["id"] == person_id), None)
    if person_to_delete is None:
        return f"Person mit ID {person_id} nicht gefunden."

    # ── EKG-Dateien löschen ───────────────────────────────────────────────
    for ekg_test in person_to_delete.get("ekg_tests", []):
        ekg_path = ekg_test.get("result_link")
        if ekg_path and os.path.exists(ekg_path):
            os.remove(ekg_path)

    # ── Profilbild löschen (nur wenn nicht das Default-Bild) ──────────────
    picture_path = person_to_delete.get("picture_path", "")
    if picture_path and "default.jpg" not in picture_path and os.path.exists(picture_path):
        os.remove(picture_path)

    # ── Person aus Datenbank entfernen ────────────────────────────────────
    persons = [p for p in persons if p["id"] != person_id]
    save_person_db(persons)

    name = f"{person_to_delete['firstname']} {person_to_delete['lastname']}"
    return f"{name} wurde erfolgreich gelöscht."