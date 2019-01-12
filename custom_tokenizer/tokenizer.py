#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 09:13:17 2018

@author: rita
"""

from flask import Flask
from flask_restful import Api, Resource, reqparse
import re, pickle, os
from string import punctuation
import spacy
import enchant
from spacy.attrs import ORTH, LEMMA, POS


class Parser(Resource):
    
    def __init__(self):
    
        # Word collocations dictionary obtained by scraping the Online Oxford Collocation Dictionary
        colls_dict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'collocations_dict.pickle')
        with open(colls_dict_path, 'rb') as file:
            self.colls_dict = pickle.load(file)
        # Spell checking tool
        self.spell_checker = enchant.Dict("en_US")
        self.nlp = spacy.load('en')
        # String to convert words into regular expressions that match those words in the string they may appear in 
        # regardless of the place where they may be found
        self.regexer = "^({0})(?=[\W_])|(?<=[\W_])({0})(?=[\W_])|(?<=[\W_])({0})$"
        # Regular expression to match punctuation (excluding apostrophes)
        self.punct_re = re.compile('|'.join(map(re.escape, [punct for punct in punctuation if not re.match(r"\'", punct)])))
        # The cases I want Spacy's tokenizer to handle differently to how they are usually handled.
        self.neg_cases = [
                {'string': "dunno", 'substrings': [{ORTH: "du", LEMMA: "do", POS: "VERB"}, {ORTH: "n", LEMMA: "not", POS: "ADV"}, {ORTH: "no", LEMMA: "know", POS: "VERB"}]},
                {'string': "I'm", 'substrings': [{ORTH: "I", LEMMA: "-PRON-", POS: "PRON"}, {ORTH: "'m", LEMMA: "be", POS: "VERB"}]},
                {'string': "I've", 'substrings': [{ORTH: "I", LEMMA: "-PRON-",  POS: "PRON"}, {ORTH: "'ve", LEMMA: "have", POS: "VERB"}]},
                {'string': "gonna", 'substrings': [{ORTH: "gonn", LEMMA: "go", POS: "VERB"}, {ORTH: "a", LEMMA: "to", POS: "PART"}]},
                {'string': "coulda", 'substrings': [{ORTH: "could", LEMMA: "can", POS: "VERB"}, {ORTH: "a", LEMMA: "have", POS: "VERB"}]},
                {'string': "could've", 'substrings': [{ORTH: "could", LEMMA: "can", POS: "VERB"}, {ORTH: "'ve", LEMMA: "have", POS: "VERB"}]},
                {'string': "you're", 'substrings': [{ORTH: "you", LEMMA: "-PRON-", POS: "PRON"}, {ORTH: "'re", LEMMA: "be", POS: "VERB"}]},
                {'string': "they're", 'substrings': [{ORTH: "they", LEMMA: "-PRON-", POS: "PRON"}, {ORTH: "'re", LEMMA: "be", POS: "VERB"}]},
                {'string': "isn't", 'substrings': [{ORTH: "is", LEMMA: "be", POS: "VERB"}, {ORTH: "n't", LEMMA: "not", POS: "ADV"}]},
                {'string': "aren't", 'substrings': [{ORTH: "are", LEMMA: "be", POS: "VERB"}, {ORTH: "n't", LEMMA: "not", POS: "ADV"}]},
                {'string': "won't", 'substrings': [{ORTH: "wo", LEMMA: "will", POS: "VERB"}, {ORTH: "n't", LEMMA: "not", POS: "ADV"}]},
                {'string': "didn't", 'substrings': [{ORTH: "did", LEMMA: "do", POS: "VERB"}, {ORTH: "n't", LEMMA: "not", POS: "ADV"}]},
                {'string': "don't", 'substrings': [{ORTH: "do", LEMMA: "do", POS: "VERB"}, {ORTH: "n't", LEMMA: "not", POS: "ADV"}]},
                {'string': "doesn't", 'substrings': [{ORTH: "does", LEMMA: "do", POS: "VERB"}, {ORTH: "n't", LEMMA: "not", POS: "ADV"}]},
                {'string': "ain't", 'substrings': [{ORTH: "ai", LEMMA: "be", POS: "VERB"}, {ORTH: "n't", LEMMA: "not", POS: "ADV"}]}, 
                {'string': "couldn't", 'substrings': [{ORTH: "could", LEMMA: "can", POS: "VERB"}, {ORTH: "n't", LEMMA: "not", POS: "ADV"}]},
                {'string': "can't", 'substrings': [{ORTH: "ca", LEMMA: "can", POS: "VERB"}, {ORTH: "n't", LEMMA: "not", POS: "ADV"}]},
                {'string': "wouldn't", 'substrings': [{ORTH: "would", LEMMA: "will", POS: "VERB"}, {ORTH: "n't", LEMMA: "not", POS: "ADV"}]},
                {'string': "mustn't", 'substrings': [{ORTH: "must", LEMMA: "must", POS: "VERB"}, {ORTH: "n't", LEMMA: "not", POS: "ADV"}]}
                ]
        
        for dict_i in self.neg_cases:
            self.nlp.tokenizer.add_special_case(dict_i.get('string'), dict_i.get('substrings')) 
           

    def process_text(self, sent):
        
        """
        Function to tokenize a given string and return a dictionary comprised of, in turn, 
        one dictionary per token, containing the information on the appearance the word it 
        stems from has, as well as the part-of-speech tag Spacy assigns to it, the token, that is. 
        
        Parameters:
        -----------
            sent (str): The string to be tokenized.
        
        Returns:
        --------
            tokens_dict (dict): The aforementioned dictionary.
            
        """
        
        # Checking the input's format
        if not isinstance(sent, str):
            raise TypeError("The input has to be of type str.")
            
        if len(sent) == 0:
            raise ValueError("The string passed as input was found to be empty.")
        
        parsed_text = self.nlp(sent)
        # I want to replicate the behavior of Spacy's tokenizer when splitting into words 
        # to build a list containing the words to which Spacy's tokens can be mapped to. 
        split_sent = [elem for elem in re.split(r'([^\w\'])', sent) if elem and not re.search(r'\s', elem)]    
        tok0 = []
        values = []
        for i in range(len(parsed_text)):
            # I want to first find the word the token at issue derived from.
            raw0 = [elem for elem in split_sent 
                    if re.search(re.compile(parsed_text[i].orth_), elem)]
            if raw0:
                raw = raw0[0]
            else:
                raw = parsed_text[i].orth_
            
            # Deleting from my list of original words the one I have already linked to the token at hand 
            # if the token is followed by a space or if the following token is a punctuation mark. 
            if re.search(r'\s', parsed_text[i].text_with_ws) or re.match(self.punct_re, parsed_text[min(i+1, len(parsed_text)-1)].orth_):
                del split_sent[0]
            
            # The rules that make a word worthy of being considered correctly spelled.
            spell_check_cond0 = self.spell_checker.check(raw)
            spell_check_cond1 = re.search(self.punct_re, parsed_text[i].orth_)
            spell_check_cond2 = raw.islower() != True
            spell_check_cond3 = re.search(re.compile(raw), '|'.join(map(re.escape, [case.get('string') for case in self.neg_cases])))
        
            # If a word cannot be considered correctly spelled ...
            if not (spell_check_cond0 or spell_check_cond1 or spell_check_cond2 or spell_check_cond3):
                # ... from the list containing the different available options to serve as replacements
                # I want to select the best candidate by checking if any of the alternatives 
                # matches a word collocation of the surrounding words or if any of the surrounding words is, 
                # in turn, a word collocation of any of the available candidates. 
                immediate_context = parsed_text[max(0, i-4): min(len(parsed_text)-1, i+3)]
                colls = sum([list(self.colls_dict.get(c.orth_)) for c in immediate_context if self.colls_dict.get(c.orth_)], [])
                pos_tok, colls_tok = [], []
                viable_candidates = [a.orth_ for a in immediate_context 
                                     if (re.search(r'(nound|adv|adj|verb|adp)', str(a.pos_), re.I) and not
                                         re.search(re.compile('be|' + raw.lower()), str(a.lemma_)))]
                immediate_context_re = self.regexer.format('|'.join(viable_candidates))
                # I want to go through the list of possible candidates backwards, 
                # because it is arranged according to the likelihood the words in it have of being 
                # the correct candidates for replacing mispelled words, 
                # from the most to the least likely.
                for p in self.spell_checker.suggest(raw)[::-1]:
                    if (re.search(re.compile(self.regexer.format(p)), ' '.join(colls)) or
                        (self.colls_dict.get(p) and re.search(re.compile(immediate_context_re, re.I), ' '.join(list(self.colls_dict.get(p)))))):
                        colls_tok.append(p)
                    else:
                        # Alternatevely, I want to see if the POS tag assigned to each of the viable candidates
                        # is one that would make sense for the correct replacement to have assigned to it, 
                        # given the POS tag assigned to the nucleus of the clause the supposedly mispelled word belongs to.
                        parsed_alt = self.nlp(re.sub(raw, p, sent))
                        cond0 = re.search(r'(NOUN|ADV)', str(parsed_text[i].head.pos_)) and parsed_alt[i].pos_ == 'ADJ'
                        cond1 = parsed_text[i].head.pos_ == 'VERB' and re.search(r'(NOUN|ADV)', str(parsed_alt[i].pos_))
                        cond2 = parsed_text[i].head.dep_ == 'nsubj' and parsed_alt[i].pos_ == 'VERB'
                        if cond0 or cond1 or cond2:
                            pos_tok.append(p)
                        else:
                            continue
                
                # The last element I have iterated over is the most likely 
                # to be the correct candidate for replacement.
                if colls_tok:
                    corrected_raw = colls_tok[-1]
                elif pos_tok:
                    corrected_raw = pos_tok[-1]
                else:
                    corrected_raw = p
            else:
                corrected_raw = raw
               
            parsed_alter = self.nlp(re.sub(re.escape(raw), corrected_raw, sent))
            tok = [str(t) for t in self.nlp.tokenizer(corrected_raw)]
            # If I have already built my tokens' dictionary 
            # from the list of tokens a given word can be split into, 
            # I don't want to do it again.
            if tok != tok0:
                for t in tok:
                    tokens = {}
                    tokens['raw'] = raw
                    if t == raw:
                        tokens['pos'] = parsed_text[i].pos_
                    else:
                        tokens['pos'] = [word.pos_ for word in parsed_alter if word.orth_ == t][0] 
                    tokens['token'] = t
                    values.append(tokens)
                
            tok0 = tok
        
        
        tokens_dict = {'tokens': values}
        return tokens_dict

    def post(self):
        # Parse input arguments
        parser = reqparse.RequestParser()
        parser.add_argument("input")
        args = parser.parse_args()
        
        # Check for correct input
        try:
            sent = args.get('input')
        except:
            return {}, 400
        
        try:
            # Perform tokenization
            tokens_dict = self.process_text(sent)
        except:
            return {}, 400
                
        return tokens_dict, 200



def create_app():    
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Parser, "/tokenise/")
    return app
 
    
def launch_app():
    app = create_app()
    app.run(debug=True)



    
if __name__ == '__main__':
   launch_app()
