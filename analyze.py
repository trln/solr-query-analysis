#!/usr/bin/env python

import os
import pandas as pd
import re

host_data = {}
cols = []

primary = None

for x in sorted([os.path.join('results', x) for x in os.listdir('results') if x.endswith('.csv')]):
    df = pd.read_csv(x)
    if primary is None:
        primary = df
    else:
        primary = primary.append(df)

print(primary[['host', 'test_type', 'querylen', 'num_clauses', 'time', 'result_count']].groupby(['host', 'test_type', 'querylen']).agg({ 'time': ['mean', 'min', 'max'], 'num_clauses': ['mean'], 'result_count': ['mean']}))
    

