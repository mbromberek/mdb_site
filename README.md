# mdb_site

# Start Postgres
pg_ctl -D /usr/local/var/postgres start
# Start Postgres and set Brew to start it on bootup
pg_ctl -D /usr/local/var/postgres start && brew services start postgresql

# Access postgresql from terminal
% psql postgres
\q # quits

Create Virtual Environment and install libraries
```
mkvirtualenv site
pip install -r requirements.txt
deactivate
workon site
workon #See all projects
```
