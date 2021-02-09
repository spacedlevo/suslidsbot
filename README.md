# SusLidBot

Bot created for a small friends server where we play Among Us. The bot has several features

## Reads Stats

Using OpenCV and PyTesseract, screenshots can be read and data save posted to a database. Credit to https://github.com/py-Tom/StatsAmongUs for this section of the code

## !whose_sus? command

Will pick a player from the database and a random sus sentence. These sentences can be user submitted. I have set it up that those who submit there stats to the database are given a role of Crewmate, and only Crewmates can add to the sus messages. 

## !leadeboard & !percent

Will create leaderboards from stats stored in the database. The !percent will present these as a per hundred game basis. 

## !wins 

Will calculate the percentage of wins as either crewmate or imposter depending on which is given as an argument.

# How to use

* Clone Repo
* Create Envirnoment
* `pip install -r requirements.txt`
* create a `.env` file and add variables for your `TOKEN` and `GUILD`
* Run `main.py` and follow discords instructions to adding bot to your server