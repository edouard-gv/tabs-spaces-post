import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

#Data IN
df = pd.read_csv('developer_survey_2017/survey_results_public.csv')

#Filtering
# -- learning notna()
max(df[df.Salary.notna()].Salary)

df = df[df.Salary.notna()]
df = df[df.TabsSpaces.notna()]

df['Country'].unique();
df['TabsSpaces'].unique();

# The problem
# -- learning pivot table
df.pivot_table(index='TabsSpaces', values='Salary')
df.pivot_table(index='TabsSpaces', values='Respondent', aggfunc=pd.Series.count)
df.pivot_table(index='TabsSpaces', values='Respondent', aggfunc="count")

# -- learning inner join on indices, just to see
df.pivot_table(index='TabsSpaces', values='Salary').\
    merge(
        df.pivot_table(index='TabsSpaces', values='Respondent', aggfunc=pd.Series.count),
        left_index=True,
        right_index=True)

# First thing, distribution
# -- learning distribution
sns.distplot(df.Salary, hist=False)

# -- learning filter
sns.distplot(df[df.TabsSpaces == 'Spaces'].Salary,  label='Spaces', hist=False)

for strategy in df.TabsSpaces.unique():
    sns.distplot(df[df.TabsSpaces == strategy].Salary, label=strategy, hist=False)

# A. Let's understand the two bumps : maybe countries?

# Selecting only top countries
countryS = df.pivot_table(index='Country', values='Respondent', aggfunc="count").sort_values('Respondent', ascending=False)\
    .head(10).index

len(df)
len(df[df.Country.isin(countryS)])

for country in countryS:
    sns.distplot(df[df.Country == country].Salary, label=country, hist=False)

# Something wierd for these countries
for country in ['Poland', 'Germany', 'France']:
    sns.distplot(df[df.Country == country].Salary, label=country, hist=False)

# -Haha, let's assume people mix with their monthly salaries in these countries
# => Remove salaries above the sixth of the mean for each countries

# -- learning groupby()
df.groupby(['Country']).size()['France']
df.groupby(['Country']).Salary.mean()['France']

salaryM = df.groupby(['Country']).Salary.mean()
df['SalaryM'] = df.Country.apply(lambda c: salaryM[c])

df[['SalaryM', 'Country']]

# -- trying a simpler way (from https://stackoverflow.com/questions/30757272/pivot-each-group-in-pandas)
df = df.set_index(['Country'])
df['SalaryM2'] = df.groupby(['Country']).Salary.mean()
df = df.reset_index()

(df['SalaryM2'] - df['SalaryM']).unique()

# removing lower salaries
dfs = df[df.Salary >= df.SalaryM / 6]

# comparing means after removing lower salaries
df.pivot_table(index='TabsSpaces', values='Salary')
dfs.pivot_table(index='TabsSpaces', values='Salary')

df.pivot_table(index='TabsSpaces', values='Salary').merge(
    dfs.pivot_table(index='TabsSpaces', values='Salary'),
    left_index=True, right_index=True)

# comparing distribution after removing lower salaries

for strategy in df.TabsSpaces.unique():
    sns.distplot(df[df.TabsSpaces == strategy].Salary, label="raw "+strategy, hist=False, kde_kws={'shade': True})

for strategy in dfs.TabsSpaces.unique():
    sns.distplot(dfs[dfs.TabsSpaces == strategy].Salary, label=strategy, hist=False, kde_kws={"lw": 3})

for country in countryS:
    sns.distplot(dfs[dfs.Country == country].Salary, label=country, hist=False)

# B Hypothesis: its cultural (ie depending on countries)
# we show only data concerning top 10 countries
top_countries_dfs = df[df.Country.isin(countryS)]

# First type of graphs
dfgg = top_countries_dfs.groupby(['Country', 'TabsSpaces'])
dfgg.Salary.mean().plot(kind='bar')

# Better with pivot tables
top_countries_dfs.pivot_table(index='Country', columns='TabsSpaces', values='Salary').plot(kind='bar')

# - learning to count (by default values are meaned)
top_countries_dfs.pivot_table(index='Country', columns='TabsSpaces', values='Respondent', aggfunc="count").plot(kind='bar')

