# -*- coding: utf-8 -*-
import os
import re
import argparse

MIN_WORDS=1
MAX_WORDS=15

NUMBERS_REGEX=re.compile(r"[0-9]+")
SYMBOL_REGEX=re.compile(r"[<>\+\*\\#@\^\[\]\(\)\/]")
ABBREVIATION_REGEX=re.compile(r"[A-Z]{2,}|[A-Z]+\.*[A-Z]+")

APOSTRAPHE=r"'\u2018\u2019\u02BC"
SEPARATOR = r",.?!\";|`"

valid_letters = 'aáàâäbcdeéèêëfghiíìîïjklmnoóòôöpqrstuúùûüvwẃẁŵẅyýỳŷÿz'
ALPHABET_REGEX = re.compile(r"[" + valid_letters + valid_letters.upper() + "]")

sentences_seen = set()

def tokenize(string):
    s = string
    s = re.sub('\t', " ", s)
    s = re.sub(r"[" + SEPARATOR + "]", " ", s)
    s = re.sub(r"[" + APOSTRAPHE + "]", " ", s)
    return s.strip().split()


def filterNumbers(string):
    return not NUMBERS_REGEX.findall(string)


def filterSymbols(string):
    return not SYMBOL_REGEX.findall(string)
   

def filterAbbreviations(string):
    return not ABBREVIATION_REGEX.findall(string)


def filterAlphabet(string):
    return ALPHABET_REGEX.findall(string)



def main(in_filepath, out_filepath, rejected_filepath):
    outfile = open(out_filepath, 'w', encoding='utf-8')
    rejectfile = open(rejected_filepath, 'w', encoding='utf-8')

    with open(in_filepath, 'r', encoding='utf-8') as infile:
        for sentence in infile:
            if sentence in sentences_seen:
                continue
 
            if not filterNumbers(sentence):
                rejectfile.write("NUMBERS: %s " % sentence)
                continue

            if not filterSymbols(sentence):
                rejectfile.write("SYMBOLS: %s " % sentence)
                continue

            if not filterAbbreviations(sentence):
                rejectfile.write("ABBREVIATION: %s " % sentence)
                continue

            tokenized = tokenize(sentence)
            if (len(tokenized) > MIN_WORDS and len(tokenized) < MAX_WORDS):
                outOfAlphabet = False
                for word in tokenized:
                    if not filterAlphabet(word):
                        outOfAlphabet = True
                        break

                if outOfAlphabet:
                    rejectfile.write("OUT OF ALPHABET: %s" % sentence)
                    continue

            else:
                rejectfile.write("TOO LONG: %s " % sentence)
                continue
           
            sentences_seen.add(sentence)          
            outfile.write(sentence)

    outfile.close()
    rejectfile.close() 


 
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in-file", required=True )
    parser.add_argument("-o", "--out-file", required=True)
    parser.add_argument("-r", "--rejects-file", required=True)
    args = parser.parse_args()

    main(args.in_file, args.out_file, args.rejects_file)

