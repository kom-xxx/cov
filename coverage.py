#!/usr/bin/env python

import sys
from os.path import exists as file_exists
from getopt import getopt

class disasm:
    condition = ['EQ', 'NE', 'CS', 'HS', 'CC', 'LO', 'MI', 'PL',
                 'VS', 'VC', 'LS', 'GE', 'LT', 'GT', 'LE', 'AL']
    qualifier = ['N', 'W']

    def __read_disasm(self, fn):
        with open(fn, 'r') as rs:
            start = False
            text = False
            label_stack = []
            for _line in rs:
                line = _line.split()
                if not line:
                    continue
                if (not text and line[0] == '**' and line[1] == 'Section' and
                    line[3] == "'.text'"):
                    text = True
                    continue
                if text and line[0] == 'Address:':
                    start = True
                    continue
                if not start or not text:
                    continue
                if start and text and line[0] == '**':
                    start = False
                    text = False
                    continue

                if not line[0].startswith('0'):
                    label_stack.append(line[0])
                    continue

                addr = int(line[0][0:-1], 0)
                if label_stack:
                    self.hash[addr] = {'line':line, '_line':_line,
                                       'labels':label_stack,
                                       'it':False, 'is':False}
                else:
                    self.hash[addr] = {'line':line, '_line':_line,
                                       'it':False, 'is':False}
                label_stack = []

    def __init__(self, disasm, hash_file):
        self.hash_file = hash_file
        if not file_exists(self.hash_file):
            self.hash = {}
            if not disasm:
                raise RuntimeError("No disassemle file specified.")
            self.__read_disasm(disasm)
        else:
            with open(self.hash_file, 'r') as f:
                buff = f.read()
                self.hash = self.eval(buff)

    def save_hash(self):
        with open(hash_file, 'w') as hfile:
            print(self.hash)

    def mark_inst(self, tarmac_file):
        with open(tarmac_file, 'r') as rs:
            for line in rs:
                line = line.split()
                if line[2] != 'IT' and line[2] != 'IS':
                    continue

                addr = int(line[4], 16)
                inst = self.hash[addr]
                inst[line[2].lower()] = True

    def write_list(self, ofile_name):
        keys = sorted(self.hash.keys())
        with open(ofile_name, 'w') as ofile:
            for key in keys:
                elt = self.hash[key]
                if 'labels' in elt and elt['labels']:
                    print('', file=ofile)
                    for label in elt['labels']:
                        print(label, file=ofile)
                line = elt['line']
                inst = line[3].split('.')
                mark = '-'
                if inst[0] != 'SVC' and inst[0][-2:] in self.condition:
                    if elt['it'] and elt['is']:
                        mark = '*'
                    elif elt['it']:
                        mark = '+'
                    elif elt['is']:
                        mark = '!'
                else:
                    if elt['it']:
                        mark = '*'
                if not '_line' in elt:
                    print(elt)
                print('{}{}'.format(mark, elt['_line']), file=ofile, end='')

def main():
    hash_file = "__coverage.hash"
    disasm_file = None
    opts, args = getopt(sys.argv[1:], 'd:h:o:')

    for opt in opts:
        if opt[0] == '-d':
            disasm_file = opt[1]
        elif opt[0] == '-h':
            hash_file = opt[1]
        elif opt[0] == '-o':
            ofile = opt[1]
        else:
            pass

    if disasm_file and file_exists(disasm_file):
        da = disasm(disasm_file, hash_file)
    elif not file_exists(hash_file):
        print("coverage file {} not found and disassemble file not specified"
              .format(hash_file), file=sys.stderr)
        sys.exit(1)
    else:
        with open(hash_file, "r") as f:
            buf = f.read()
            inst_hash = eval(buf)
            if not inst_hash:
                print("empty coverage file", file=sys.stderr)
                sys.exit(1)
            else:
                da = disasm(None, hash_file)

    for arg in args:
        da.mark_inst(arg)

    if ofile:
        da.write_list(ofile)

if __name__ == '__main__':
    if sys.argv == ['']:
        sys.argv = ['',
                    '-d', 'calculator-aarch32.disasm',
                    '-o', 'calculator-aarch32.disasm.out',
                    'calculator-aarch32-fastmodel.tarmac']
    main()
