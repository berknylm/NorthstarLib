#LINK
python3 nc.py link 72 74 82
python3 nc.py delay "1"
python3 nc.py origin "40.8038103, 29.358119" --all
python3 nc.py delay "1"

#ARM
python3 nc.py arm --all
python3 nc.py delay "5"

#TAKEOFF
python3 nc.py takeoff "10" --all
python3 nc.py delay "30"

#LAND
python3 nc.py land --all
python3 nc.py delay "20"
python3 nc.py disarm --all
python3 nc.py kill --all