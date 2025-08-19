
#LINK
python3 nc.py delay "1"
python3 nc.py origin "40.8038103, 29.358119" --all
python3 nc.py delay "1"

#ARM
python3 nc.py arm --all
python3 nc.py delay "10"

#TAKEOFF
python3 nc.py takeoff "10" --all
python3 nc.py delay "25"

#ARROW 10 SECONDS
python3 nc.py move "-5, 0, 7" 72
python3 nc.py move "0, 0, 12" 74
python3 nc.py move "5, 0, 7" 82
python3 nc.py delay "15"

#LINE 10 SECONDS
python3 nc.py move "-5, 0, 10" 72
python3 nc.py move "0, 0, 10" 74
python3 nc.py move "5, 0, 10" 82
python3 nc.py delay "15"

#LAND
python3 nc.py land --all
python3 nc.py delay "20"
python3 nc.py disarm --all
python3 nc.py kill --all