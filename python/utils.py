import roman
import re
import os
import sys

from num2words import num2words
from typing.re import Pattern

from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.collocations import BigramCollocationFinder
from nltk.collocations import BigramAssocMeasures
from nltk.collocations import TrigramCollocationFinder
from nltk.collocations import TrigramAssocMeasures
import textwrap
import language_check
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

mapping_normalization = [
  #[ u'\xa0 ', u' ' ],
#  [ u'«\xa0', u'«' ],
#  [ u'\xa0»', u'»' ],
  #[ u'\xa0' , u' ' ],
  [ u'M.\u00a0'   , u'Monsieur ' ],
  [ u'M. '   , u'Monsieur ' ],
  [ u'Mme\u00a0'  , u'Madame ' ],
  [ u'Mme '  , u'Madame ' ],
  [ u'Mlle\u00a0' , u'Mademoiselle ' ],
  [ u'Mlle ' , u'Mademoiselle ' ],
  [ u'Mlles\u00a0', u'Mademoiselles ' ],
  [ u'Mlles ', u'Mademoiselles ' ],
  [ u'%', u'pourcent' ],
  [ u'arr. ', u'arrondissement ' ],
  [ re.compile('\[\d+\]'), u'' ],
]

superscript_chars_mapping = {
  '0': u'\u2070',
  '1': u'\u00b9',
  '2': u'\u00b2',
  '3': u'\u00b3',
  '4': u'\u2074',
  '5': u'\u2075',
  '6': u'\u2076',
  '7': u'\u2077',
  '8': u'\u2078',
  '9': u'\u2079',

  '0 ': u'\u2070 ',
  '1 ': u'\u00b9 ',
  '2 ': u'\u00b2 ',
  '3 ': u'\u00b3 ',
  '4 ': u'\u2074 ',
  '5 ': u'\u2075 ',
  '6 ': u'\u2076 ',
  '7 ': u'\u2077 ',
  '8 ': u'\u2078 ',
  '9 ': u'\u2079 ',

  'o': 'uméro',
  '°': 'uméro',
  'os': 'uméros',
  '°s': 'uméros',
  '° s': 'uméros',
  u'°\u00a0s': 'uméros',
  'o s': 'uméros',
  u'o\u00a0s': 'uméros',
  's': 's',
  'ter': 'ter',
  'gr': 'onseigneur',

  ' ': ' ',

  # Those should be in sync with ORDINAL_REGEX
  'e': 'ieme',
  'è': 'ieme ',
  'e,': 'ieme,',
  'èm': 'ieme ',
  'e ': 'ieme ',
  'e –': 'ieme –',
  'r': 'ier',
  'er': 'ier',
  'er ': 'ier ',
  'er.': 'ier.',
  'er,': 'ier,',
  'ER': 'ier',
  'Er': 'ier',
  'er –': 'ier –',
  're': 'iere',
  'ère': 'iere',
  'ère': 'iere',
  'ème': 'ieme',
  'éme': 'ieme',
  'ème ': 'ieme',
  'eme': 'ieme',
}

ORDINAL_REGEX = re.compile("(\d+)([ieme|ier|iere]+)")

subscript_chars_mapping = {
  '0': u'\u2080',
  '1': u'\u2081',
  '2': u'\u2082',
  '3': u'\u2083',
  '4': u'\u2084',
  '5': u'\u2085',
  '6': u'\u2086',
  '7': u'\u2087',
  '8': u'\u2088',
  '9': u'\u2089',

  '0 ': u'\u2080 ',
  '1 ': u'\u2081 ',
  '2 ': u'\u2082 ',
  '3 ': u'\u2083 ',
  '4 ': u'\u2084 ',
  '5 ': u'\u2085 ',
  '6 ': u'\u2086 ',
  '7 ': u'\u2087 ',
  '8 ': u'\u2088 ',
  '9 ': u'\u2089 ',

  'e': u'\u2091',
  ' ': '',
}

WORD_REGEX = re.compile("[^\w\d\'\-]+")
def splitIntoWords(text):
    return WORD_REGEX.split(text)

NUMS_REGEX = re.compile("(\d+,?\u00A0?\d+)|(\d+\w+)|(\d)*")
def getNumbers(text):
    return NUMS_REGEX.split(text)

def getRomanNumbers(ch):
  ROMAN_CHARS = "XVI"
  ro  = ''
  ros = 0
  for i in range(len(ch)):
    c = ch[i]
    if c in ROMAN_CHARS:
      #print('len(ro)="{}" c="{}" ch[i-1]="{}" ro="{}" ch="{}"'.format(len(ro), c, ch[i-1], ro, ch))
      if len(ro) == 0 and not ch[i-1].isalpha():
        ro  = c
        ros = i
      else:
        if len(ro) > 0 and ch[i-1] in ROMAN_CHARS:
          ro += c
    else:
      if len(ro) > 0:
        if not c.isalpha():
          #print('getRomanNumbers', ch, ro)
          yield ch[ros-1], ch[i], ro
        ro  = ''
        ros = i

  if len(ro) > 0:
    #print('getRomanNumbers final', ch, "|||", ro)
    yield ch[ros-1], '', ro

