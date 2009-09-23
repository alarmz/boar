#!/usr/bin/python
from __future__ import with_statement

import md5
import os
import tempfile
import re
import simplejson as json

import repository

def md5sum(data):
    m = md5.new()
    m.update(data)
    return m.hexdigest()

class RepoWriter:
    def __init__(self, repo):
        self.repo = repo
        self.session_path = None
        self.metadatas = []
        self.sessioninfo = {}

    def new_session(self, session_name):
        assert self.session_path == None
        assert os.path.exists(self.repo.repopath)
        self.session_path = tempfile.mkdtemp(prefix = "tmp_", dir = self.repo.repopath) 

    def add(self, data, metadata = {}):
        assert self.session_path != None
        sum = md5sum(data)
        metadata["md5sum"] = sum
        existing_blob = self.repo.find_blob(sum)
        fname = os.path.join(self.session_path, sum)
        if not existing_blob and not os.path.exists(fname):
            f = open(fname, "w")
            f.write(data)
            f.close()
        self.metadatas.append(metadata)
        return sum

    def set_sessioninfo(sessioninfo):
        self.sessioninfo = sessioninfo

    def close_session(self):
        assert self.session_path != None

        bloblist_filename = os.path.join(self.session_path, "bloblist.json")
        assert not os.path.exists(bloblist_filename)
        with open(bloblist_filename, "w") as f:
            json.dump(self.metadatas, f, indent = 4)

        session_filename = os.path.join(self.session_path, "session.json")
        assert not os.path.exists(session_filename)
        with open(session_filename, "w") as f:
            json.dump(self.sessioninfo, f, indent = 4)

        fileno = self.repo.find_next_session_id()
        final_session_dir = os.path.join(self.repo.repopath, str(fileno))
        assert not os.path.exists(final_session_dir)
        os.rename(self.session_path, final_session_dir)


class RepoReader:

    def __init__(self):
        self.session_path = None

    def open(self, session_name):
        assert self.session_path == None

    def get(self, file_path):
        assert self.session_path != None
        assert False, "Not implemented"

    def get_session_names(self):
        assert False, "Not implemented"





def main():
    r = repository.Repo("/tmp/REPO")
    s = RepoWriter(r)
    s.new_session("TestSession")
    os.chdir("/tmp")
    def visitor(arg, dirname, names):
        for name in names:
            print "Visiting", dirname, name
            full_path = os.path.join(dirname, name)
            if not os.path.isfile(full_path):
                continue
            f = open(full_path, "r")
            data = f.read()
            f.close()
            s.add(data, {"filename": full_path})
        
    os.path.walk("json", visitor, "bilder")

    s.close_session()
    
if __name__ == "__main__":
    main()

