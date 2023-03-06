import sys
from parse_python import parse_file, read_file_to_string
from build import main
import os
import traceback
import ast

# ---------- parse pyhon2 files to cfg with parse_cfg.py ---------- #

examples = r"C:/Users/ninas/OneDrive/Documents/UNI/Productive-Bachelors/DATA/data2"
output ='OUTPUT/my_dataset_cfg'

def prep_path(path):
    x = '\\\\?\\' + path.replace('/','\\')
    print "hello"
    return x


def test_output_cfg():           
    with open(output_cfg,'w') as out, open(path, 'r')as f:
        print >>out, parse_file_2cfg(test)
        print "finished :)"

def parse_data(f):
    i =0
    with open(output,'w') as out, open('OUTPUT/errorlog2.txt', 'w') as errorlog:
        for root, _, files in os.walk(f):
            for file in files:
                if i > 100:
                    return 
                path = prep_path(os.path.join(root, file))
                try:
                    with open(path, 'r', )as f:
                        print >>out, main(path)
                        s = "done " + str(i)
                        print s
                        i = i+1
                except Exception as e:
                        errorlog.write(path + " " + str(e) + "\n")
                        # errorlog.write(traceback.format_exc() + "\n")
    print "finished :)"
    return

parse_data(examples)




    