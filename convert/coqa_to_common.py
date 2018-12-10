import argparse
import sys
import re
import json
import string
from evals.coqa_eval import CoQAEvaluator
from collections import defaultdict, Counter

def parse_args():
  parser = argparse.ArgumentParser('Convert CoQA to common format')
  parser.add_argument('--input_file', help='Input CoQA JSON file.', required=True)
  parser.add_argument('--output_file', help='Model predictions.', required=True)
  parser.add_argument('--context_word_threshold', help="Remove contexts that are longer than the word threshold", default=99999, type=int)
  parser.add_argument('--max_span_length', help="When searching for the best extractive span, limit the length", default=9999, type=int)
  parser.add_argument('--have_span', help="If testing, this should be set to zero, forcing the script to search for the best extraction answer in the whole context as opposed to in the retionale span", default=1, type=int)
  parser.add_argument('--have_predictions', help="If testing, and you are missing spans, the models own predictions for yes/no can be used as previous spans", default=None, type=str)
  return parser.parse_args()

p = parse_args()

file_to_convert = p.input_file#
file_to_write = p.output_file
word_threshold = p.context_word_threshold
max_span = p.max_span_length
have_span = p.have_span
have_predictions = p.have_predictions

if have_predictions is not None:
 print("using predictions to fill yes/no")
 predictions_file =  p.have_predictions
 have_predictions = True
else:
 have_predictions = False

if not have_span: 
  print("using paragraph for matching... this could take a while...")
if have_predictions:
  #use this to fix up the yes/no.... if you don't have spans
  f = open(predictions_file)
  model_predictions = {}
  for line in f.readlines():
     s = json.loads(line)
     for i in range(0, len(s["best_span_str"])):
       model_predictions[s["qid"][i]] = s["best_span_str"][i]

data = json.load(open(file_to_convert))["data"]
yes_no = ["yes", "no"]

def find_max_f1(gold, other):

  gold_tok = gold.split()
  other_tok = other.split() #default python splitting
  current_best = other
  mx = CoQAEvaluator.compute_f1(gold, other)

  for i in range(0, len(other_tok)):
    for j in range(i , len(other_tok)):
       if j - i > max_span: continue
       other_str = ' '.join(other_tok[i:(j+1)])
       #this could be made more efficient caching the cleaning and splits, but eh...
       f1 = CoQAEvaluator.compute_f1(gold, other_str)
       if f1 >= min(len(gold_tok), mx):
         if mx == f1 and len(other_str) > len(current_best): continue
         mx = f1
         current_best = other_str
  return (mx, current_best) 

total_questions = 0
cannot_answer = 0

quac_style = []

def find_majority(entries):
  dd = defaultdict(int)
 
  for e in entries:
    dd[e] += 1

  return sorted(dd.items(), key=lambda x: -x[1])[0][0] 

new_data = []
doc_len = defaultdict(int)

print("searching for answers with max F1...")
for (_i, item) in enumerate(data):
  qd = {}
  qd["title"] = item["filename"]
  paragraph = {}
  tokenized_paragraph =  (item["story"] + " CANNOTANSWER").replace("(" , " (").split()
  doc_len[int(len(tokenized_paragraph)/100)]+=1
  if len(tokenized_paragraph) > word_threshold: continue 
  story_text = ' '.join(tokenized_paragraph)
  paragraph["context"] = story_text   
  qas = []
   
  _id = item["id"]
   
  #print(_i)
  if len(data) < 1000: 
    if _i % 50 == 0 : print("{}/{}".format(_i, len(data)))
  else:
    if _i % 500 == 0 : print("{}/{}".format(_i, len(data)))

  for k,answer in enumerate(item["answers"]):
    total_questions += 1
    answer_span = []
    answer_text = []

    if "additional_answers" in item:
      _item = item["additional_answers"]
      for (_, other_answer) in _item.items():
         if have_span: answer_span.append(' '.join(other_answer[k]["span_text"].replace("(", " (").split()))
         answer_text.append(' '.join(other_answer[k]["input_text"].replace("(", " (").split()))  
   
    if have_span: answer_span.append(' '.join(answer["span_text"].replace("(", " (").split()))
    answer_text.append(' '.join(answer["input_text"].replace("(", " (").split()))
     
    f1s = []
    spans = []
    yesno = []
    unknown = []    
 
    for aids in range(0, len(answer_text)):
     _answer_text = answer_text[aids]
     if have_span : _answer_span = answer_span[aids]
     else: _answer_span = story_text
     
     tkns = CoQAEvaluator.get_tokens(_answer_text)
    
  #handle yes/no: if the answer is exactly one token and it is 'yes' or 'no', we can handle it 
     if len(tkns) == 1 and tkns[0] in yes_no:
        f1s.append(1.0)
        if have_predictions:
          spans.append(model_predictions["{}_q#{}".format(_id,k)])
        elif len(qas) > 0 :
          #we set the target to what we predicted
          spans.append(qas[-1]["answers"][aids]["text"])
        else:
          #print("adding first word, {}".format(k))
          spans.append(story_text.split()[0])
          #spans.append(_answer_span)
        yesno.append(tkns[0][0])
        
        unknown.append("n")
     elif len(_answer_span) == 0 or _answer_span == "unknown":
        f1s.append(1.0)
        spans.append("CANNOTANSWER")
        yesno.append("x")
        unknown.append("y")
     else: 
        #find the span from the answer span that has highest f1
        (f1, mx) = find_max_f1(_answer_text, _answer_span)
        #if _answer_text in mx and len(mx.split()) > len(_answer_text.split()):
        #  print("error: {},  {}".format(_answer_text, mx))
        #  exit()
          
        f1s.append(f1)
        spans.append(mx)
        yesno.append("x")
        unknown.append("n")
    
    original_answer = spans[-1]
    yesno_majority = find_majority(yesno)
    unknown_majority = find_majority(unknown)
    if unknown_majority == "y":
      cannot_answer += 1
    #print("{} -> {}".format(yesno, yesno_majority))
    _qas = {}
    _qas["yesno"] = yesno_majority
    _qas["question"] = item["questions"][k]['input_text']
    #print(original_answer)
    _qas["orig_answer"] = {"text":original_answer, "answer_start": story_text.index(original_answer)}
    _qas["abstractive_answer"] = {"text":_answer_text}
    _qas["followup"] = "y"
    _qas["id"] = "{}_q#{}".format(_id,k)
    _qas["orig_span"] = _answer_span
    all_answers = []
    for span in spans:
      #print(_qas["question"])
      #print(span)
      all_answers.append({"text":span, "answer_start":story_text.index(span)})
    _qas["answers"] = all_answers
    
    qas.append(_qas)

  paragraph["qas"] = qas
  qd["paragraphs"] = [paragraph]
  new_data.append(qd)    

print("done")
print("cannot answer (total, total_questions, portion) {} {} {}".format(cannot_answer , total_questions, 100*float(cannot_answer)/total_questions))
print(doc_len)
print("{}/{} total conversations in base on thresholds".format(len(new_data), len(data)))

of = open(file_to_write, "w")
json.dump({"data":new_data}, of)
of.close()