for strategy in dfs.TabsSpaces.unique():
    sns.distplot(df[(df.TabsSpaces == strategy) & (df.Country == 'India')].Salary, label="India "+strategy, hist=False, kde_kws={'shade': True})

for strategy in dfs.TabsSpaces.unique():
    sns.distplot(df[(df.TabsSpaces == strategy) & (df.Country == 'United States')].Salary, label="US "+strategy, hist=False)

#
# C Let's find if there is a variable that correlates with tabsspaces.
dfs.pivot_table(index='JobSatisfaction',  columns='TabsSpaces',values='Respondent', aggfunc="count")[['Spaces', 'Tabs', 'Both']].plot(kind='bar')
dfs.pivot_table(index='PronounceGIF',  columns='TabsSpaces', values='Respondent', aggfunc="count")[['Spaces', 'Tabs', 'Both']].plot(kind='bar')
dfs.pivot_table(index='VersionControl',  columns='TabsSpaces', values='Respondent', aggfunc="count")[['Spaces', 'Tabs', 'Both']].plot(kind='bar')

dfs.ProgramHobby.unique()
dfs['OpenSourceContributor'] = (dfs.ProgramHobby.apply(lambda s: s == "Yes, I contribute to open source projects" or s == "Yes, both"))
dfs.pivot_table(index='OpenSourceContributor', columns='TabsSpaces', values='Respondent', aggfunc="count")[['Spaces', 'Tabs', 'Both']].plot(kind='bar')
dfs.pivot_table(index='OpenSourceContributor', columns='TabsSpaces', values='Salary')[['Spaces', 'Tabs', 'Both']].plot(kind='bar')

dfs.YearsProgram.unique()
dfs.YearsProgram.apply(lambda s: (np.NaN if type(s) != str else 0 if s == "Less than a year" else int(s.split(" ")[0]))).unique()

# and look if the difference stays all along the life of a developer
dfs['YearsProgramI'] = dfs.YearsProgram.apply(lambda s: (np.NaN if type(s) != str else 0 if s == "Less than a year" else int(s.split(" ")[0])))
dfs.pivot_table(index='YearsProgramI',  columns='TabsSpaces', values='Salary')[['Spaces', 'Tabs', 'Both']].plot(kind='line')

dfs.YearsProgramI.apply(type).unique()

dfs['YearsProgramG'] = dfs.YearsProgramI.apply(lambda i: (np.NaN if type(i) != float
                                                         else "a) 0-4" if i <5
                                                         else "b) 5-9" if i<10
                                                         else "c) 10-14" if i<15
                                                         else "d) 15-19" if i <20
                                                         else "e) >20"))

dfs.YearsProgramG.unique()

dfs.pivot_table(index='YearsProgramG',  columns='TabsSpaces', values='Salary')[['Spaces', 'Tabs', 'Both']].plot(kind='line')

dfs.YearsCodedJob.unique()
dfs['YearsCodedJobI'] = dfs.YearsCodedJob.apply(lambda s: (0 if s == "Less than a year" else np.NaN if type(s) != str else int(s.split(" ")[0])))

dfs['YearsCodedJobG'] = dfs.YearsCodedJobI.apply(lambda i: (np.NaN if type(i) != float
                                                         else "a) 0-4" if i <5
                                                         else "b) 5-9" if i<10
                                                         else "c) 10-14" if i<15
                                                         else "d) 15-19" if i <20
                                                         else "e) >20"))

dfs.pivot_table(index='YearsCodedJobI',  columns='TabsSpaces', values='Salary')[['Spaces', 'Tabs', 'Both']].plot(kind='line')
dfs.pivot_table(index='YearsCodedJobG',  columns='TabsSpaces', values='Salary')[['Spaces', 'Tabs', 'Both']].plot(kind='line')

dfs.pivot_table(index='YearsCodedJobI', columns=['TabsSpaces', 'OpenSourceContributor'], values='Salary')[['Spaces', 'Tabs', 'Both']].plot(kind='line')
dfs.pivot_table(index='YearsCodedJobG', columns=['TabsSpaces', 'OpenSourceContributor'], values='Salary')[['Spaces', 'Tabs', 'Both']].plot(kind='line')



