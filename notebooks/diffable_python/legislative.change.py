# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all
#     notebook_metadata_filter: all,-language_info
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# During the last decade, controlled drugs legislation has been amended on various occasions due to concerns. In tis notebook we will set out to examine the impact of reclassification on Prescribing Patterns
#
# - [Gabapentinoids](#gaba)
# - [Tramadol](#tramadol)
# - [Zopiclone](#zdrugs) ->NOT STARTED YET
# - [Overall Summary](#summ) -> NOT STARTED YET
#
#

#import libraries required for analysis
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from ebmdatalab import bq
import os

# # Gabapentinoids <a id='gaba'></a>
# In April 2019 Gabapentinoids (i.e. pregabaln and gabapentin) were reclassified under the misuse of drugs act. This followed the [Advisory Committee of Misuse of Drugs recommending reclassification due to their concerns](https://www.gov.uk/government/news/pregabalin-and-gabapentin-to-be-controlled-as-class-c-drugs) over rising prescribing, misuse and deaths associated with both medicines. The reclassification we intended to bring in stronger controls and reduce the chances of medicines being used inapprorpiately.
#
# On OpenPrescribing we have various measures on gabapentinoid prescribing including including a measure of total use by using [Daily Defined Doses (DDD) to include both medicines in a single measure](https://openprescribing.net/measure/gabapentinoidsddd/).
#

# +
sql1 = '''
SELECT
  month,
  pct_id,
  sum(numerator) as total_gaba,
FROM
  `ebmdatalab.measures.ccg_data_gabapentinoidsddd` AS p
GROUP BY
month,
pct_id
'''

df_gaba = bq.cached_read(sql1, csv_path=os.path.join('..', 'data', 'df_gaba.csv'))
df_gaba['month'] = pd.to_datetime(df_gaba['month'])
df_gaba.rename(columns={'pct_id':'pct'}, inplace=True) ##prep for maps library whe  pct must be colum name
df_gaba.head(5)



# -

ax = df_gaba.groupby(["month"])['total_gaba'].sum().plot(kind='line', title="Total Gabapentinoids DDD")
ax.axvline(pd.to_datetime('2019-04-01'), color='black', linestyle='--', lw=2) ##law change
plt.ylim(0, 30000000 )

# # Tramadol <a id='tramadol'></a>

# In June 2014 tramdol was reclassified as a schedule 3 CD and the [ONS reported 5% drop in tramadol prescribing](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/deaths/bulletins/deathsrelatedtodrugpoisoninginenglandandwales/2015registrations) as well as the first fall in deaths related to tramadol since the first recorded death. The [Royal Pharmaceutical Society have a brefing here](https://www.rpharms.com/about-us/news/details/Rescheduling-of-gabapentin-and-pregabalin-to-Schedule-3-Controlled-Drugs-from-1-April-2019). OpenPrescribing item data goes back to 2011 but raw prescribing information only goes back to January 2014. We will do a two step analysis
# 1. Assess overall change in items and cost (indicative of qty) 
#
# 2. a) Work our total amounts of mg of tramadol dispensed in raw data for six months prior to the change. <br />
#     b) Work out tablet quantities for the 50mg and 100mg

# +
sql2 = '''
SELECT
  month,
  bnf_name,
  bnf_code,
  SUM(items) AS total_items,
  SUM(actual_cost) AS total_cost
FROM
  ebmdatalab.hscic.normalised_prescribing AS rx
WHERE
 bnf_code LIKE '040702040%'
GROUP BY
  month,
  bnf_name,
  bnf_code
ORDER BY
  month
'''

df_tramadol = bq.cached_read(sql2, csv_path=os.path.join('..', 'data', 'df_tramadol.csv'))
df_tramadol['month'] = pd.to_datetime(df_tramadol['month'])
df_tramadol.head(5)
# -

ax = df_tramadol.groupby(["month"])['total_items'].sum().plot(kind='line', title="Total number of items for Tramadol")
ax.axvline(pd.to_datetime('2014-06-01'), color='black', linestyle='--', lw=2) ##law change
plt.ylim(0, 800000)

ax = df_tramadol.groupby(["month"])['total_cost'].sum().plot(kind='line', title="Total cost(£)  for Tramadol")
ax.axvline(pd.to_datetime('2014-06-01'), color='black', linestyle='--', lw=2) ##law change
plt.ylim(0, )

# +
#for prototype I'll just take a look at 50mg caps
sql3 = '''
SELECT
  month,
  bnf_name,
  bnf_code,
SUM(CASE
      WHEN SUBSTR(bnf_code,14,2)='AA' THEN quantity * 50 #Tramadol 50mg capsules
      WHEN SUBSTR(bnf_code,14,2)='AT' THEN quantity * 50 #Tramadol 50mg orodispersible tablets sugar free
      WHEN SUBSTR(bnf_code,14,2)='AG' THEN quantity * 50 #Tramadol 50mg modified-release capsules
      WHEN SUBSTR(bnf_code,14,2)='AY' THEN quantity * 50 #Tramadol 50mg modified-release tablets
      WHEN SUBSTR(bnf_code,14,2)='AF' THEN quantity * 50 #Tramadol 50mg soluble tablets sugar free
      ELSE 0 END) AS tramadol_mg
FROM
  ebmdatalab.hscic.normalised_prescribing
WHERE
 bnf_code LIKE '040702040%'
GROUP BY
  month,
  bnf_name,
  bnf_code
ORDER BY
  month
'''

df_raw_tramadol = bq.cached_read(sql3, csv_path=os.path.join('..', 'data', 'df_tramadol_raw.csv'))
df_raw_tramadol['month'] = pd.to_datetime(df_raw_tramadol['month'])
df_raw_tramadol.head(5)
# -

ax = df_raw_tramadol.groupby(["month"])['tramadol_mg'].sum().plot(kind='line', title="Total number of mg for Tramadol 50mg caps")
ax.axvline(pd.to_datetime('2014-06-01'), color='black', linestyle='--', lw=2) ##law change
plt.ylim(0, 3500000000 )

# # Z-Drugs <a id='zdrugs'></a>

# Here the change is about reducing the amount on prescription at any one time. WE should look at decreases as well as a measure of 28/30 day scripts.
#
# •	https://www.rpharms.com/about-us/news/details/Controlled-drug-changes--tramadol--lisdexamfetamine--zopiclone-and-zaleplon
#
#

# # Overall Summary <a id='summ'></a>
