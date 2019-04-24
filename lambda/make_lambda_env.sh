virtualenv ${1}
cd  ${1}
source bin/activate
pwd
pip -V
pip install pip -U
pip -V
pip install pycryptodome
pip install paramiko
pip install ucsmsdk
deactivate
