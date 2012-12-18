# API de Moment

## Goal

Créer une API qui sera utilisée par les applications mobiles. Cette API donnera accès à toutes les informations dont les application ont besoin.



### Requirements

[Flask](http://flask.pocoo.org/) : microframework utilisé pour créer le serveur. Permet de prendre en charge les requetes http facilement. 
Pour installer ce microframework :

	easy_install Flask

[FlaskSQLAlchemy](http://packages.python.org/Flask-SQLAlchemy/) : Extension de Flask qui ajoute le support de [SQLAlchemy](http://www.sqlalchemy.org/) qui est un touil SQL Python. Pour l'installer :

	easy_install Flask-SQLAlchemy
	

### Configurations

Le projet contient un fichier `config.py` dans lequel sont spécifié toutes les variables de configuration. Variables qui changeront en fonction de l'environnement (de dev, ou prod)


