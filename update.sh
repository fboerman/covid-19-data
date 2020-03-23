#!/usr/bin/env bash

echo "[>] pulling RIVM data"
#csvlinknl=$(curl -s https://www.volksgezondheidenzorg.info/onderwerp/infectieziekten/regionaal-internationaal/coronavirus-covid-19 | tr '"' '\n' | grep '\.csv$')
#csvlinknl="https://www.volksgezondheidenzorg.info${csvlinknl}"
#cd nederland/RIVM
#currentdate=$(echo $csvlinknl | grep -oE '[0-9]{8}')
currentdate=$(date '+%d%m%Y')
currentdatecsv="nederland/RIVM/${currentdate}.csv"

if [[ ! -e $currentdatecsv ]]; then
	touch $currentdatecsv
fi
#wget --quiet $csvlinknl
./extract_current_csv_rivm.py > /tmp/$currentdate.csv

#echo "[*>] fix names of csv"
#cd nederland/RIVM
#for file in ./*.csv; do
#    [ -e "$file" ] || continue
#    name=${file##*/}
#    newname=$(echo $name | grep -oE '[0-9]{8}')
#    newname="${newname}.csv"
#    mv $name $newname 2> /dev/null
#done
#cd ../..

echo "[>] pulling johns hopkins data"
cd world/COVID-19
git_output=$(git pull)
cd ../../

echo "[>] writing data to grafana database"
echo "[*>] world"
if [[ "$git_output" != "Already up to date." ]]; then
	cd world
	./import.py
	cd ..
else
	echo "[*>] no changes detected"
fi

echo "[*> netherlands"
diff_output="$(diff /tmp/$currentdate.csv $currentdatecsv)"
HOUR=$(date +%H)
if [[ "0" != "${#diff_output}" ]]; then
	mv /tmp/$currentdate.csv $currentdatecsv
	cd nederland
	./import.py
	cd ..
	./push.sh
	if [[ $HOUR != 00 ]]; then
		#./extract_current_ziekenhuis_number.py
		cd /home/python/covid19bot/
		env/bin/python manage.py send_updates --rivmupdate
		cd /root/corona
	fi
else
	echo "[*>] no changes detected"
fi
