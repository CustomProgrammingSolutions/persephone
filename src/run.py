""" A driver script that runs experiments. """

import os
import shutil

import config
import rnn_ctc
import datasets.na
#import datasets.griko
import datasets.chatino
#import datasets.timit
#import datasets.japhug
import datasets.babel
from corpus_reader import CorpusReader

import results

EXP_DIR = config.EXP_DIR

def get_exp_dir_num():
    """ Gets the number of the current experiment directory."""
    return max([int(fn.split(".")[0])
                for fn in os.listdir(EXP_DIR) if fn.split(".")[0].isdigit()])

def prep_exp_dir():
    """ Prepares an experiment directory by copying the code in this directory
    to it as is, and setting the logger to write to files in that
    directory.
    """

    exp_num = get_exp_dir_num()
    exp_num = exp_num + 1
    code_dir = os.path.join(EXP_DIR, str(exp_num), "code")
    shutil.copytree(os.getcwd(), code_dir)

    print("exp_num: %d" % exp_num)

    return os.path.join(EXP_DIR, str(exp_num))

def multi_train():
    results_dir = "results_chatino_run_2"
    #train("chatino", "fbank", "phonemes_and_tones", results_dir, num_layers=3, hidden_size=250)
    #train("chatino", "fbank_and_pitch", "phonemes_and_tones", results_dir, num_layers=3, hidden_size=250)
    #train("chatino", "fbank", "phonemes", results_dir, num_layers=3, hidden_size=250)
    #train("chatino", "fbank_and_pitch", "phonemes", results_dir, num_layers=3, hidden_size=250)
    #train("chatino", "fbank", "tones", results_dir, num_layers=3, hidden_size=250)
    #train("chatino", "fbank_and_pitch", "tones", results_dir, num_layers=3, hidden_size=250)
    train("chatino", "phonemes_onehot", "tones", results_dir, num_layers=3, hidden_size=250)
    train("chatino", "pitch", "tones", results_dir, num_layers=3, hidden_size=250)

def train(language, feat_type, label_type, results_dir, num_layers=3, hidden_size=250):
    """ Run an experiment. """

    results_path = os.path.join(EXP_DIR, results_dir)
    if not os.path.exists(results_path):
        os.makedirs(results_path)

    fn = "%s_%s_%s_%s_%s" % (language, feat_type, label_type, num_layers, hidden_size)

    #feat_type = "fbank"
    #label_type = "tones"
    num_trains = [128,256,512,1024,1792]
    #num_trains = [2048]

    print("language: %s" % language)
    print("feat_type: %s" % feat_type)
    print("label_type: %s" % label_type)
    print("num_layers: %d" % num_layers)
    print("hidden_size: %d" % hidden_size)

    if language == "chatino":
        corpus = datasets.chatino.Corpus(feat_type, label_type, max_samples=900)
    elif language == "na":
        corpus = datasets.na.Corpus(feat_type, label_type, max_samples=900)
    else:
        raise Exception("Language '%s' not supported." % language)

    exp_dirs = []
    for i in num_trains:
        # Prepares a new experiment dir for all logging.
        exp_dir = prep_exp_dir()
        exp_dirs.append(exp_dir)
        corpus_reader = CorpusReader(corpus, num_train=i, batch_size=64)
        model = rnn_ctc.Model(exp_dir, corpus_reader,
                              num_layers=num_layers,
                              hidden_size=hidden_size,
                              decoding_merge_repeated=(False if
                                                       label_type=="tones"
                                                       else True))
        model.train()

    with open(os.path.join(results_path, fn), "w") as f:
        print("language: %s" % language, file=f)
        print("feat_type: %s" % feat_type, file=f)
        print("label_type: %s" % label_type, file=f)
        print("num_layers: %d" % num_layers, file=f)
        print("hidden_size: %d" % hidden_size, file=f)
        print("Exp dirs:", exp_dirs, file=f)
        if language == "chatino":
            results.format(exp_dirs,
                           phones=datasets.chatino.PHONEMES,
                           tones=datasets.chatino.TONES,
                           file=f)
        elif language == "na":
            results.format(exp_dirs,
                           phones=datasets.na.PHONES,
                           tones=datasets.na.TONES,
                           file=f)

def train_babel():
    # Prepares a new experiment dir for all logging.
    exp_dir = prep_exp_dir()
    corpus = datasets.babel.Corpus(["turkish"])
    corpus_reader = CorpusReader(corpus, num_train=len(corpus.get_train_fns()), batch_size=128)
    model = rnn_ctc.Model(exp_dir, corpus_reader, num_layers=3)
    model.train()

