import graphene
from graphene import ObjectType, String, Field, List
from bson import ObjectId  # Pour gérer les ObjectId MongoDB
from database import users_collection  # Importer la collection MongoDB
import bcrypt  # Pour hacher les mots de passe


# Définition du modèle GraphQL User
class User(ObjectType):
    id = String(required=True)  # ID sous forme de chaîne (car MongoDB utilise ObjectId)
    username = String(required=True)
    email = String(required=True)


# Mutation pour créer un utilisateur
class RegisterUser(graphene.Mutation):
   class Arguments:
      username = graphene.String(required=True)
      email = graphene.String(required=True)
      password = graphene.String(required=True)

   success = graphene.Boolean()
   message = graphene.String()
   user = graphene.Field(User)  # Ajouter le champ user

   def mutate(self, info, username, email, password):
      # Vérifier si l'utilisateur existe déjà
      if users_collection.find_one({"email": email}):
         return RegisterUser(success=False, message="Email déjà utilisé.", user=None)

      # Hacher le mot de passe
      hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

      # Insérer l'utilisateur dans la base de données
      new_user = {
         "username": username,
         "email": email,
         "password": hashed_password.decode('utf-8')
      }
      inserted_user = users_collection.insert_one(new_user)

      # Vérifier si l'insertion a réussi
      if not inserted_user.inserted_id:
         return RegisterUser(success=False, message="Échec de l'inscription.", user=None)

      # Récupérer l'utilisateur inséré
      created_user = users_collection.find_one({"_id": inserted_user.inserted_id})

      return RegisterUser(
         success=True,
         message="Utilisateur inscrit avec succès.",
         user=User(
               id=str(created_user["_id"]),
               username=created_user["username"],
               email=created_user["email"]
         )
      )

# Définition des requêtes
class Query(ObjectType):
   users = List(User)

   def resolve_users(self, info):
      users_from_db = users_collection.find()
      return [
         User(id=str(user["_id"]), username=user["username"], email=user["email"])
         for user in users_from_db
      ]

# Définition des mutations
class Mutation(ObjectType):
   register_user = RegisterUser.Field()


# Création du schéma GraphQL
schema = graphene.Schema(query=Query, mutation=Mutation)