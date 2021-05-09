## rlfetch
`rlfetch` is a tool to check the state of packages installed on the system. It downloads data using Repology.org API and checks the list of installed packages against it.

### How to install/uninstall
To install this program clone the repository, navigate to the project folder and run
```
pip install .
```

To uninstall, run
```
pip uninstall rlfetch
```

### Usage
```
usage: rlfetch [-h] [--disable DISABLE] [--detailed DETAILED] [--repo REPO]

Repology fetch tool

optional arguments:
  -h, --help           show this help message and exit
  --disable DISABLE    disable unneeded fields, possible values: newest,outdated,problematic,unique,vulnerable; possible to use multiple values separated by commas
  --detailed DETAILED  list packages from categories, usage is same to disable flag
  --repo REPO          usage of specific repo, possible values: VoidLinux
```