def filter_numbers(inp, lang="fr"):
  finalinp = ''

  #print('filter_numbers', 'inp=', inp)

  for e in getNumbers(inp):
    if not e:
      continue

    newinp = e
    #print('filter_numbers', 'e=', e)

    try:
      ee = ''.join(e.split())
      if int(e) > 0:
        #print('filter_numbers', 'INT:BEFORE', 'ee=', ee, 'newinp=', newinp)
        newinp = num2words(int(ee), lang=lang)
        #print('filter_numbers', 'INT:AFTER', 'ee=', ee, 'newinp=', newinp)
    except ValueError:
      try:
        ee = ''.join(e.replace(',', '.').split())
        if float(ee):
          #print('filter_numbers', 'FLOAT:BEFORE', 'ee=', ee, 'newinp=', newinp)
          newinp = num2words(float(ee), lang=lang)
          #print('filter_numbers', 'FLOAT:AFTER', 'ee=', ee, 'newinp=', newinp)
      except ValueError:
        matches = ORDINAL_REGEX.match(e)
        #print('filter_numbers', 'ORDINAL', 'e=', e, matches)
        if matches:
          newinp = num2words(int(matches.group(1)), ordinal=True, lang=lang)

    finalinp += newinp

    #print('filter_numbers', 'e=', e, 'newinp=', newinp, 'finalinp=', finalinp)

  return finalinp

def maybe_normalize(value, mapping=mapping_normalization):
  for norm in mapping:
    if type(norm[0]) == str:
      value = value.replace(norm[0], norm[1])
    elif isinstance(norm[0], Pattern):
      value = norm[0].sub(norm[1], value)
    else:
      print('UNEXPECTED', type(norm[0]), norm[0])

  for ro_before, ro_after, ro in getRomanNumbers(value):
    #print('maybe_normalize', 'ro=', ro)
    try:
      value = value.replace(ro_before + ro + ro_after, ro_before + str(roman.fromRoman(ro)) + ro_after)
    except roman.InvalidRomanNumeralError as ex:
      print(ex)
      pass

  return value

def maybe_translate(element, mapping):
  value = maybe_normalize(element.nodeValue)

  bsp  = value.count(' ')
  nbsp = value.count('\u00a0')
  if value in mapping:
    return mapping[value]
  else:
    nvalue = value.strip()
    if nbsp > 0:
      if nbsp == 1 and value.find('\u00a0') == len(value) - 1:
        if nvalue in mapping:
          return mapping[nvalue] + u'\u00a0'
      if nbsp == 1 and value.find('\u00a0') == len(value) - 2 and value.find(' ') == len(value) - 1:
        if nvalue in mapping:
          return mapping[nvalue] + u'\u00a0'
    if bsp > 0:
      if bsp == 1 and value.find(' ') == len(value) - 1:
        if nvalue in mapping:
          return mapping[nvalue] + u' '

  if element.nodeValue.strip().isnumeric() and str(int(element.nodeValue.strip())) == element.nodeValue.strip():
    pass
  else:
    print("NOT TRANSLATED: '{}' => '{}'".format(element.nodeValue, value))
    for c in value:
      print("value: '{}' == {}".format(c, ord(c)))
  return value

def recursive_text(root, finaltext=""):
  if root.nodeName == 'br':
    return ' '
  else:
    for c in root.childNodes:
      if c.nodeType == c.TEXT_NODE:
        if root.nodeName == 'exposant':
          finaltext += maybe_translate(c, superscript_chars_mapping)
        elif root.nodeName == 'indice':
          finaltext += maybe_translate(c, subscript_chars_mapping)
        else:
          finaltext += maybe_normalize(c.nodeValue)
      if c.nodeType == c.ELEMENT_NODE:
        finaltext += recursive_text(c)
  return finaltext

def extract_sentences(arr, min_words, max_words, nlp=None):
  full_text = ' '.join(arr)
  if nlp == None: #if no nlp object were passed, we use basic sentence splitting      
    raw_sentences = (full_text).split('. ')
  else: 
    #if we pass a nlp object, we use the Spacy library. See example in libretheatre.py
    #There's a 1000000 character limit in Spacy NER parser, so we need to avoid passing a too long text
    text_list = textwrap.wrap(full_text, 999999, break_long_words=False)
    all_sentences = []
    for chunk in text_list:
        doc = nlp(chunk, disable=["ner", "parser"])  
        #Retrieve a list of common nouns, pronouns, and expressions in the doc. We'll use them to spot stage directions
        most_common_expressions = common_nouns(doc) + common_collocations(chunk)
        #Retrieve a sentence list, removing stage directions (see maybe_clean_stage_directions function )
        raw_sentences = [maybe_clean_stage_directions(sent, most_common_expressions) for sent in doc.sents]
        #maybe_clean_stage_directions function returns "None" when a stage direction is spotted, so we have to remove None items from the list
        raw_sentences = [sentence for sentence in raw_sentences if sentence != None]
        all_sentences += raw_sentences
  return filter(lambda x: len(splitIntoWords(x)) >= min_words and len(splitIntoWords(x)) <= max_words, all_sentences) #raw_sentences)

