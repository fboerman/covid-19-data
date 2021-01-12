import pandas as pd

df_2weeks = pd.read_csv('RIVM_timeseries/gemeenten_2weken/latest.csv', skip_blank_lines=True, delimiter=';')
df=df_2weeks[['Gemnr', 'Gemeente', 'Bev_2020']]
df.sort_values('Gemnr', inplace=True)
df.drop_duplicates(subset=['Gemnr'],keep='first', inplace=True)
df.rename(columns={
    'Gemnr': 'Gemeentecode',
    'Gemeente': 'Gemeentenaam',
    'Bev_2020': 'Inwoneraantal'
}, inplace=True)
df.to_csv('RIVM_timeseries/gemeenten_inwoners.csv', index=False, sep=';')