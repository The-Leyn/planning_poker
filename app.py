from flask import Flask,render_template
from flask_graphql import GraphQLView
from graph import schema

# Création de l'application Flask
app = Flask(__name__)

app.add_url_rule("/graphql", view_func=GraphQLView.as_view(
   "graphql",
   schema=schema,
   graphiql=True  # Interface GraphiQL activée
))

@app.route("/")
def index():
    return "Hello Web 2"

@app.route("/register", methods=["GET","POST"])
def promo():
   return render_template("register.html")

if __name__ == "__main__":
   app.run(debug=True)