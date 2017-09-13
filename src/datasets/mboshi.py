""" Interface to Mboshi data. """

import os

import config

ORG_DIR = config.MBOSHI_DIR
TGT_DIR = os.path.join(config.TGT_DIR, "mboshi")

PHONEMES = set()
with open(os.path.join(ORG_DIR, "corpus.token.train.mb")) as phn_f:
    for line in phn_f:
        PHONEMES = PHONEMES.union(set(line.split()))

print(PHONEMES)
