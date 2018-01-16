import os
from os.path import join
import config

with open("sylllist.txt") as syl_f:
    syllables = [line.strip() for line in syl_f]
syllables[0] = "ɑ"
syllables = set(syllables)

text_path = join(config.TGT_DIR, "na/new/label/TEXT")

lines = []
for fn in os.listdir(text_path):
    if fn.endswith("phonemes"):
        with open(join(text_path, fn)) as f:
            line = f.readline().strip()
            # Remove whitespace
            lines.append((line, fn))

print(sorted(list(syllables)))
# Find the length of the longest item in syllables
maxlen = len(sorted(list(syllables), key=lambda x: len(x))[-1])

OTHER_SYMS = {"…"}
OTHER_SYLS = {"hĩ", "mmm", "ne", "ʑi", "t…", "m", "ɻ", "ʂɻ̩",
                "t", "ʈʰ", "ʈʂʰ", "ɖ", "v", "z", "ʁ", "d", "ʈ", "s", # These ones with ldots; usually surrounded by lt & gt syms.
                "hṽ", "tʰv̩", # Found searching the sylllist  "manually"
                "ʈʂʰõ", "lõ", "ʁõ", "ɕĩ",
            }

def check(line, sent_id):
    for i in range(maxlen, 0, -1):
        if line[:i] in syllables.union(OTHER_SYLS).union(OTHER_SYMS):
            if line[:i] in OTHER_SYLS:
                print("syll: ", line[:i])
                print("Line: {}\n".format(line) + 
                      "Sentence ID: {}".format(sent_id))
                input()
            print(line[:i])
            return line[i:]
    print("Can't process line: {}\n".format(line) + 
          "Sentence ID: {}".format(sent_id))
    for i in range(maxlen, 0, -1):
        print(line[:i])
    input()
    return ""

# Ensure all phonemic subsequences are accounted for in the Na texts
i = 0
for line, sent_id in lines:
    i += 1
    print(i, line)
    line = "".join(line.split())
    subline = line
#    for sym in OTHER_SYMS:
#        subline = subline.replace(sym, "")
    while subline != "":
        subline = check(subline, sent_id)

