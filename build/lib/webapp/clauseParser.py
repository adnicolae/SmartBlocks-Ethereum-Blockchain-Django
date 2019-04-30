#!/usr/bin/python

import re

class Bounds:
    def __init__(self,pl=0,pu=2**31,ql=0,qu=2**31):
        self.pl = pl
        self.pu = pu
        self.ql = ql
        self.qu = qu
        
    def toStr(self):
        return "Bounds: {} < p < {} | {} < q < {}".format(self.pl, self.pu, self.ql, self.qu)

class Expression:
    def __init__(self,l,o,r):
        self.left = l
        self.op = o
        self.right = r
        
        self.bounds = []
        
        pl=0
        pu=2**31
        ql=0
        qu=2**31
        
        if(self.op == '<' or self.op == '='):
            if(self.left == 'p'):
                pu = self.right
            elif(self.left == 'q'):
                qu = self.right
        if(self.op == '>' or self.op == '='):
            if(self.left == 'p'):
                pl = self.right
            elif(self.left == 'q'):
                ql = self.right
                
        self.bounds.append(Bounds(pl,pu,ql,qu))
        
    
    def eval(self, p, q):
        if(self.op == '<'):
            if(self.left == 'p'):
                return p <= self.right
            elif(self.left == 'q'):
                return q <= self.right
        elif(self.op == '>'):
            if(self.left == 'p'):
                return p >= self.right
            elif(self.left == 'q'):
                return q >= self.right
        elif(self.op == '='):
            if(self.left == 'p'):
                return p == self.right
            elif(self.left == 'q'):
                return q == self.right
        
    def toStr(self):
        return "{} {} {}".format(self.left, self.op, self.right)

class Clause:
    def __init__(self,ex1,o,ex2):
        self.left = ex1
        self.op = o
        self.right = ex2
        
        self.bounds = []
        
        if(self.op == '+'):    
            for b1 in self.left.bounds :
                for b2 in self.right.bounds :
                    pl = max(b1.pl, b2.pl)
                    pu = min(b1.pu, b2.pu)
                    ql = max(b1.ql, b2.ql)
                    qu = min(b1.qu, b2.qu)
                    self.bounds.append(Bounds(pl,pu,ql,qu))
        elif(self.op == '/'):
            for b1 in self.left.bounds :                
                self.bounds.append(b1)
            for b2 in self.right.bounds :
                self.bounds.append(b2)
        
    def eval(self, p, q):
        if(self.op == '+'):
            return self.left.eval(p,q) and self.right.eval(p,q)
        elif(self.op == '/'):
            return self.left.eval(p,q) or self.right.eval(p,q)
            
    def boundsToStr(self):
        str = ''
        for b in self.bounds:
            str += "{}\n".format(b.toStr())
        return str
        
    def toStr(self):
        return "({} {} {})".format(self.left.toStr(), self.op, self.right.toStr())


def parse(inputString, v=0):
    if(v==1):
        print("Input String: ", inputString)

    #find clauses
    inputString = inputString.replace('AND', '+')
    inputString = inputString.replace('OR', '/')
    inputString = inputString.replace('price', 'p')
    inputString = inputString.replace('quantity', 'q')
    if(v==1):
        print("Input String: ", inputString)

    inputString = inputString.replace(' ', '')
    
    for c in inputString:
        if c not in ['+','/','p','q','<','=','>','(',')','1','2','3','4','5','6','7','8','9','0']:
            return None #error in input string

    #Expression regex: [pq][<=>][\d]+([.][\d]+)?
    #Clause regex: [(]?[ec][\d]+[+/][ec][\d]+[)]?

    allExpr = re.findall('[pq][<=>][\d]+\.\d+|[pq][<=>][\d]+', inputString)
    expressions = []

    index = 0
    for e in allExpr:
        expressions.append(Expression(e[0],e[1],float(e[2:])))
        inputString = inputString.replace(e,"e{}".format(index), 1)
        index+=1

    if(v==1):
        print("Input String: ", inputString)

    clauses = []
    index = 0
    allClauses = re.findall('[(]?[ec][\d]+[+/][ec][\d]+[)]?', inputString)
    while(allClauses != []):
        for c in allClauses:
            exprInClause = re.findall('[ec][\d]+', c)
            left = exprInClause[0]
            op = re.findall('[+/]', c)
            right = exprInClause[1]
            if(v==1):
                print(left, op[0], right)
            if(left[0]=="e"):
                left = expressions[int(float(left[1:]))]
            elif(left[0]=="c"):
                left = clauses[int(float(left[1:]))]
                
            if(right[0]=="e"):
                right = expressions[int(float(right[1:]))]
            elif(right[0]=="c"):
                right = clauses[int(float(right[1:]))]
                
            clauses.append(Clause(left, op[0], right))
            inputString = inputString.replace(c,"c{}".format(index), 1)
            index+=1
            
        if(v==1):
            print("Input String: ", inputString)
        allClauses = re.findall('[(]?[ec][\d]+[+/][ec][\d]+[)]?', inputString)
    
    if(len(clauses) == 0 or len(clauses) < len(expressions) - 1):
        return None
    return clauses[len(clauses)-1]