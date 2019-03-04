#!/usr/bin/python

from .clauseParser import parse
import sys

def match(buyBounds, sellBounds, priority):
    for b in buyBounds:
        for s in sellBounds:
            price_overlap = overlap(b.pl, b.pu, s.pl, s.pu)
            quantity_overlap = overlap(b.ql, b.qu, s.ql, s.qu)
            if price_overlap and quantity_overlap:
                if priority == 'buyer':
                    pv = max(b.pl, s.pl)
                else:
                    pv = min(b.pu, s.pu)
                qv = min(b.qu, s.qu)
                #print("Match found:\n{}\n{}\nPrice: {} or {}\nQuant: {}".format(b.toStr(), s.toStr(), pv_buyer, pv_seller, qv))
                return pv,qv
    return None
                
def overlap(lb1, ub1, lb2, ub2):
    if lb2 > ub1 or ub2 < lb1 :
        return False
    return True
    
def parseString(string):
    return parse(string);