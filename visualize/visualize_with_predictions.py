import sys
import argparse
import json
import re
import random
import math

def parse_args():
  parser = argparse.ArgumentParser('Visualize a dataset in common format, optionally with predictions')
  parser.add_argument('--input_file', help='Input JSON file in common format.', required=True)
  parser.add_argument('--output_directory', help='directory to output LaTEX files', required=True)
  parser.add_argument('--examples', help='The number of examples to visualize', default=1, type=int)
  parser.add_argument('--predictions', help='Prediction file in QuAC format', default="")
  parser.add_argument('--interactions', help='Create a new figure every K interactions', default=3, type=int)
  parser.add_argument('--references', help='Output up to R additional references', default=0, type=int)
  return parser.parse_args()

p = parse_args()
squad_file = p.input_file
outdir = p.output_directory 
mi = p.examples
split_k = p.interactions
reference_n = p.references
id_prediction = {}
#in quac format
if len(p.predictions) > 0: 
  predictions_file = open(p.predictions)
  for line in predictions_file.readlines():
    struct = json.loads(line)
    for i in range(0, len(struct["best_span_str"])):
      qid = struct["qid"][i]
      span = struct["best_span_str"][i]
      yesno = struct["yesno"][i]
      followup = struct["followup"][i]
      id_prediction[qid] = (span, yesno, followup)

data = json.load(open(squad_file))

base = open("visualize/base.tex").read()

context_str = "!!CONTEXT!!"
replace_str = "!!REPLACEME!!"

basefigure = "\\begin{figure}[t] \\small \\begin{tcolorbox}[boxsep=0pt,left=5pt,right=0pt,top=2pt,colback = yellow!5] \\begin{dialogue}\n \\small \n !!REPLACEME!! \\end{dialogue}\\end{tcolorbox}\\end{figure}"

random.shuffle(data["data"])

def clean(s): return s.replace('"', "''").replace("_", " ").replace("%"," ").replace("$"," ")

#print(mi)

outputs = set()
while len(outputs) < mi:
 for _item in data["data"]:
  title = u"{}".format(_item["title"])
  if "section_title" in _item: title = u"{} -- {}".format(title, _item["section_title"])
  ix = int(random.random()*len(_item["paragraphs"]))
  for i,_p in enumerate(_item["paragraphs"]):
     if i != ix : continue
     output = ""
     title_i = title + "{}\\\\".format(i)

     context = "\hspace{15pt}{\\textbf{Section}:"+clean(title_i)+"}\n"
     context += "\\\\ Context: " + clean(_p["context"])
     t = 0
     figures = ""
     for _q in _p["qas"]:
       t += 1     
       output += "\\speak{Student}{\\bf "+_q["question"]+" }\n"
       qid = _q["id"]
       fu = _q["followup"]
       yn = _q["yesno"]
       output += "\\speak{Teacher}"
       if fu == "y":
         output += "\\colorbox{pink!25}{$\\hookrightarrow$}\n"
       elif fu == "n":
         output += "\\colorbox{pink!25}{$\\not\\hookrightarrow$}\n"
       else:
         output += "\\colorbox{pink!25}{ $\\bar{\hookrightarrow}$}\n"
       if yn == "y":
         output += "\\colorbox{red!25}{Yes,}\n"
       elif yn == "n":
         output += "\\colorbox{red!25}{No,}\n"
       
       if "abstractive_answer" in _q and len(_q["abstractive_answer"]["text"].strip()) > 0:  output += "{ ``"+clean(_q["abstractive_answer"]["text"])+"'' ("+clean(_q["orig_answer"]["text"])+" ) }\n"
       else: output += "{ "+clean(_q["orig_answer"]["text"])+" }\n"
       #output+="\\\\\n" 
       for r,_a in enumerate(_q["answers"]):
         if r >= reference_n: break
         output += "\\speak{TeacherX}"
         if fu == "y":
           output += "\\colorbox{pink!25}{$\\hookrightarrow$}\n"
         elif fu == "n":
           output += "\\colorbox{pink!25}{$\\not\\hookrightarrow$}\n"
         else:
           output += "\\colorbox{pink!25}{ $\\bar{\hookrightarrow}$}\n"
         if yn == "y":
           output += "\\colorbox{red!25}{Yes,}\n"
         elif yn == "n":
           output += "\\colorbox{red!25}{No,}\n"
       
         output += "{ "+clean(_a["text"])+" }\n"
       
       if len(id_prediction) > 0:
         pred = id_prediction[qid] 
         output += "\\speak{System}{"
         if pred[1] == "y": output +=  "\\colorbox{red!25}{Yes,}\n"
         if pred[1] == "n": output +=  "\\colorbox{red!25}{No,}\n"
         output +=  clean(pred[0]) + "}"  
         #output += "\\\\\n"
       if t >= split_k: 
         figures += basefigure.replace(replace_str, output)
         output = ""
         t = 0
       else: output+="\\\\\n" 

     if len(output) > 0:
       figures += basefigure.replace(replace_str, output)
     
     title_i = re.sub(r'\W+', '', title_i)
     o = base.replace(replace_str, figures).replace(context_str, clean(context))
     of = open(outdir + "/"+title_i+".tex","w")
     of.write(o.encode('utf-8'))
     of.close()
     outputs.add(outdir + "/"+title_i+".tex")
     if len(outputs) >= mi: exit()

