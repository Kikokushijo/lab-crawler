import sys, os
from argparse import ArgumentParser
import concurrent.futures

novel_ids = []
with open('preprocess/index_list.txt', 'r') as f:
    for line in f:
        novel_ids.append(line.strip())

parser = ArgumentParser()
parser.add_argument('-s', '--start-with', help='index to start with', type=int, default=0)
parser.add_argument('-e', '--end-with', help='index to end with', type=int, default=len(novel_ids))
parser.add_argument('-t', '--threads', help='number of threads', type=int, default=1)
parser.add_argument('-c', '--script', help='script to iterate the index list', type=str, default='workflow.sh')

args = parser.parse_args()
start_with = args.start_with
end_with = args.end_with
n_workers = args.threads
script = args.script
assert start_with < end_with
print('Start processing the novel_ids[%d:%d]' % (start_with, end_with))

novel_ids = novel_ids[start_with:end_with]

def process_with_script(novel_id):
    return os.system('./%s %s' % (script, novel_id))

with open('errorlist.txt', 'w+') as f:
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_workers) as executor:
        future_to_nid = {executor.submit(process_with_script, nid): nid for nid in novel_ids}
        for future in concurrent.futures.as_completed(future_to_nid):
            nid = future_to_nid[future]
            try:
                result = future.result()
            except Execption as exc:
                print('%r generated an exception: %s' % (nid, exc))
            else:
                if result:
                    print('Error occurs when doing process on novel_id = %s' % (nid))
                    print(nid, file=f)