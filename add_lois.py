from django.core.management import setup_environ
import nearbysources.settings as settings
import sys, json

if __name__ == "__main__":
    setup_environ(settings)

from nearbysources.questions.models import *

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        betriebe = json.load(f)['features']
    campaign = Campaign.objects.get(name=sys.argv[2])
    for b in betriebe:
        campaign.locations.add(LocationOfInterest(name=b["properties"]["Betriebsname"] + ", " + b["properties"]["Strasse"], lat=b["geometry"]["coordinates"][1], lng=b["geometry"]["coordinates"][0]))
        print b["properties"]["Betriebsname"]
