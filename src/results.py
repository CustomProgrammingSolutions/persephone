""" Script for formatting results of experiments """

import datasets.na

import os
import utils

from distance import min_edit_distance_align

def round_items(floats):
    return ["%0.3f" % fl for fl in floats]

def format(exp_paths,
                   phones=datasets.na.PHONES,
                   tones=datasets.na.TONES,
                   file=None):
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

    if file:
        print("Valid LER", round_items(valid_lers), file=file)
        print("Test LER", round_items(test_lers), file=file)
        print("Test PER", round_items(test_pers), file=file)
        print("Test TER", round_items(test_ters), file=file)

        print("TONES")
        for item in zip([128,256,512,1024,2048], test_ters):
            print("(%d, %f)" % item, file=file)
        print("PHONEMES")
        for item in zip([128,256,512,1024,2048], test_pers):
            print("(%d, %f)" % item, file=file)
    else:
        print("Valid LER", round_items(valid_lers))
        print("Test LER", round_items(test_lers))
        print("Test PER", round_items(test_pers))
        print("Test TER", round_items(test_ters))

        print("TONES")
        for item in zip([128,256,512,1024,2048], test_ters):
            print("(%d, %f)" % item)
        print("PHONEMES")
        for item in zip([128,256,512,1024,2048], test_pers):
            print("(%d, %f)" % item)

def filter_labels(sent, labels):
    """ Returns only the tokens present in the sentence that are in labels."""
    return [tok for tok in sent if tok in labels]

def test_results(exp_path, phones, tones):
    """ Gets results of the model on the test set. """

    test_path = os.path.join(exp_path, "test")
    with open(os.path.join(test_path, "test_per")) as test_f:
        line = test_f.readlines()[0]
        test_ler = float(line.split()[2].strip(","))

    test_per = filtered_error_rate(os.path.join(test_path, "hyps"),
                                      os.path.join(test_path, "refs"),
                                      phones)

    test_ter = filtered_error_rate(os.path.join(test_path, "hyps"),
                                      os.path.join(test_path, "refs"),
                                      tones)

    return test_ler, test_per, test_ter

def filtered_error_rate(hyps_path, refs_path, labels):

    with open(hyps_path) as hyps_f:
        lines = hyps_f.readlines()
        hyps = [filter_labels(line.split(), labels) for line in lines]
    with open(refs_path) as refs_f:
        lines = refs_f.readlines()
        refs = [filter_labels(line.split(), labels) for line in lines]

    # For the case where there are no tokens left after filtering.
    only_empty = True
    for entry in hyps:
        if entry != []:
            only_empty = False
    if only_empty:
        return -1

    return utils.batch_per(hyps, refs)

def create_align_hist(exp_path, labels):

    test_path = os.path.join(exp_path, "test")
    hyps_path = os.path.join(test_path, "hyps")
    refs_path = os.path.join(test_path, "refs")

    with open(hyps_path) as hyps_f:
        lines = hyps_f.readlines()
        hyps = [filter_labels(line.split(), labels) for line in lines]
    with open(refs_path) as refs_f:
        lines = refs_f.readlines()
        refs = [filter_labels(line.split(), labels) for line in lines]

    alignments = []
    errors = []
    for ref, hyp in zip(refs, hyps):
        alignment = min_edit_distance_align(ref, hyp)
        alignments.append(alignment)
        for arrow in alignment:
            #if arrow[0] != arrow[1]:
            #    errors.append(arrow)
            errors.append(arrow)

    total_hist = {}
    err_hist = {}
    for error in errors:
        if error in err_hist:
            err_hist[error] += 1
        else:
            err_hist[error] = 1
        if error[0] != error[1] and error[1] != "" and error[0] != "":
            if error[0] in total_hist:
                total_hist[error[0]] += 1
            else:
                total_hist[error[0]] = 1

    return err_hist, total_hist


def error_types(exp_path, labels):
    """ Stats about the most common types of errors in the test set."""

    # TODO Need to address non-errors
    #err_hist = create_err_hist(exp_path, labels)

    error_list = sorted(err_hist.items(), key=lambda x: x[1], reverse=False)
    for thing in error_list:
        print(thing)

def confusion_matrix(exp_path, labels):

    labels = labels[:]
    labels.remove("˩˧")
    labels.remove("˧˩")
    labels = ["˧","˩","˥","˩˥","˧˥"]
    lmap = {"˩":"L","˥":"H","˧":"M","˧˥":"MH","˩˥":"LH"}

    align_hist, total_hist = create_align_hist(exp_path, labels)
    print(total_hist.items())

    # Don't consider counts for non-errors
    for key in align_hist.keys():
        if key[0] == key[1]:
            align_hist[key] = 0
    print(align_hist)
    for l_j in labels[:-1]:
        print(lmap[l_j], end=",")
    print(lmap[labels[-1]], end="")
    print()
    for l_i in labels:
        print(lmap[l_i], end=",")
        for l_j in labels[:-1]:
            key = (l_i, l_j)
            if key in align_hist:
                print("%0.1f" % (align_hist[key]*100/total_hist[key[0]]), end=",")
            else:
                print(0, end=",")
        key = (l_i, labels[-1])
        if key in align_hist:
            print("%0.1f" % (align_hist[key]*100/total_hist[key[0]]), end="")
        else:
            print(0, end="")
        print()
