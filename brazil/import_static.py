#!/usr/bin/env python3

from db import engine
import pandas as pd
from regions import states

df = pd.DataFrame(states, columns=["name", "code", "region"])
df.to_sql('static_brazil_states', engine, if_exists='replace')
