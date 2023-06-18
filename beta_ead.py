import numpy as np
import pandas as pd
from statsmodels.genmod import families
from statsmodels.othermod.betareg import BetaModel
import statsmodels.formula.api as smf
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from statsmodels.tools.eval_measures import aic
from itertools import combinations

links = families.links

np.random.seed(0)

n = 1000
Months_on_Book = np.random.normal(50, 10, n)
utilisation_ratio = np.random.normal(0.6, 0.1, n)
Amount = np.random.normal(500, 100, n)
noise = np.random.uniform(-0.02, 0.02, n)
CCF = utilisation_ratio * 0.5 + Months_on_Book * 0.002 + noise
CCF = np.clip(CCF, 0, 1)

df = pd.DataFrame({'CCF': CCF, 'utilisation_ratio': utilisation_ratio, 'Months_on_Book': Months_on_Book, 'Amount': Amount})

thresholds = [0.5, 0.6]  # list of thresholds
amount_threshold = [400]  # threshold for Amount
model_types = ['beta', 'linear']
model_summary = []

for threshold, amount_thresh, model_type in combinations(thresholds + amount_threshold, model_types):
    df['group'] = np.where((df['utilisation_ratio'] > threshold) & (df['Amount'] > amount_thresh), 'Group1', 'Group2')

    model_summ_row = [threshold, amount_thresh, model_type]

    # Models for Group 1 and Group 2
    for group in df['group'].unique():
        df_group = df[df['group'] == group].copy()
        df_train, df_test = train_test_split(df_group, test_size=0.2, random_state=42)

        model = "CCF ~ utilisation_ratio + Months_on_Book"
       
        # Check the model type
        if model_type == 'beta':
            mod = BetaModel.from_formula(model, df_train, link_precision=links.identity())
        elif model_type == 'linear':
            mod = smf.ols(formula=model, data=df_train)
       
        res = mod.fit()

        # Add the fitted values as new columns in the original dataset and df_group
        df.loc[df_train.index, 'fitted_values_' + str(threshold) + '_' + str(amount_thresh) + '_' + model_type] = res.fittedvalues
        df.loc[df_test.index, 'fitted_values_' + str(threshold) + '_' + str(amount_thresh) + '_' + model_type] = res.predict(df_test)
        df_group['fitted_values'] = df['fitted_values_' + str(threshold) + '_' + str(amount_thresh) + '_' + model_type]

        # Calculate metrics
        r2 = r2_score(df_group['CCF'], df_group['fitted_values'])
        aic_val = aic(res.llf, df_group.shape[0], res.df_model)
        max_pval = max(res.pvalues)

        model_summ_row.extend([group, r2, aic_val, max_pval])

    model_summary.append(model_summ_row)

# Create a new dataframe for the model summary
df_model_summary = pd.DataFrame(model_summary, columns=['Threshold', 'Amount_Threshold', 'Model_Type', 'Group1', 'R2_1', 'AIC_1', 'Max_pval_1', 'Group2', 'R2_2', 'AIC_2', 'Max_pval_2'])
print(df_model_summary)
print(df)
