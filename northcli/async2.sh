
#python3 nc.py link 72 74 82
python3 nc.py delay "1"

python3 nc.py set arm --all
python3 nc.py set delay "10" --all
python3 nc.py set origin "40.8040946, 29.3564791" --all
python3 nc.py set delay "1" --all

python3 nc.py set takeoff "12" "8" --all
python3 nc.py set delay "9" --all

python3 nc.py set move "-4, 0, 14" "5" 72
python3 nc.py set move "0, 0, 10" "5" 74
python3 nc.py set move "4,  0, 14" "5" 82

python3 nc.py set delay "20" --all

python3 nc.py set move "-6, 0, 12" "5" 72
python3 nc.py set move "0, 0, 12" "5" 74
python3 nc.py set move "6,  0, 12" "5" 82

python3 nc.py set delay "20" --all

python3 nc.py set land --all
python3 nc.py set delay "8" --all
python3 nc.py set disarm --all

