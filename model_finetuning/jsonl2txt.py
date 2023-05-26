import os, json
from random import random

f = open('scraped_data.jsonl', 'r')

train = open('train_data.txt', 'w')
valid = open('valid_data.txt', 'w')

for line in f:
    data = json.loads(line)
    if random() < 0.9:
        train.write(data['content'] + '\n')
    else:
        valid.write(data['content'] + '\n')

f.close()
train.close()
valid.close()