def check_output_dir(output):
  if not os.path.isdir(output):
    print('Directory does not exists', output, file=sys.stderr)
    sys.exit(1)

def common_collocations(text, occurences=20):
  tokens = word_tokenize(text)
  final_results = []
  for measures, collocationFinder, min_size in [(BigramAssocMeasures(), BigramCollocationFinder, 2), (TrigramAssocMeasures(), TrigramCollocationFinder, 3)]:
    m = measures
    finder = collocationFinder.from_words(tokens, window_size=min_size)
    finder.apply_word_filter(lambda w: len(w) < 2)
    finder.apply_freq_filter(1)
    results = finder.nbest(m.student_t, occurences)
    final_results += [" ".join(gram) for gram in results]
  return final_results
  
def common_nouns(doc):
       
  nouns = [token.text for token in doc if token.is_stop != True and token.is_punct != True and token.pos_ in ["NOUN", "PROPN"]]
  word_freq = Counter(nouns)
  word_list = [word for word, occ in word_freq.most_common(15) if occ > 2] 
  return word_list 

def maybe_clean_stage_directions(sentence, most_common_expressions):
  """ Fonction destinée à supprimer les didascalies du texte
      et à faire quelques nettoyages divers sur les phrases
  """
  #cleaning the beginning of the sentence (removing punctuations and spaces)
  while sentence[0].pos_ in ["PUNCT", "SPACE"]:
    sentence = sentence[1:]
    if sentence.text == "":
        break
    
  #Don't keep sentences longer than 4 words
  if len([word for word in sentence if word.is_punct == False and word.is_space == False]) < 4: 
    return None  
  
  #All-caps word followed by a punctuation mark: certainly a stage direction (Example : "ALFRED, déconcerté")
  if sentence[0].is_upper and sentence[1].is_punct: 
    return None
  #Frequent word starting the sentence, and followed by a punctuation mark -> stage direction
  elif sentence[0].text in most_common_expressions and sentence[1].is_punct: 
    return None
  #Frequent collocation starting the sentence, and followed by a punctuation mark -> stage direction. Example: "Le marquis, hésitant".
  elif sentence[0:2].text in most_common_expressions and sentence[3].is_punct: 
    return None
  #Two all-caps word starting the sentence
  elif sentence[0].is_upper and sentence[1].is_upper: 
    #followed by a punctuation mark: stage direction. Example : "LA COMTESSE, troublée".
    if sentence[2].is_punct: 
      return None    
    #followed by a capitalized word: probably a character's name followed by her line. 
    elif sentence[2].text[0].isupper() and sentence[2].is_upper == False: 
      #let's remove the character's name
      return sentence[2:].text  
  #All-caps word starting a sentence, followed by a capitalized word, not followed by a punctuation mark: probably a character's name followed by her line
  elif sentence[0].is_upper and sentence[1].text[0].isupper() and sentence[1].is_punct == False:
    return sentence[1:].text #Removing the character's name at the sentence's start
  #Like above, except we check the 3 first words instead
  elif sentence[0].is_upper and sentence[1].is_upper and sentence[1].text[0].isupper() and sentence[1].is_punct == False: 
    return sentence[2:].text  
  #If it's an all-caps sentence, then it's certainly a stage direction. Example: "IN THE WORKSHOP"
  elif sentence.text.isupper(): 
    return None
  #If it's a sentence among the most common expressions in the text, it's certainly a stage direction
  elif sentence.text in most_common_expressions: 
    return None
  else:
    return sentence.text

def set_custom_boundaries(doc):
  for token in doc[:-1]:
    next_token = doc[token.i+1]  
    if token.text in [";", ","] or next_token.text[0].islower():
      doc[token.i+1].is_sent_start = False
    elif doc[token.i+1].is_punct and doc[token.i+1].text not in ["-"]:
      doc[token.i+1].is_sent_start = False  
    elif token.text in ['.', '!', '?', "...", "…"]: 
      doc[token.i+1].is_sent_start = True    
  return doc

def correct_sentence(text, lang_code):
    tool = language_check.LanguageTool(lang_code)    
    while True:
        matches = tool.check(text)
        #can't use automatic correction if there's no suggestion
        matches = [match for match in matches if match.ruleId != "HUNSPELL_NO_SUGGEST_RULE"]
        if len(matches) == 0:
            break        
        text = language_check.correct(text, matches)   
    return text
