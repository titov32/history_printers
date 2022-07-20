#  для задания переменных окружения использовать:

# Для .bashrc:
#
# echo "export VAR="value"" >> ~/.bashrc && source ~/.bashrc
# Для .bash_profile:
#
# echo "export VAR="value"" >> ~/.bash_profile && source ~/.bash_profile
# Для /etc/environment:
#
# echo "export VAR="value"" >> /etc/environment && source /etc/environment

import os

POSTGRESUSER = os.getenv('POSTGRESUSER')
POSTGRESPASS = os.getenv('POSTGRESPASS')
POSTGRESDB = os.getenv('POSTGRESDB')
DATABASEURL = f"{POSTGRESUSER}:{POSTGRESPASS}@localhost/{POSTGRESDB}"

DOMAIN_NAME = '192.168.24.40:8000'
