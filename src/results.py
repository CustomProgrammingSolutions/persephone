""" Script for formatting results of experiments """

import datasets.na

import os
import utils

def round_items(floats):
    return ["%0.3f" % fl for fl in floats]

def format(exp_paths,
                   phones=datasets.na.PHONES,
                   tones=datasets.na.TONES):
    """ Takes a list of experimental paths such as mam/exp/<number> and outputs
    the results. """

    valid_lers = []
    valid_pers = []
    test_lers = []
    test_pers = []
    test_ters = []

    for path in exp_paths:

        test_ler, test_per, test_ter = test_results(path, phones, tones)
        test_lers.append(test_ler)
        test_pers.append(test_per)
        test_ters.append(test_ter)

        with open(os.path.join(path, "best_scores.txt")) as best_f:
            sp = best_f.readline().replace(",", "").split()
            training_ler, valid_ler, valid_per = float(sp[4]), float(sp[7]), float(sp[10])
            valid_lers.append(valid_ler)

    print("Valid LER", round_items(valid_lers))
    print("Test LER", round_items(test_lers))
    print("Test PER", round_items(test_pers))
    print("Test TER", round_items(test_ters))

    for item in zip([128,256,512,1024,2048], test_pers):
        print("(%d, %f)" % item)

def test_results(exp_path, phones, tones):
    """ Gets results of the model on the test set. """

    test_path = os.path.join(exp_path, "test")
    with open(os.path.join(test_path, "test_per")) as test_f:
        line = test_f.readlines()[0]
        test_ler = float(line.split()[2].strip(","))

    test_per = phones_only_error_rate(os.path.join(test_path, "hyps"),
                                      os.path.join(test_path, "refs"),
                                      phones)

    test_ter = tones_only_error_rate(os.path.join(test_path, "hyps"),
                                      os.path.join(test_path, "refs"),
                                      tones)

    return test_ler, test_per, test_ter

def phones_only_error_rate(hyps_path, refs_path, phones):

    def phones_only(sent):
        """ Returns only the Na phones present in the sentence."""
        return [phone for phone in sent if phone in phones]

    with open(hyps_path) as hyps_f:
        lines = hyps_f.readlines()
        hyps = [phones_only(line.split()) for line in lines]
    with open(refs_path) as refs_f:
        lines = refs_f.readlines()
        refs = [phones_only(line.split()) for line in lines]

    return utils.batch_per(hyps, refs)

def tones_only_error_rate(hyps_path, refs_path, tones):

    def tones_only(sent):
        """ Returns only the Na tones present in the sentence."""
        return [tone for tone in sent if tone in tones]

    with open(hyps_path) as hyps_f:
        lines = hyps_f.readlines()
        hyps = [tones_only(line.split()) for line in lines]
    with open(refs_path) as refs_f:
        lines = refs_f.readlines()
        refs = [tones_only(line.split()) for line in lines]

    # For the case where there are no tones (the experiment was phones only).
    only_empty = True
    for entry in hyps:
        if entry != []:
            only_empty = False
    if only_empty:
        return -1

    return utils.batch_per(hyps, refs)