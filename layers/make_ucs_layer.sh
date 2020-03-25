rm -rf ${1}
mkdir ${1}
cd ${1}
python3.7 -m venv venv
source venv/bin/activate
pwd
pip -V
pip install pip -U
pip -V
pip install requests -U
pip install ucsmsdk -U
pip install ucscsdk -U
pip install imcsdk -U
deactivate