import pandas as pd

data = pd.read_csv('nov_jan_positions.csv', index_col=0)
names = set(data['trader'].tolist())
new_data = pd.DataFrame()

ids = []
for username in names:
    positions_db = pd.read_csv('nov_jan_positions.csv', index_col=0)
    user_positions = positions_db[positions_db['trader'] == username]
    descriptions = []
    for index, row in user_positions.iterrows():
        descriptions.append(row['description'])
    descriptions = list(set(descriptions))
    open_descriptions = []
    for description in descriptions:
        same_trades = user_positions[user_positions['description'] == description]
        qty = 0
        for index, pos in same_trades.iterrows():
            qty += pos['quantity']
        if qty > 0 or qty < 0:
            ids.append(pos['id'])
            open_descriptions.append((qty, description))
print(data)
def check_id(row):
    if row in ids:
        return True
    return False
data['newcol'] = data['id'].apply(check_id)
new_data = data[data['newcol']]
new_data['nextcol'] = new_data['description'].apply(lambda x:  'Mar' in x or 'Apr' in x or 'May' in x or 'Jun' in x or 'Jul' in x)
new_data = new_data[new_data['nextcol']]
new_data['time'] = "2021-02-01 01:59:10"
new_data.drop('newcol', axis=1, inplace=True)
new_data.drop('nextcol', axis=1, inplace=True)
new_data.to_csv('extranew.csv')