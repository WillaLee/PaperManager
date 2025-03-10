### To deploy locally

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

4. Run the application

```python
python manage.py runserver
```

### To contribute

1. Before pushing your contribute, checkout to main and pull the latest changes and merge with your own branch
```
checkout main
git pull
checkout <your_branch_name>
git merge
```

2. To push your contribute
```
git add .
git commit -m "some comment"
git push
```
Remerber to create pull request on Github