from colored import fg, attr
from urllib.request import urlopen
import argparse
import json
import subprocess
import os
import sys

JSON_ENTRIES = 200

OUTDATED = "&outdated=1"
UNIQUE = "&families=1"
PROBLEMATIC = "&problematic=1"
NEWEST = "&newest=1"
VULNERABLE = "&vulnerable=1"


class Repository:
    def __init__(self, json_data, repo_id):
        self.desc = None
        if not repo_id:
            self.id, self.desc = self.fetch_repo_info()
        else:
            self.id = repo_id    
        self.json_data = json_data[self.id]
        if not self.desc:
            self.desc = self.json_data["description"]
        self.cmd = self.json_data["command"]
        self.color = self.json_data["color"]
        self.repository = self.json_data["repository"]

    def fetch_repo_info(self):
        cmd = ["lsb_release", "-id"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        tmp = proc.communicate()[0].decode("ascii")
        lines = tmp.split("\n")
        result = []
        for i in range(len(lines)-1):
            result.append(lines[i].split("\t")[1])
        return result

    def get_pkgs_list(self):
        proc = subprocess.Popen(self.cmd, stdout=subprocess.PIPE)
        tmp = proc.communicate()[0].decode("UTF-8")
        pkgs = tmp.split("\n")
        pkgs.pop(-1)
        for i in range(len(pkgs)):
            pkgs[i] = pkgs[i].split(" ")[1].rsplit("-", 1)[0]
        return pkgs


def get_json_data(repository, project, request):
    if len(project) > 0:
        project += "/"
    url = f"https://repology.org/api/v1/projects/{project}" \
          f"?inrepo={repository.repository}{request}"
    page = urlopen(url).read().decode("UTF-8")
    return json.loads(page)


def get_pkgs_data(repository, request):
    data = get_json_data(repository, "", request)
    keys = list(data.keys())

    while len(keys) >= JSON_ENTRIES:
        data = get_json_data(repository, keys[-1], request)
        new_keys = list(data.keys())
        if len(new_keys) == 1:
            break
        keys.extend(new_keys[1:])
    return keys


categories = ["newest", "outdated", "problematic", "unique", "vulnerable"]

def main():
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(curr_dir, "repos.json"), "r") as f:
        json_raw_data = f.read()
    json_data = json.loads(json_raw_data)
    parser = argparse.ArgumentParser(prog="rlfetch",
                                     description="Repology fetch tool")
    parser.add_argument('--disable', help="disable unneeded fields, possible"
                                          f" values: {','.join(categories)};"
                                          " possible to use multiple values"
                                          " separated by commas")
    parser.add_argument('--repo', help="usage of specific repo, possible"
                                       " values:"
                                       f" {','.join(json_data.keys())}",
                        default=None)
    args = parser.parse_args()
    disabled = args.disable.split(",") if args.disable else []
    if not args.repo in json_data.keys():
        args.repo = None
    repo = Repository(json_data, args.repo)
    pkgs = repo.get_pkgs_list()
    pkgs_set = set(pkgs)
    style = fg(repo.color) + attr(1)
    print(f"{style}{repo.desc}")
    print(f"Packages:{attr(0)} {len(pkgs)}")
    if not "newest" in disabled:
        print(f"{style}Newest:{attr(0)}"
              f" {len(list(pkgs_set & set(get_pkgs_data(repo, NEWEST))))}")
    if not "outdated" in disabled:
        print(f"{style}Outdated:{attr(0)}"
              f" {len(list(pkgs_set & set(get_pkgs_data(repo, OUTDATED))))}")
    if not "problematic" in disabled:
        print(f"{style}Problematic:{attr(0)}"
              f" {len(list(pkgs_set & set(get_pkgs_data(repo, PROBLEMATIC))))}")
    if not "unique" in disabled:
        print(f"{style}Unique:{attr(0)}"
              f" {len(list(pkgs_set & set(get_pkgs_data(repo, UNIQUE))))}")
    if not "vulnerable" in disabled:
        print(f"{style}Potentially vulnerable:{attr(0)}"
              f" {len(list(pkgs_set & set(get_pkgs_data(repo, VULNERABLE))))}")
    return 0
