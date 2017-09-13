""" Derives a phoneme set from [preprocessed] transcriptions in a given directory."""

import os
import sys

PATH = sys.argv[1]

PHONEMES = set()
for root, dirn, filenames in os.walk(PATH):
    for filename in filenames:
        if "tonesTrue" not in filename and ".tones." not in filename:
            file_path = os.path.join(root, filename)
            with open(file_path) as f:
                for line in f:
                    PHONEMES = PHONEMES.union(set(line.split()))

print(PHONEMES)
