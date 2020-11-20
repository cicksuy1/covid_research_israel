import pandas as pd
import urllib.request
url = 'https://data.gov.il/api/3/action/datastore_search?resource_id=dcf999c1-d394-4b57-a5e0-9d014a62e046&limit=1&include_total=true'
fileobj = urllib.request.urlopen(url)
case_object = pd.read_json(fileobj)
totalcases=case_object.loc["total"]["result"]


fileobj= "https://data.gov.il/api/3/action/datastore_search?resource_id=dcf999c1-d394-4b57-a5e0-9d014a62e046&limit=50&records_format=csv"
results = pd.read_json(fileobj)
results