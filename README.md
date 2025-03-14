## To deploy locally

1. Clone the repo to local

```
git clone https://github.com/WillaLee/PaperManager.git
```

2. Go to the cloned directory and create a new branch for development

```
cd PaperManager
git checkout -b <new_branch_name>
```

3. Create a python virtual environment and install required python modules.

```python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Reference: https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/

4. Configure the database
    1. If you uses local MySQL server, logging in to MySQL
    ```bash
    psql -U postgres
    ```
    create a new database for this project
    ```sql
    CREATE DATABASE papermanager_db;
    ```
    2. Or if you prefer using Docker, run a docker container
    ```bash
    docker run --name papermanager-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=papermanager_db -p 5432:5432 -d postgres:latest
    ```
    3. Create a ```.env``` file in directory PaperManager, and configure this fields in this file
    ```
    DB_PASSWORD=<password_of_postgresql>
    DB_HOSTNAME=127.0.0.1 # If you are running a MySQL container using Docker on Linux or WSL2, use 'localhost'
    DB_PORT=5432
    ```

4. Run the database migrations to create database structures

```python
python manage.py migrate
```

5. Run the application

```python
python manage.py runserver
```

## To contribute

1. Before pushing your contribute, checkout to main and pull the latest changes and merge with your own branch
```
git checkout main
git pull
git checkout <your_branch_name>
git merge main
```

2. To push your contribute
```
git add .
git commit -m "some comment"
git push
```
Remerber to create pull request on Github