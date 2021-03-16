Ansible Setup for bigCGI

Ansible Dependencies on hosts:
- User with default shell set to sh or bash
- python3.7 installed
- sudo installed
- bash installed

Installing Ansible on the Controlling Computer
- Run: 'python3.8 -m pip install -r requirements.txt'
- Modify .profile to include ~/.local/bin to PATH
- Run: 'ansible-galaxy collection install community.general' for FreeBSD stuff

TODO:
- supervisord isn't running on startup (env vars not set).  On first provision,
  freebsd restarts, so you need to run the start supervisord tasks again
- need more commands for tests, start supervisord, etc.
