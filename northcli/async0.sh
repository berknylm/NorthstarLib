
python3 nc.py link 82
python3 nc.py delay "1"

python3 nc.py set arm --all
python3 nc.py set delay "10" --all
python3 nc.py set origin "40.8064456, 29.3560396" --all
python3 nc.py set disarm --all

python3 nc.py delay "1"
python3 nc.py launch --all
