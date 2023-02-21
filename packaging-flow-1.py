from pprint import pprint
from frictionless import describe
import pandas as pd
import json
import requests
import pipe

###########################################################################
# get the latest version of the heal json dd schema to populate the 
# heal csv dd template
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
         

heal_dd_df = pd.DataFrame(columns=my_df_col)

###########################################################################
# get the required fields from the heal json dd schema and put those 
# first in the heal csv dd template
###########################################################################

required_col = heal_dd_json_schema['required']

def everything_after(df, cols):
    another = df.columns.difference(cols, sort=False).tolist()
    return df[cols + another]

heal_dd_df = heal_dd_df.pipe(everything_after, required_col)

###########################################################################
# bring in a new tabular resource, infer minimal table schema/dd
###########################################################################

resource = describe('./package/data-snp-exp-1.csv')
resource.to_json('./package/data-snp-exp-1.resource.json')

with open('./package/data-snp-exp-1.resource.json','r') as f:
    data = json.loads(f.read())

df = pd.json_normalize(data, record_path=['schema','fields'])

###########################################################################
# write inferred dd to the heal csv dd template so that investigator
# can add information - make a more detailed dd
###########################################################################

heal_dd_df = pd.concat([heal_dd_df,df])
heal_dd_df.to_csv('./package/my_heal_dd_df.csv',index=False)

