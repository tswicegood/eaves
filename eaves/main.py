#!/usr/bin/env python
import json
import requests
import sys


def get_all_repos(user):
    r = requests.get("https://api.github.com/users/%s/repos" % user)
    return json.loads(r.content)

def get_fork_users(user, repo):
    try:
        r = requests.get("https://api.github.com/repos/%s/%s/forks" % (user, repo["name"]))
        return [a["owner"]["login"] for a in json.loads(r.content)]
    except Exception:
        import ipdb;ipdb.set_trace()

def get_branches(user, repo):
    r = requests.get("https://api.github.com/repos/%s/%s/branches" % (user, repo["name"]))
    return [a["name"] for a in json.loads(r.content)]

def to_opml(data):
    html_url, rss_url, name = data
    return '    <outline htmlUrl="%s" xmlUrl="%s" text="%s" type="rss" />' % (
            html_url, rss_url, name)

def main(user):
    repos = get_all_repos(user)
    atom_urls = []
    print "found %d repos for %s" % (len(repos), user)
    for repo in repos:
        fork_users = get_fork_users(user, repo)
        print "  found %d users with forks for %s" % (len(fork_users), repo["name"])
        for fork_user in fork_users:
            branches = get_branches(fork_user, repo)
            print "    found %d branches for %s/%s" % (len(branches), fork_user, repo["name"])
            for branch in branches:
                atom_urls.append(
                    ("https://github.com/%s/%s/tree/%s" % (fork_user, repo["name"], branch),
                     "https://github.com/%s/%s/commits/%s.atom" % (fork_user, repo["name"], branch),
                     "%s/%s@%s" % (fork_user, repo["name"], branch),
                    )
                )

    print '<opml encoding="utf-8" version="2.0">'
    print '  <head>'
    print '    <title>Armstrong Dev</title>'
    print '  </head>'
    print '  <body>'
    print "\n".join([to_opml(a) for a in atom_urls])
    print '  </body>'
    print '</opml>'

if __name__ == "__main__":
    if len(sys.argv) is not 2:
        sys.stderr.write("usage: eaves [username]")
        sys.exit(1)

    user = sys.argv[1]
    main(user)
