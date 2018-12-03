import sys, os
from argparse import ArgumentParser

novel_ids = []
with open('preprocess/index_list.txt', 'r') as f:
    for line in f:
        novel_ids.append(line.strip())

parser = ArgumentParser()
parser.add_argument('-s', '--start-with', help='index to start with', type=int, default=0)
parser.add_argument('-e', '--end-with', help='index to end with', type=int, default=len(novel_ids))
args = parser.parse_args()
start_with = args.start_with
end_with = args.end_with
print('Start crawling the novel_ids[%d:%d]' % (start_with, end_with))

with open('errorlist.txt', 'w+') as f:
    for idx, novel_id in enumerate(novel_ids[start_with:end_with], start_with):
        print('Now doing process on the %d-th novel with novel_id = %s' % (idx, novel_id))
        res = os.system('./workflow.sh %s' % novel_id)
        if res:
            print('Error occurs when doing process on novel_id = %s' % (novel_id))
            print(novel_id, file=f)
            continue
