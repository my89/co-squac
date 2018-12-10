import argparse
import sys
import re
import json
import string
from evals.coqa_eval import CoQAEvaluator
from collections import defaultdict, Counter

def parse_args():
  parser = argparse.ArgumentParser('Measure max F1 for a CoQA dataset under extractive search')
  parser.add_argument('--input_file', help='Input JSON file in CoQA data format.', required=True)
  parser.add_argument('--print_low', help='Print items with F1 lower than .8', default=False, action="store_true")
  return parser.parse_args()
 
p = parse_args()
#file to eval
file_to_eval = p.input_file
#sys.argv[1]
#whether to print the low extractiveness f1 examples
print_low = p.print_low
#int(sys.argv[2])

data = json.load(open(file_to_eval))["data"]
yes_no = ["yes", "no"]

def find_max_f1(gold, other):
  other_tok = other.split() #default python splitting
  mx = -1
  current_best = None
  
  for i in range(0, len(other_tok)):
    for j in range(i , len(other_tok)):
       other_str = ' '.join(other_tok[i:j+1])
       #this could be made more efficient caching the cleaning and splits, but eh...
       f1 = CoQAEvaluator.compute_f1(gold, other_str)
       if f1 >= mx:
         mx = f1
         current_best = other_str
  return (mx, current_best) 

total_questions = 0
total_f1 = 0.0 
low_f1 = 0

for (_i, item) in enumerate(data):

  if len(data) < 1000: 
    if _i % 100 == 0 : print("{}/{}".format(_i, len(data)))
  else:
    if _i % 500 == 0 : print("{}/{}".format(_i, len(data)))

  for k,answer in enumerate(item["answers"]):
    answer_span = []
    answer_text = []

    answer_span.append(answer["span_text"])
    answer_text.append(answer["input_text"])
    if "additional_answers" in item:
      _item = item["additional_answers"]
      for (_, other_answer) in _item.items():
         answer_span.append(other_answer[k]["span_text"])
         answer_text.append(other_answer[k]["input_text"])    
    
    f1s = []
  
    for aids in range(0, len(answer_span)):
     _answer_text = answer_text[aids]
     _answer_span = answer_span[aids]
     
     #save time by not compute f1 if they are exactly identical
     if CoQAEvaluator.normalize_answer(_answer_text) in CoQAEvaluator.normalize_answer(_answer_span): f1s.append(1.0)
     else:
      tkns = CoQAEvaluator.get_tokens(_answer_text)
      #handle yes/no: if the answer is exactly one token and it is 'yes' or 'no', we can handle it 
      if len(tkns) == 1 and tkns[0] in yes_no:
        #print(tkns)
        f1s.append(1.0)
      else: 
        #find the span from the answer span that has highest f1
        (f1, mx) = find_max_f1(_answer_text, _answer_span)
        f1s.append(f1)

    #compute the leave one out upper bound (which is a bit less bc sometimes we will get unlucky)
    if len(f1s) > 1:
      tot = 0
 
      for j in range(0, len(f1s)):
        _f1s = list(f1s) 
        del _f1s[j]
        tot += max(_f1s)
      
      total_f1 += tot / len(f1s)
    else:
      total_f1 += f1s[0]

    if max(f1s) < .8:
      low_f1 += 1
      if print_low:
        print("f1 = {}".format(f1s))
        print("question : {}".format(item["questions"][k]["input_text"]))
        print("answer_spans : {}".format(answer_span))
        print("answer_texts : {}".format(answer_text))
        print("--------")
    total_questions += 1

print("total f1 < .8 = {} out of total = {} ({:.2f}%)".format(low_f1, total_questions, 100*float(low_f1)/total_questions))
print("extractive f1 = {:.3f}".format(total_f1/total_questions))

