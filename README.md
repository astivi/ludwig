# ludwig

Ludwig is a python script which does the following:
* Clones all the repositories listed on the definitions file
* Checks every repository for a docker-compose.yml file
* Merges said files in a single docker-compose.yml which contains all the services listed on the repositories

Usage: python ludwig.py {filename}

### File format

```
folder:
  subfolder:
    project1: git@github.com:user/project1.git
    project2: git@github.com:user/project2.git
  project3: git@github.com:user/project3.git
```
