from geopy import geocoders
import json

GEO_APP_KEY = ''
g = geocoders.Bing(GEO_APP_KEY)

#transforms = [('Greater ', ''), (' Area', '')]

with open("linkedin_lite.json", "r") as f:
    dataset = json.load(f)

for p in dataset:
    if not p.has_key('locality'):
        continue
    transformed_location = p['locality']
    #for transform in transforms:
    #    transformed_location = transformed_location.replace(*transform)
    geo = g.geocode(transformed_location, exactly_one = False)
    if geo == []:
        continue
    p['locality_code'] = list(geo[0])

data = json.dumps(dataset, indent=4)
with open("bing_location.json", "w") as ff:
    ff.write(data)