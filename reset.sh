#!/bin/bash
# Rebuild a small test folder: 3 old files (should be deleted), 2 files that should stay.
cd ~/cleanup-lab
chmod -R u+w testdata 2>/dev/null
rm -rf testdata
mkdir -p testdata/sub
touch testdata/new.log testdata/old.log testdata/sub/old2.log.1 testdata/build.jar testdata/keep.txt
touch -d "40 days ago" testdata/old.log testdata/sub/old2.log.1 testdata/build.jar
echo "Test data reset:"
ls -lR testdata
