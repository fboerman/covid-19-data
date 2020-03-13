#!/usr/bin/env bash

echo "[>] pulling RIVM data"
#csvlinknl=$(curl -s https://www.volksgezondheidenzorg.info/onderwerp/infectieziekten/regionaal-internationaal/coronavirus-covid-19 | tr '"' '\n' | grep '\.csv$')
#csvlinknl="https://www.volksgezondheidenzorg.info${csvlinknl}"
#cd nederland/RIVM
#currentdate=$(echo $csvlinknl | grep -oE '[0-9]{8}')
currentdate=$(date '+%d%m%Y')
currentdatecsv="nederland/RIVM/${currentdate}.csv"
rm $currentdatename 2> /dev/null
#wget --quiet $csvlinknl
./extract_current_csv_rivm.py > $currentdatecsv


echo "[*>] fix names of csv"
cd nederland/RIVM
for file in ./*.csv; do
    [ -e "$file" ] || continue
    name=${file##*/}
    newname=$(echo $name | grep -oE '[0-9]{8}')
    newname="${newname}.csv"
    mv $name $newname 2> /dev/null
done
cd ../..

echo "[>] pulling johns hopkins data"
cd world/COVID-19
git pull
cd ../../

echo "[>] writing data to grafana database"
echo "[*>] world"
cd world
./import.py
echo "[*> netherlands"
cd ../nederland
./import.py
