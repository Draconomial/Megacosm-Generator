"""`main` is the top level module for this application."""

# Import the stuffs!
from flask import Flask, send_file, render_template, request, url_for
from generators import Planet, NPC, MagicItem, Deity, Bond
from util.MakeMap import *
from util.Seeds import *
from util import Filters
import random
import redis
import ConfigParser
import pprint
import json
import os
import sys
import inflect
import re
from pprint import pprint

p = inflect.engine()

MAPWIDTH=500
MAPHEIGHT=300

config = ConfigParser.RawConfigParser()
config.read( 'data/config.ini')

url = config.get('redis', 'url')
server=redis.from_url(url)

#pool = redis.ConnectionPool(host=config.get('redis', 'host'), port=config.get('redis', 'port'), db=0, password=config.get('redis', 'password'),   )
#server = redis.Redis(connection_pool=pool)    

# This thing here.. does stuff.
app = Flask(__name__)

@app.route('/')
def indexpage():
    """This is the first page anyone sees."""
    return render_template('index.html') 


@app.route('/magic_item')
def GenerateMagicItem():
    """Generate a MagicItem"""
    seed=set_seed( request.args.get('seed') )

    print "MAH SEED:",seed

    magicitemfeatures={'seed':seed,}
    for param in request.args :
        if re.match('^magicitem_[a-z_]+_roll$',param) and int(request.args[param])>=0 and int(request.args[param])<=100 :
            print "param is",param,"=",request.args[param]
            magicitemfeatures[param]=int(request.args[param])
        elif re.match('^magicitem_kind$',param) and request.args[param] in server.lrange('magicitem_kind',0,-1):
            magicitemfeatures['kind']=request.args[param]

    magicitem=MagicItem.MagicItem(server, magicitemfeatures)
    kind= magicitem.kind
    return render_template('magicitem_'+kind+'.html',magicitem=magicitem) 

@app.route('/npc')
def GenerateNPC():
    """Generate an NPC"""
    seed=set_seed( request.args.get('seed') )

    npcfeatures={'seed':seed,}

    races=server.lrange('race',0,-1);
    professions=server.lrange('npc_profession',0,-1);
    attitudes=server.lrange('npc_attitude',0,-1);
    motivations=server.lrange('npc_motivation',0,-1);
    emotions=server.lrange('npc_emotion',0,-1);
    for param in request.args :
        if re.match('^npc_[a-z_]+_roll$',param) and int(request.args[param])>=0 and int(request.args[param])<=100 :
            print "param is",param,"=",request.args[param]
            npcfeatures[param]=int(request.args[param])
        elif re.match('^npc_race$',param) and request.args[param] in races:
            npcfeatures['race']=request.args[param]
        elif re.match('^npc_profession$',param) and request.args[param] in professions:
            npcfeatures['profession']=request.args[param]
        elif re.match('^npc_attitude$',param) and request.args[param] in attitudes:
            npcfeatures['attitude']=request.args[param]
        elif re.match('^npc_motivation$',param) and request.args[param] in motivations:
            npcfeatures['motivation']=request.args[param]
        elif re.match('^npc_emotion$',param) and request.args[param] in emotions:
            npcfeatures['emotion']=request.args[param]

    npc=NPC.NPC(server,npcfeatures)
    return render_template('npc.html',npc=npc) 

@app.route('/npc_builder')
def NPC_Builder():
    """Generate an NPC"""

    stats=server.lrange('npcstats',0,-1)
    statinfo={}
    races=server.lrange('race',0,-1);
    professions=server.lrange('npc_profession',0,-1);
    attitudes=server.lrange('npc_attitude',0,-1);
    motivations=server.lrange('npc_motivation',0,-1);
    emotions=server.lrange('npc_emotion',0,-1);
    for stat in stats :
        statinfo[stat]=[]
        for statstring in server.zrange('npc_'+stat,0,-1):
            statinfo[stat].append(json.loads(statstring))
    
    return render_template('npc_builder.html',statinfo=statinfo, otherstats={'race':races,'profession':professions,'attitude':attitudes,'motivation':motivations,'emotion':emotions}) 

