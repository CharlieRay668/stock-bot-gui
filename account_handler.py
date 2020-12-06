import pandas as pd

class AccountHandler():

    def __init__(self):
        self.database = 'accounts_db.csv'
        self.columns = ['holder', 'port_value', 'default_type', 'tradingview']

    def check_existnace(self, index):
        df = self.get_db()
        row = df[df['holder'] == index]
        return len(row) > 0

    def view_account(self, index):
        df = self.get_db()
        row = df[df['holder'] == index]
        if len(row) < 1:
            return 404, 'Unable to find specified row'
        true_index = row.index.values
        if len(true_index) > 1:
            return 501, 'Too many matches'
        true_index = true_index[0]
        try:
            return_dict = df.loc[true_index].to_dict()
            return 200, return_dict
        except:
            return 500, 'Something went wrong'

    def get_db(self):
        return pd.read_csv(self.database, index_col = 0)

    def get_value(self, index, col):
        df = self.get_db()
        row = df[df['holder'] == index]
        if len(row) < 1:
            return 404, 'Unable to find specified row'
        true_index = row.index.values
        if len(true_index) > 1:
            return 501, 'Too many matches'
        true_index = true_index[0]
        try:
            return_value = df.loc[true_index, col]
            return 200, return_value
        except KeyError:
            return 403, 'Unable to find specified column'
        return 500, 'Something went wrong'

    def edit_value(self, index, col, value):
        if type(value) is not float and type(value) is not int:
            if len(value) == 0:
                return 400, 'No value provided'
        df = self.get_db()
        row = df[df['holder'] == index]
        if len(row) < 1:
            return 404, 'Unable to find specified row'
        true_index = row.index.values
        if len(true_index) > 1:
            return 501, 'Too many matches'
        true_index = true_index[0]
        try:
            df.loc[true_index, col] = value
            df.to_csv(self.database)
            return 200, 'Success'
        except KeyError:
            return 403, 'Unable to find specified column'
        return 500, 'Something went wrong'

    def edit_row(self, index, new_row):
        if len(new_row) < 4:
            return 400, 'Not enough values provided'
        if len(new_row) < 5:
            new_row.append(None)
        df = self.get_db()
        row = df[df['holder'] == index]
        if len(row) < 1:
            return 404, 'Unable to find specified row'
        true_index = row.index.values
        if len(true_index) > 1:
            return 501, 'Too many matches'
        true_index = true_index[0]
        try:
            print(new_row)
            df.loc[true_index] = new_row
            print(df.loc[true_index])
            df.to_csv(self.database)
            return 200, 'Success'
        except KeyError:
            return 403, 'Unable to find specified column'
        return 500, 'Something went wrong'

    def add_row(self, row):
        df = self.get_db()
        new_df = pd.DataFrame([row], columns = df.columns)
        df = df.append(new_df, ignore_index = True)
        df.to_csv(self.database)
        return 200, 'Success'
        
    def remove_row(self, index):
        df = self.get_db()
        row = df[df['holder'] == index]
        if len(row) < 1:
            return 404, 'Unable to find specified row'
        true_index = row.index.values
        if len(true_index) > 1:
            return 501, 'Too many matches'
        true_index = true_index[0]
        try:
            df.drop([true_index], inplace=True)
            df.to_csv(self.database)
            return 200, 'Success'
        except:
            return 500, 'Something went wrong'
        return 500, 'Something went wrong'
