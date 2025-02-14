from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Remplace par ton URI si nécessaire
db = client["planning_poker"]  # Nom de la base de données
users_collection = db["users"]  # Collection des utilisateurs