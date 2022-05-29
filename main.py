from http.client import ResponseNotReady
from matplotlib.pyplot import text
import requests
from prettytable import PrettyTable
import base64
import json
import sys


scriptusage="Usage: python3 main.py --name username/organizationname [Optional: --mode orgs[organizations]/users[users] , --debug, --help]"

if "--help" in sys.argv:
    print(scriptusage)
    sys.exit()

if len(sys.argv)<3:
    print(scriptusage)
    sys.exit()

if "--mode" in sys.argv:
    if sys.argv[sys.argv.index("--mode")+1] == "orgs":
        type="orgs"
    elif sys.argv[sys.argv.index("--mode")+1] == "users":
        pass
    else:
        print(scriptusage)
else:
    type="users"

if "--debug" in sys.argv:
    debug_mode=True
else:
    debug_mode=False

try:
    github_username = sys.argv[sys.argv.index("--name")+1]
except:
    print(scriptusage)

#API limit bypass
token=base64.b64encode(b'myclientid:CHANGETHIS_ITMUSTYOURGITHUBSECRETTOKEN').decode()
apiLimitBypass={"Authorization": f"Basic {token}"} 
table = PrettyTable()

table.field_names = ["First Found Repo","First Found Commit SHA", "Mail"]
mails=[]



# Select mail from raw text
def mailselector(responsein):
    p=(responsein[:responsein.find("@")])
    q=p[p.find("\n"):]
    r=(responsein[responsein.find("@"):])
    s=r[:r.find("\n")]
    raw=q+s
    clean=raw[raw.find("<")+1:raw.find(">")]
    return clean

# Get Repositories
urlForGetReposRaw = f"https://api.github.com/{type}/{github_username}/repos"
responseForRepos = requests.get(urlForGetReposRaw, headers=apiLimitBypass).text
reporaw = json.loads(responseForRepos)


for repository in reporaw:
    repoName=(repository["name"])
    if debug_mode:print("Searching in "+str(repoName))

    urlforgetcommitsraw=f"https://api.github.com/repos/{github_username}/{repoName}/commits"
    responseforcommits = requests.get(urlforgetcommitsraw, headers=apiLimitBypass).text
    commitsraw = json.loads(responseforcommits)
    
    for commits in commitsraw:
        temporary_=[]
        temporary_.append(commits["sha"])
        
        #Debug
        if debug_mode:print("Commit:"+str(commits["sha"]))

        for commitsha in temporary_:
            response = requests.get(f"https://github.com/{github_username}/{repoName}/commit/{commitsha}.patch").text
            clean = mailselector(response)
            if clean not in mails:
                if "@" in clean:
                    if debug_mode: print("\033[93m"+str(clean)+" found.\033[0m")
                    table.add_row([repoName, commitsha, clean])
                    mails.append(clean)
                else:
                    if debug_mode:print("\033[93m"+" Error Occured Commit:"+str(commitsha)+"\033[0m")
            else:
                pass

print(table)