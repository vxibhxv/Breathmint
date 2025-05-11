import json
from pathlib import Path

class Character:
    def __init__(self, name, level, health, skills):
        self.name = name
        self.level = level
        self.health = health
        self.skills = skills

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            level=data["level"],
            health=data["health"],
            skills=data["skills"]
        )

    def to_dict(self):
        return {
            "name": self.name,
            "level": self.level,
            "health": self.health,
            "skills": self.skills
        }

class CharacterManager:
    def __init__(self, json_path):
        self.json_path = Path(json_path)
        self.characters = self._load_characters()

    def _load_characters(self):
        if self.json_path.exists():
            with open(self.json_path, 'r') as f:
                return json.load(f)
        return {}

    def get_character(self, key):
        data = self.characters.get(key)
        return Character.from_dict(data) if data else None

    def update_character(self, key, character):
        self.characters[key] = character.to_dict()

    def save(self):
        with open(self.json_path, 'w') as f:
            json.dump(self.characters, f, indent=2)


