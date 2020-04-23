import os

rule_path = os.path.join(os.path.dirname(__file__),'rules')

def write_file(filename, string):
    file = open(os.path.join(rule_path,filename),'w')
    file.write(string)
    file.close()

def read_answer(filename):
    return open(os.path.join(rule_path,"{}.answers".format(filename)),"r").read()