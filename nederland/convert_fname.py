import os
from datetime import datetime

for fname in os.listdir("RIVM_timeseries"):
    print(fname)
    new_fname = datetime.strptime(fname.split('.')[0], "%d%m%Y").strftime('%Y-%m-%d') + ".csv"
    os.rename(f"RIVM_timeseries/{fname}", f"RIVM_timeseries/{new_fname}")
