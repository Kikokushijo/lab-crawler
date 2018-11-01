import sys, os

novel_ids = []
with open('preprocess/index_list.txt', 'r') as f:
    for line in f:
        novel_ids.append(line.strip())

start_with = int(sys.argv[1])
for novel_id in novel_ids[start_with:]:
    print('Now doing process with novel_id = %s' % novel_id)
    os.system('./workflow.sh %s' % novel_id)
