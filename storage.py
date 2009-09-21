#!/usr/bin/python
import md5
import os
import tempfile
import re
import simplejson as json

def md5sum(data):
    m = md5.new()
    m.update(data)
    return m.hexdigest()

def get_session_path(repopath, session_id):
    return os.path.join(repopath, str(session_id))

def find_blob(repopath, sum):
    """ Takes a md5sum arg as a string, and returns the path to the blob
    with that checksum, if it exists """
    for session_id in get_all_sessions(repopath):
        session_path = get_session_path(repopath, session_id)
        blob_path = os.path.join(session_path, sum)
        if os.path.exists(blob_path):
            return blob_path
    return None

def get_all_sessions(repopath):
    session_dirs = []
    for dir in os.listdir(repopath):
        if re.match("^[0-9]+$", dir) != None:
            session_dirs.append(int(dir))
    return session_dirs

def find_next_session_id(repopath):
    assert os.path.exists(repopath)
    session_dirs = get_all_sessions(repopath)
    session_dirs.append(-1)
    return max(session_dirs) + 1            

class RepoWriter:

    def __init__(self):
        self.repopath = "REPO"
        self.session_path = None
        self.metadatas = []
        self.sessioninfo = {}

    def new_session(self, session_name):
        assert self.session_path == None
        assert os.path.exists(self.repopath)
        self.session_path = tempfile.mkdtemp(prefix = "tmp_", dir = self.repopath) 

    def add(self, data, metadata = {}):
        assert self.session_path != None
        sum = md5sum(data)
        metadata["md5sum"] = sum
        existing_blob = find_blob(self.repopath, sum)
        if not existing_blob:
            fname = os.path.join(self.session_path, sum)
            assert not os.path.exists(fname)
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
        f = open(bloblist_filename, "w")
        json.dump(self.metadatas, f, indent = 4)
        f.close()

        session_filename = os.path.join(self.session_path, "session.json")
        assert not os.path.exists(session_filename)
        f = open(session_filename, "w")
        json.dump(self.sessioninfo, f, indent = 4)
        f.close()

        fileno = find_next_session_id(self.repopath)
        final_session_dir = os.path.join(self.repopath, str(fileno))
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
    s = RepoWriter()
    s.new_session("new_session")

    file_to_add = "promenader.txt"
    data = open(file_to_add, "r").read()
    s.add(data, {"filename": file_to_add})
    s.add(data, {"filename": file_to_add})
    s.add(data, {"filename": file_to_add})
    s.add(data, {"filename": file_to_add})
    s.add(data, {"filename": file_to_add})
    s.add(data, {"filename": file_to_add})
    s.add(data, {"filename": file_to_add})
    s.add(data, {"filename": file_to_add})
    s.close_session()
    
if __name__ == "__main__":
    main()
