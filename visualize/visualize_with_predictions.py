import sys
import json
import re
import random
import math

#dev file
squad_file = sys.argv[1]
#directory to write
outdir = sys.argv[2]
#
mi = int(sys.argv[3])+1

#in quac format
predictions_file = open(sys.argv[4])

id_prediction = {}
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

print(mi)

for _item in data["data"]:
  title = u"{}".format(_item["title"])
  ix = int(random.random()*len(_item["paragraphs"]))
  for i,_p in enumerate(_item["paragraphs"]):
     if i != ix : continue
     output = ""
     mi -=1
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
       

       if "abstractive_answer" in _q and len(_q["abstractive_answer"].strip()) > 0:  output += "{ ``"+clean(_q["abstractive_answer"]["text"])+"'' ("+clean(_q["orig_answer"]["text"])+" ) }\n"
       else: output += "{ "+clean(_q["orig_answer"]["text"])+" }\n"
       output+="\\\\\n" 
       for _a in _q["answers"]:
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
       
       pred = id_prediction[qid] 
       output += "\\speak{System}{"
       if pred[1] == "y": output +=  "\\colorbox{red!25}{Yes,}\n"
       if pred[1] == "n": output +=  "\\colorbox{red!25}{No,}\n"
       output +=  clean(pred[0]) + "}"  
       output += "\\\\\n"
       if t >= 3: 
         figures += basefigure.replace(replace_str, output)
         output = ""
         t = 0
     if len(output) > 0:
       figures += basefigure.replace(replace_str, output)
     
     title_i = re.sub(r'\W+', '', title_i)
     o = base.replace(replace_str, figures).replace(context_str, clean(context))
     of = open(outdir + "/"+title_i+".tex","w")
     of.write(o.encode('utf-8'))
     of.close()
     if mi<0: exit()
