import overpy
import matplotlib.collections as mc
import numpy as np
import json
import matplotlib.pyplot as plt
import sarquicklook

api = overpy.Overpass()

lons = [-122.0, -121.0]
lats = [38.0, 39.5]

bbox=[lats[0],lons[0],lats[1],lons[1]]

query = """
[out:json][bbox:{0[0]},{0[1]},{0[2]},{0[3]}];
(
way["highway"="motorway"];
);
out center;
""".format(bbox)

roadfile = "SacramentoRoads.json"


sarfile = "Sacramento/s1a-iw-grd-vv-20230101t020006-20230101t020031-046584-059528-001_lon-122.15_-121.25_lat38.2_38.8.npz"

#sarfile = "Sacramento/s1a-iw-grd-vv-20230113t020005-20230113t020030-046759-059b08-001_lon-122.15_-121.25_lat38.2_38.8.npz"



try:
    with open(roadfile, "r") as iFile:
        roads = json.load(iFile)
    print("File loaded.")
except:
    print("Sending Query")
    result = api.query(query)

    print("Plotting")
    cnt = 0
    num = len(result.ways)
    roads = []
    for way in result.ways:
        cnt+=1
        print("{}/{}".format(cnt,num))
        nodes = way.get_nodes(resolve_missing=True)
        roads.append( [[float(node.lon), float(node.lat)] for node in nodes])
        #if cnt >= 10:
        #    break
    #roads = np.array(roads, dtype="float32")
    with open(roadfile, "w") as oFile:
        oFile.write(json.dumps(roads))

#print(roads)

sar = np.load(sarfile)
#print(sar.files)
#print(sar["lon"])

plons = [-121.75, -121.45]
plats = [38.4, 38.8]

fig, ax = plt.subplots(1,1, figsize=(10,8))
sarquicklook.quicklook(sar["lon"], sar["lat"], sar["data"], dd=1, xlim=plons, ylim=plats, fig=fig, ax=ax)
lc = mc.LineCollection(roads, colors="m")
ax.add_collection(lc)
ax.axis('equal')
ax.set_xlim(plons[0], plons[1])
ax.set_ylim(plats[0], plats[1])
plt.show()
