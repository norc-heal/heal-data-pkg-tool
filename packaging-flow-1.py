from pprint import pprint
from frictionless import describe
import pandas as pd
import json
import requests

###########################################################################
###########################################################################

heal_dd_json_schema_url = 'https://raw.githubusercontent.com/HEAL/heal-metadata-schemas/main/variable-level-metadata-schema/schemas/fields.json'
r = requests.get(heal_dd_json_schema_url)
heal_dd_json_schema = r.json()
print(heal_dd_json_schema)

my_df_col = []

for p in list(heal_dd_json_schema['properties'].keys()):
    if 'properties' in heal_dd_json_schema['properties'][p].keys():
        for p2 in list(heal_dd_json_schema['properties'][p]['properties'].keys()):
            my_df_col.append(p+'.'+p2)
    else:
        my_df_col.append(p)
         
my_df_col

###########################################################################
###########################################################################


resource = describe('./package/data-snp-exp-1.csv')
resource.to_json('./package/data-snp-exp-1.resource.json')

#df = pd.read_json('./package/data-snp-exp-1.resource.json')
#df.to_csv('./package/my_df.csv')
with open('./package/data-snp-exp-1.resource.json','r') as f:
    data = json.loads(f.read())

df = pd.json_normalize(data, record_path=['schema','fields'])
print(df)
#df.to_csv('./package/my_df.csv',index=False)

heal_dd_df = pd.DataFrame(columns=['name','type','description','title','module','format','encodings','constraints.enum'])
heal_dd_df
heal_dd_df['name'] = df['name']
heal_dd_df
heal_dd_df['type'] = df['type']
heal_dd_df
heal_dd_df.to_csv('./package/my_heal_dd_df.csv',index=False)

heal_dd_full_df = pd.DataFrame(columns=['name','type','description','title','module','format','encodings','constraints.enum'])
heal_dd_full_df
heal_dd_full_df['name'] = df['name']
heal_dd_full_df
heal_dd_full_df['type'] = df['type']
heal_dd_full_df
heal_dd_full_df.to_csv('./package/my_heal_dd_full_df.csv',index=False)

pprint(resource)
pprint(type(resource))
pprint(type(resource.schema.fields))
pprint(type(resource.schema.fields[0]))
pprint(type(json.dumps(resource.schema.fields[0])))

#pprint(pd.DataFrame(resource.schema.fields))
#pprint(pd.json_normalize(resource, record_path='fields'))

#pprint(pd.DataFrame.from_dict(resource.schema.fields))
#pprint(pd.DataFrame.from_records(resource.schema.fields))

df = pd.DataFrame(resource.schema.fields)
pprint(type(df))
df.to_csv('./package/my_df.csv')
