
#python3 nc.py link 72 74 82
python3 nc.py delay "1"

python3 nc.py set arm --all
python3 nc.py set delay "10" --all
python3 nc.py set origin "40.803587, 29.3591255" --all
python3 nc.py set delay "1" --all

python3 nc.py set takeoff "10" "8" --all
python3 nc.py set delay "8" --all

python3 nc.py set move "-14, 5, 10" "4" 72
python3 nc.py set move "-10, 9, 10" "4" 74
python3 nc.py set move "-6,  5, 10" "4" 82

python3 nc.py set delay "22" --all

python3 nc.py set land --all
python3 nc.py set delay "20" --all
python3 nc.py set disarm --all

