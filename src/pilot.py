
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_validate
from sklearn.compose import make_column_selector as selector
from sklearn.impute import MissingIndicator
from sklearn.impute import SimpleImputer

data = pd.read_csv('../data/LISS_example_input_data.csv', encoding='cp1252')
outcome = pd.read_csv('../data/LISS_example_groundtruth_data.csv')

# Defining an household id and dropping those which are nas.
data = data.rename(columns = {'nohouse_encr2019':'hh_id'})
# Identify columns to be dropped
columns_to_drop = [col for col in data.columns if col.startswith('nohouse_encr')]

# Drop the columns
data = data.drop(columns_to_drop, axis=1)

# Filtering out those households that do not have an household id.
data = data.loc[data['hh_id'].notna()]
outcome = outcome.merge(data[['nomem_encr','hh_id']], on = 'nomem_encr')

# Filtering out individuals where target (new_child) is na.
outcome = outcome.loc[outcome['new_child'].notna()]
data = data.loc[data['hh_id'].isin(outcome['hh_id'])]

# Dropping columns with only na values.
data = data.loc[:,data.isna().sum() != len(data)].copy()


outcome = pd.concat([outcome,data[['nomem_encr','hh_id']].assign(new_child = 0)], ignore_index=True)
outcome = outcome.sort_values(by = 'new_child', ascending = False)
outcome = outcome.drop_duplicates(subset = 'nomem_encr')
outcome = outcome.set_index(['hh_id','nomem_encr'])


# Setting the index.
data = data.set_index(['hh_id','nomem_encr'])


data = data.loc[:,['leeftijd2019',
          'geslacht',
          'positie2019',
          'aantalhh2019',
          'aantalki2019',
          'partner2019',
          'burgstat2019',
          'woonvorm2019',
          'woning2019',
          'sted2019',
          'belbezig2019',
          'brutoink2019',
          'brutoink_f2019',
          'netinc2019',
          'brutohh_f2019',
          'nettohh_f2019',
          'oplzon2019',
          'oplmet2019',
          'doetmee2019',
          'herkomstgroep2019',
          'simpc2019']]


# Impute missing values, and add features that flag missing values.
imputer = SimpleImputer(missing_values=np.nan, strategy='mean', fill_value=True, add_indicator=True)

# BE CAREFUL WITH THE FLAGS FOR MISSING VALUES IN THE COLUMN SELECTION.
# Selecting categorical columns.
categorical_columns_selector = selector(dtype_include = object)
# Getting the names of the categorical columns.
categorical_columns = categorical_columns_selector(data)
# Encoding the categorical columns.
encoder = OneHotEncoder(handle_unknown='ignore')

# Selecting numerical columns.
numerical_columns_selector = selector(dtype_include = "float64")
# Getting the name of the numerical columns.
numerical_columns = numerical_columns_selector(data)
# Scaling numerical columns.
scaler = StandardScaler()

# Probably not needed.
# # Create the object flagging missing values.
# missing_values = MissingIndicator()
# # Flagging na values.
# #flags = missing_values.fit_transform(data)
# # Get the feature names for the flags (columns spelled 'missing' + column name).
# names_columns_missing = missing_values.get_feature_names_out() 

preprocessor = ColumnTransformer(
    [
        ('on-hot-encoder',encoder,categorical_columns),
        ('standard_scaler',scaler,numerical_columns)
    ]
)

model = make_pipeline(imputer,preprocessor,LogisticRegression(max_iter=500))
# replace income by income categories if not available?

#cross_validate(model,data,outcome,cv = 5)


