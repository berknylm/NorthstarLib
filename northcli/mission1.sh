
python3 nc.py link 72 74 84
python3 nc.py delay "1"
python3 nc.py origin "40.8064456, 29.3560396" --all
python3 nc.py delay "1"
python3 nc.py arm --all
python3 nc.py delay "5"
python3 nc.py takeoff "10" --all
python3 nc.py delay "28"
python3 nc.py move "-4, -2, 8" 72
python3 nc.py move "0, -2, 12" 74
python3 nc.py move "4, -2, 8" 84
python3 nc.py delay "20"
python3 nc.py move "-4, -2, 10" 72
python3 nc.py move "0, -2, 10" 74
python3 nc.py move "4, -2, 10" 84
python3 nc.py delay "20"
python3 nc.py land --all
python3 nc.py delay "15"
python3 nc.py disarm --all
python3 nc.py kill --all




