#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 17 17:45:55 2018

@author: rita
"""

import pytest

def create_parser():
    from custom_tokenizer import tokenizer
    return tokenizer.Parser()


#Check for correct exception raising
def test_type_error ():
    parser_object = create_parser()
    with pytest.raises(TypeError):
        parser_object.process_text(10)
        
def test_empty_input_error ():
    parser_object = create_parser()
    with pytest.raises(ValueError):
        parser_object.process_text('')

#Check correct responses
@pytest.mark.parametrize(
    "test_input, expected_raw", 
    [
     ("The houze is blue", 
      ["The", "houze", "is", "blue"]),
     ("The fox cn't jump over the fence", 
      ["The", "fox", "cn't", "cn't", "jump", "over", "the", "fence"]),
     ("Frankly, my dear, I don't give a durn.", 
      ["Frankly", ",", "my", "dear", ",", "I", "don't", "don't", "give", "a", 
       "durn", "."]), 
     ("I'm gonna make him an offre he can't refuse.",
      ["I'm", "I'm", "gonna", "gonna", "make", "him","an", "offre", "he", 
       "can't", "can't", "refuse", "."]), 
     ("You don't understand! I coulda had clas. I coulda been a contender. I could've been somebody, instead of a bum, which is what I am.", 
      ["You", "don't", "don't", "understand", "!", "I", "coulda", "coulda", 
       "had", "clas", ".", "I", "coulda", "coulda", "been", "a", "contender", 
       ".", "I", "could've", "could've", "been", "somebody", ",", "instead", 
       "of", "a", "bum", ",", "which", "is", "what", "I", "am", "."]), 
     ("I dunno what ya mean!", 
      ["I", "dunno", "dunno", "dunno", "what", "ya", "mean", "!"])
    ])
        
def test_raw_matches(test_input, expected_raw):
    parser_object = create_parser()
    full_response = parser_object.process_text(test_input)
    obtained_raw = [t['raw'] for t in full_response['tokens']]
    assert obtained_raw == expected_raw

    
@pytest.mark.parametrize(
    "test_input, expected_pos", 
    [
     ("The houze is blue", 
      ["DET", "NOUN", "VERB", "ADJ"]),
     ("The fox cn't jump over the fence",
      ["DET", "NOUN", "VERB", "ADV", "VERB", "ADP", "DET", "NOUN"]),
     ("Frankly, my dear, I don't give a durn.", 
      ["ADV", "PUNCT", "ADJ", "NOUN", "PUNCT", "PRON", "VERB", "ADV", "VERB", 
       "DET", "NOUN", "PUNCT"]), 
    ("I'm gonna make him an offre he can't refuse.", 
     ["PRON", "VERB", "VERB", "PART", "VERB", "PRON", "DET", "NOUN", "PRON", 
      "VERB", "ADV", "VERB", "PUNCT"]), 
    ("You don't understand! I coulda had clas. I coulda been a contender. I could've been somebody, instead of a bum, which is what I am.", 
     ["PRON", "VERB", "ADV", "VERB", "PUNCT", "PRON", "VERB", "VERB", "VERB", 
      "NOUN", "PUNCT", "PRON", "VERB", "VERB", "VERB", "DET", "NOUN", "PUNCT", 
      "PRON", "VERB", "VERB", "VERB", "NOUN", "PUNCT", "ADV", "ADP", "DET", 
      "NOUN", "PUNCT", "ADJ", "VERB", "NOUN", "PRON", "VERB", "PUNCT"]), 
    ("I dunno what ya mean!", 
     ["PRON", "VERB", "ADV", "VERB", "NOUN", "PRON", "VERB", "PUNCT"])
    ]) 
        
def test_pos_matches(test_input, expected_pos):
    parser_object = create_parser()
    full_response = parser_object.process_text(test_input)
    obtained_pos = [t['pos'] for t in full_response['tokens']]
    assert obtained_pos == expected_pos
 
    
@pytest.mark.parametrize(
    "test_input, expected_token", 
    [
     ("The houze is blue", 
      ["The", "house", "is", "blue"]), 
     ("The fox cn't jump over the fence", 
      ["The", "fox", "ca", "n't", "jump", "over", "the", "fence"]),
     ("Frankly, my dear, I don't give a durn.", 
      ["Frankly", ",", "my", "dear", ",", "I", "do", "n't", "give", "a", 
       "durn", "."]), 
     ("I'm gonna make him an offre he can't refuse.", 
      ["I", "'m", "gonn", "a", "make", "him", "an", "offer", "he", "ca", 
       "n't", "refuse", "."]), 
     ("You don't understand! I coulda had clas. I coulda been a contender. I could've been somebody, instead of a bum, which is what I am.", 
      ["You", "do", "n't", "understand", "!", "I", "could", "a", "had", 
       "class", ".", "I", "could", "a", "been", "a", "contender", ".", "I", 
       "could", "'ve", "been", "somebody", ",", "instead", "of", "a", "bum", 
       ",", "which", "is", "what", "I", "am", "."]), 
     ("I dunno what ya mean!", 
      ['I', 'du', 'n', 'no', 'what', 'ya', 'mean', '!'])
    ])
        
def test_token_matches(test_input, expected_token):
    parser_object = create_parser()
    full_response = parser_object.process_text(test_input)
    obtained_token = [t['token'] for t in full_response['tokens']]
    assert obtained_token == expected_token
    