def calc_time():
    """ Calculates the total spoken time a given number of utterances
    corresponds to. """

    import numpy as np

    #for i in [128,256,512,1024,2048]:
    for i in [7420]:
        corpus = datasets.chatino.Corpus(feat_type="fbank", label_type="phonemes")
        #corpus_reader = CorpusReader(corpus, num_train=i)

        print(len(corpus.get_train_fns()[0]))

        total_frames = 0
        train_frames = 0
        valid_frames = 0
        test_frames = 0
        for feat_fn in corpus.get_train_fns()[0][:2048]:
            frames = len(np.load(feat_fn))
            total_frames += frames
            train_frames += frames
        for feat_fn in corpus.get_valid_fns()[0]:
            frames = len(np.load(feat_fn))
            total_frames += frames
            valid_frames += frames
        for feat_fn in corpus.get_test_fns()[0]:
            frames = len(np.load(feat_fn))
            total_frames += frames
            test_frames += frames

        total_time = ((total_frames*10)/1000)/60
        train_time = ((train_frames*10)/1000)/60
        valid_time = ((valid_frames*10)/1000)/60
        test_time = ((test_frames*10)/1000)/60
        print("Total time: %0.3f minutes." % total_time)
        print("Train time: %0.3f minutes." % train_time)
        print("Valid time: %0.3f minutes." % valid_time)
        print("Test time: %0.3f minutes." % test_time)

def train_japhug():
    """ Run an experiment. """

    #for i in [128,256,512,1024, 2048]:
    for i in [800]:
        # Prepares a new experiment dir for all logging.
        exp_dir = prep_exp_dir()

        corpus = datasets.japhug.Corpus(feat_type="log_mel_filterbank",
                                    target_type="phn", normalize=True)
        corpus_reader = CorpusReader(corpus, num_train=i)
        model = rnn_ctc.Model(exp_dir, corpus_reader, num_layers=3)
        model.train()

def test():
    """ Apply a previously trained model to some test data. """
    exp_dir = prep_exp_dir()
    corpus = datasets.na.Corpus(feat_type="log_mel_filterbank",
                                target_type="phn", tones=True)
    corpus_reader = CorpusReader(corpus, num_train=2048)
    model = rnn_ctc.Model(exp_dir, corpus_reader)
    restore_model_path = os.path.join(
        EXP_DIR, "131", "model", "model_best.ckpt")
    model.eval(restore_model_path)

def produce_chatino_lattices():
    """ Apply a previously trained model to some test data. """
    exp_dir = prep_exp_dir()
    corpus = datasets.chatino.Corpus(feat_type="log_mel_filterbank",
                                target_type="phn", tones=False)
    corpus_reader = CorpusReader(corpus, num_train=2048)
    model = rnn_ctc.Model(exp_dir, corpus_reader)
    restore_model_path = os.path.join(
        EXP_DIR, "194", "model", "model_best.ckpt")
    model.output_lattices(corpus_reader.valid_batch(), restore_model_path)

def produce_na_lattices():
    """ Apply a previously trained model to some test data. """
    exp_dir = prep_exp_dir()
    corpus = datasets.na.Corpus(feat_type="log_mel_filterbank",
                                target_type="phn", tones=True)
    corpus_reader = CorpusReader(corpus, num_train=2048)
    model = rnn_ctc.Model(exp_dir, corpus_reader)
    restore_model_path = os.path.join(
        EXP_DIR, "131", "model", "model_best.ckpt")
    model.output_lattices(corpus_reader.valid_batch(), restore_model_path)

def transcribe():
    """ Applies a trained model to the untranscribed Na data for Alexis. """

    exp_dir = prep_exp_dir()
    corpus = datasets.na.Corpus(feat_type="log_mel_filterbank",
                                target_type="phn", tones=True)
    corpus_reader = CorpusReader(corpus, num_train=2048)
    model = rnn_ctc.Model(exp_dir, corpus_reader)
    #print(corpus_reader.untranscribed_batch())

    # Model 155 is the first Na ASR model used to give transcriptions to
    # Alexis Michaud
    restore_model_path = os.path.join(
        EXP_DIR, "155", "model", "model_best.ckpt")

    #model.eval(restore_model_path, corpus_reader.)
    model.transcribe(restore_model_path)

def train_griko():

    # Prepares a new experiment dir for all logging.
    exp_dir = prep_exp_dir()

    corpus = datasets.griko.Corpus(feat_type="log_mel_filterbank",
                                   target_type="char")
    corpus_reader = CorpusReader(corpus, num_train=256)
    model = rnn_ctc.Model(exp_dir, corpus_reader)
    model.train()

def test_griko():
    # Prepares a new experiment dir for all logging.
    exp_dir = prep_exp_dir()

    corpus = datasets.griko.Corpus(feat_type="log_mel_filterbank",
                                   target_type="char")
    corpus_reader = CorpusReader(corpus, num_train=2048)
    model = rnn_ctc.Model(exp_dir, corpus_reader)
    restore_model_path = os.path.join(
        EXP_DIR, "164", "model", "model_best.ckpt")
    model.eval(restore_model_path)
