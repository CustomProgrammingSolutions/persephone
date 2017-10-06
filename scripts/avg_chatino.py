train_time = 49.224
utters = 2048
r = train_time / utters
root = "/home/oadams/mam/exp/results_chatino_run_1"

import os
for fn in os.listdir(root):
    print(fn)
    with open(os.path.join(root, fn)) as f:
        lines = f.readlines()
        results_1 = [eval(line) for line in lines[-10:]]
    with open(os.path.join(root.replace("1","2"), fn)) as f:
        lines = f.readlines()
        results_2 = [eval(line) for line in lines[-10:]]
    results_avg = [(item[0][0], (item[0][1]+item[1][1])/2)
                           for item in zip(results_1, results_2)]
    results_avg = [(float("%0.3f" % (item[0]*r)), float("%0.5f" % item[1])) for item in results_avg]
    print("TERs")
    for thing in results_avg[:5]:
        print(thing)
    #print("PERs")
    #for thing in results_avg[5:]:
    #    print(thing)
