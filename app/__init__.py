from flask import Flask


app=Flask(__name__,template_folder='./templates',static_folder="./static")
from config.db import SQLALCHEMY_DATABASE_URI,SQLALCHEMY_TRACK_MODIFICATIONS
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI']=SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=SQLALCHEMY_TRACK_MODIFICATIONS
db = SQLAlchemy(app)

from app.plugins import novel_index_plugin,novel_content_plugin,index_plugin,sitemap_plugin,other_index_plugin

app.register_blueprint(index_plugin.plugin)
app.register_blueprint(other_index_plugin.plugin)
app.register_blueprint(novel_index_plugin.plugin)
app.register_blueprint(novel_content_plugin.plugin)
app.register_blueprint(sitemap_plugin.plugin)