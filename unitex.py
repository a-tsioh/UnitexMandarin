# -*- coding:utf8 -*-
import codecs
import subprocess as sp
import os
import shutil
import tempfile
from collections import namedtuple
import re

gram_path = "/home/pierre/unitex/Mandarin"
working_dir = "/media/Speedy/tmp"
unitextool = "/home/pierre/Téléchargements/Unitex3.0/App/UnitexTool"

prepare_args = [unitextool,
        '{',
        'Grf2Fst2',
        '($GRAM)/Graphs/Preprocessing/Sentence/Sentence.grf',
        '-y',
        '-c',
        '-qutf8-no-bom',
        '}',
        '{',
        'Flatten',
        '($GRAM)/Graphs/Preprocessing/Sentence/Sentence.fst2',
        '-r',
        '-d5',
        '-qutf8-no-bom',
        '}']
preprocess_arg = [unitextool,
        '{',
        'Normalize',
        '($INPUT).txt',
        '-qutf8-no-bom',
        '}',
        '{',
        'Fst2Txt',
        '-t($INPUT).snt',
        '($GRAM)/Graphs/Preprocessing/Sentence/Sentence.fst2',
        '-M',
        '-c',
        '-qutf8-no-bom',
        '}',
        '{',
        'Tokenize',
        '($INPUT).snt',
        '-a($GRAM)/Alphabet.txt',
        '-c',
        '-qutf8-no-bom',
        '}',
        '{',
        'Dico',
        '-t($INPUT).snt',
        '($GRAM)/Dela/base.bin',
        '-a($GRAM)/Alphabet.txt',
        '-qutf8-no-bom',
        '}',
        '{',
        'Cassys',
        '-t($INPUT).snt',
        '-a($GRAM)/Alphabet.txt',
        '-l($GRAM)/Graphs/grammaire.csc',
        '-qutf8-no-bom',
        '}']


def prepare_grammar(path=gram_path):
    args = [a.replace("($GRAM)", path) for a in prepare_args]
    print "calling", " ".join(args)
    sp.call(args)


def preprocess(infile, outfile, workdir=working_dir, path=gram_path, cleanup=True):
    tmpdir = tempfile.mkdtemp("", "unitexpy_", workdir)
    working_file = os.path.join(tmpdir, os.path.basename(infile))
    shutil.copyfile(infile + ".txt", working_file + ".txt")
    os.mkdir(os.path.join(workdir, working_file + "_snt"))
    args = [a.replace("($GRAM)", path).replace("($INPUT)", working_file) for a in preprocess_arg]
    print "calling", " ".join(args)
    sp.call(args)
    shutil.copyfile(working_file + "_csc.txt", outfile)
    if cleanup:
        shutil.rmtree(tmpdir)


Token = namedtuple("Token", "form category")
re_escaped_token = re.compile(r"\\\{|\\,\\\.[^\\]+\\\}",
                              re.U)
re_find_specials = re.compile(r"(\{(?P<form>[^\}]*[^\\]),\.(?P<cat>[A-Z]+)\})",
                              re.U)


def toksequence_of_line(line):
    # remove inner structure:
    line = re_escaped_token.sub("", line)
    tokseq = []
    splitted = re_find_specials.split(line)
    i = 0
    while i < len(splitted):
        substr = splitted[i]
        if len(substr) < 1:
            i += 1
            continue
        if substr == "{S}":
            tokseq.append(Token("", "EOS"))
            i += 1
        elif substr[0] == "{":  # special token
            tokseq.append(Token(splitted[i+1], splitted[i+2]))
            i += 3
        else:  # normal substring:
            for car in substr:
                tokseq.append(Token(car, "normal"))
            i += 1
    return tokseq


def itokseq_from_file(infile):
    f = codecs.open(infile, "r", "utf8")
    for line in f:
        print line
        yield toksequence_of_line(line.strip())
    f.close()