@app.route('/planet_builder')
def Planet_Builder():
    """Generate the basic data about a planet"""

    stats=server.lrange('planetstats',0,-1)
    statinfo={}

    for stat in stats :
        statinfo[stat]=[]
        for statstring in server.zrange('planet_'+stat,0,-1):
            print "looking at planet_",stat, statstring
            statinfo[stat].append(json.loads(statstring))
    
    return render_template('planet_builder.html',statinfo=statinfo) 


@app.route('/planet')
def GeneratePlanet():
    """Generate the basic data about a planet"""
    seed=set_seed( request.args.get('seed') )

    print "MAH SEED:",seed

    planetfeatures={'seed':seed,}

    for param in request.args :
        if re.match('^planet_[a-z_]+_roll$',param) and int(request.args[param])>=0 and int(request.args[param])<=100 :
            print "param is",param,"=",request.args[param]
            planetfeatures[param]=int(request.args[param])

    planet=Planet.Planet(server,planetfeatures)

    return render_template('planet.html', planet=planet )


@app.route('/bond')
def GenerateBond():
    """Generate a simple bond"""
    seed=set_seed( request.args.get('seed') )

    print "MAH SEED:",seed

    bondfeatures={'seed':seed,}

    for param in request.args :
        if re.match('^bond_[a-z_]+_roll$',param) and int(request.args[param])>=0 and int(request.args[param])<=100 :
            print "param is",param,"=",request.args[param]
            bondfeatures[param]=int(request.args[param])
        elif re.match('^bond_template_id$',param)  and int(request.args[param])>=0 and int(request.args[param]) < server.llen('bond_template'):
            bondfeatures['template']=server.lrange('bond_template', int(request.args[param]), int(request.args[param]) )[0]
        elif re.match('^bond_when_id$',param)  and int(request.args[param])>=0 and int(request.args[param]) < server.llen('bond_when'):
            bondfeatures['when']=server.lrange('bond_when', int(request.args[param]), int(request.args[param]) )[0]
        elif re.match('^bond_[a-zA-Z]*$',param)  and re.match('^[a-zA-Z\']+$', request.args[param]):
            fieldname=param.split('_',2)[1]
            bondfeatures[fieldname]=request.args[param]

    bond=Bond.Bond(server,bondfeatures)

    return render_template('bond.html', bond=bond )

@app.route('/bond_builder')
def Bond_Builder():
    """Generate the basic data about a bond"""

    statinfo={}
    for stat in ['when', 'template']:
        statinfo[stat]=[]
        for statstring in server.lrange('bond_'+stat,0,-1):
            print "looking at bond_",stat, statstring
            statinfo[stat].append(statstring)
    
    return render_template('bond_builder.html',statinfo=statinfo) 


@app.route('/deity')
def GenerateDeity():
    """Generate a Deity"""
    seed=set_seed( request.args.get('seed') )

    print "MAH SEED:",seed

    deityfeatures={'seed':seed,}
    for param in request.args :
        if re.match('^deity_[a-z_]+_roll$',param) and int(request.args[param])>=0 and int(request.args[param])<=100 :
            print "param is",param,"=",request.args[param]
            deityfeatures[param]=int(request.args[param])

    deity=Deity.Deity(server, deityfeatures)
    return render_template('deity.html',deity=deity) 


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404

@app.errorhandler(500)
def page_borked(e):
    """Return a custom 500 error. Only hit when debugging is off."""
    message="You Broke it!"
    return message, 500

@app.template_filter('article')
def select_article(s):
    return Filters.select_article(s)

@app.template_filter('pluralize')
def select_pluralize(s):
    return Filters.select_pluralize(s)


if __name__ == '__main__':
    app.debug = True
    app.run()




