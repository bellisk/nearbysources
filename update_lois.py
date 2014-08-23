from django.core.management import setup_environ
from django.core.exceptions import *
import nearbysources.settings as settings
import sys, json

if __name__ == "__main__":
    setup_environ(settings)

from nearbysources.questions.models import *

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        betriebe = json.load(f)['features']
    campaign = Campaign.objects.get(name=sys.argv[2])
    n = 0
    
    for b in betriebe:
        lois = campaign.locations.filter(name=b["properties"]["Betriebsname"] + ", " + b["properties"]["Strasse"])
        if len(lois) != 0:
            print b["properties"]["Betriebsname"] + " already in database"
        else:
            campaign.locations.add(LocationOfInterest(name=b["properties"]["Betriebsname"] + ", " + b["properties"]["Strasse"], lat=b["geometry"]["coordinates"][1], lng=b["geometry"]["coordinates"][0]))
            print b["properties"]["Betriebsname"] + " added to database"
            n += 1

    lois = campaign.locations.all()
    print "No. of Betriebe in json: " + str(len(betriebe))
    print "No. of Betriebe in database: " + str(len(lois))
    print "No. of Betriebe just added to db: " + str(n)


    # finally, look through all lois to catch ones that have been removed
    m = 0
    for loi in campaign.locations.all():
        exists = False
        for b in betriebe:
            name = b["properties"]["Betriebsname"] + ", " + b["properties"]["Strasse"]
            if name == loi.name:
                exists = True
        if not exists:
            print loi.name + " no longer exists; deleting"
            loi.delete()
            m += 1
    print "No. of old Betriebe deleted: " + str(m)
