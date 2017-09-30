train_time = 49.224
utters = 2048
r = train_time / utters
root = "/home/oadams/mam/exp/results_chatino_run_1"

import os
for fn in os.listdir(root):
    print(fn)
    with open(os.path.join(root, fn)) as f:
        lines = f.readlines()
        tone_results_1 = [eval(line) for line in lines[-10:-5]]
        phoneme_results_1 = [eval(line) for line in lines[-5:]]
        #print(phoneme_results_1)
    with open(os.path.join(root.replace("1","2"), fn)) as f:
        lines = f.readlines()
        tone_results_2 = [eval(line) for line in lines[-10:-5]]
        phoneme_results_2 = [eval(line) for line in lines[-5:]]
        #print(phoneme_results_2)
    phoneme_results_avg = [(item[0][0], (item[0][1]+item[1][1])/2)
                           for item in zip(phoneme_results_1, phoneme_results_2)]
    phoneme_results_avg = [(item[0]*r, item[1]) for item in phoneme_results_avg]
    for thing in phoneme_results_avg:
        print(thing)
