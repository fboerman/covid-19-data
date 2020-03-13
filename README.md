# Coronavirus (COVID-19) data
This repo contains scripts to gather and parse data about the COVID-19 virus pandemic as well as data from the Netherlands. It is used as input for data visualizations that are displayed at [https://data.boerman.dev/](https://data.boerman.dev/).

It contains daily downloaded csv files of the dutch government data of the RIVM as well as gitmodule to the datasource of the Johns Hopkins University. Their (much better) dashboard can be found [here](https://www.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6)

The ```update.sh``` script downloads and parses all data and writes it to database using the ```to_sql``` method of pandas. To specify your own database backend create a file in both ```nederland``` and ```world``` folder called ```db.py``` in which you define the sqlalchemy database client to use. Example for postgresql:  
```
from sqlalchemy import create_engine
engine = create_engine('postgresql://<user>:<password>@<host>:<port>/<dbname>')
```
For other examples see sqlalchemy documentation.

This repo will be updated automatically daily. For questions you can reach me at [frank@fboerman.nl](mailto:frank@fboerman.nl). More information about me or this project can be found at my blog at [https://boerman.dev/](https://boerman.dev/)

