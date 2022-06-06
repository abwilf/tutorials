import time,sys
# args:
# how many workers

def read_txt(filename):
    with open(filename, 'r') as f:
        s = f.read()
    return s

num_workers = sys.argv[1]
time_sleep = 10

while True:
    if len(read_txt('email_log.txt').replace('\n','').strip()) >= num_workers:
        break
    time.sleep(time_sleep)

