Ansible Setup for bigCGI

Ansible Dependencies on hosts:
- User with default shell set to sh or bash
- Python3 installed
- Sudo installed

Installing Ansible on the Controlling Computer
- Run: 'python3.8 -m pip install -r requirements.txt'
- Modify .profile to include ~/.local/bin to PATH
- Run: 'ansible-galaxy collection install community.general' for FreeBSD stuff
