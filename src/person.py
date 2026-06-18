import json
from datetime import date
from PIL import Image


def get_person_data():
    """Lädt alle Personen aus der JSON-Datenbank und gibt eine Liste von Person-Objekten zurück."""
    with open("data/person_db.json", "r", encoding="utf-8") as file:
        person_data = json.load(file)

    person_list = []
    for p in person_data:
        person_list.append(Person(
            id=p["id"],
            date_of_birth=p["date_of_birth"],
            firstname=p["firstname"],
            lastname=p["lastname"],
            picture_path=p["picture_path"],
            ekg_tests=p["ekg_tests"],
            gender=p.get("gender", "male")
        ))
    return person_list


def get_person_by_full_name(full_name, persons=None):
    """Gibt ein Person-Objekt anhand des vollen Namens (Format: 'Nachname, Vorname') zurück."""
    if persons is None:
        persons = get_person_data()
    parts = full_name.split(", ")
    lastname, firstname = parts[0], parts[1]
    for person in persons:
        if person.lastname == lastname and person.firstname == firstname:
            return person
    return None


class Person:

    def __init__(self, id: int, date_of_birth: int, firstname: str, lastname: str,
                 picture_path: str, ekg_tests: list, gender: str = "male"):
        self.id = id
        self.date_of_birth = int(date_of_birth)
        self.firstname = firstname
        self.lastname = lastname
        self.picture_path = picture_path
        self.ekg_tests = ekg_tests
        self.gender = gender

    @staticmethod
    def load_person_data():
        """Lädt die rohen Personen-Dictionaries aus der JSON-Datenbank."""
        with open("data/person_db.json", "r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def load_by_id(person_id: int):
        """Instanziiert ein Person-Objekt anhand der ID."""
        person_data = Person.load_person_data()
        for p in person_data:
            if p["id"] == person_id:
                return Person(
                    id=p["id"],
                    date_of_birth=p["date_of_birth"],
                    firstname=p["firstname"],
                    lastname=p["lastname"],
                    picture_path=p["picture_path"],
                    ekg_tests=p["ekg_tests"],
                    gender=p.get("gender", "male")
                )
        return None

    def get_full_name(self) -> str:
        """Gibt den vollen Namen im Format 'Nachname, Vorname' zurück."""
        return f"{self.lastname}, {self.firstname}"

    def calc_age(self) -> int:
        """Berechnet das aktuelle Alter basierend auf dem Geburtsjahr."""
        current_year = date.today().year
        return current_year - self.date_of_birth

    def calc_max_heart_rate(self) -> int:
        """Berechnet die maximale Herzfrequenz basierend auf Alter und Geschlecht.
        
        Formel:
        - Männer: 220 - Alter
        - Frauen: 226 - Alter
        """
        age = self.calc_age()
        if self.gender.lower() in ("female", "w", "weiblich"):
            return 226 - age
        else:
            return 220 - age

    def get_image(self):
        """Lädt und gibt das Profilbild der Person zurück."""
        return Image.open(self.picture_path)


if __name__ == "__main__":
    persons = get_person_data()
    for p in persons:
        print(f"{p.get_full_name()} | Alter: {p.calc_age()} | Max HR: {p.calc_max_heart_rate()}")
