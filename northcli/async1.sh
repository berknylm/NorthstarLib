
python3 nc.py link 82
python3 nc.py delay "1"

python3 nc.py set arm --all
python3 nc.py set delay "5" --all
python3 nc.py set origin "40.8064456, 29.3560396" --all
python3 nc.py set delay "1" --all
python3 nc.py set takeoff "3" --all
python3 nc.py set delay "15" --all
python3 nc.py set land --all
python3 nc.py set delay "12" --all
python3 nc.py set disarm --all

python3 nc.py launch --all
