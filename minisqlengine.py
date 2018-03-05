
import collections
import sqlparse
import sys
import ast
    
metadata=open('metadata.txt','r')
metadata=metadata.read()
metadata=metadata.replace('\n',';').replace('\r',';').split(';')
lines=[]
for i in metadata:
    if i=='':
        continue
    else:
        lines.append(i)
tables=collections.OrderedDict()
#print 'lines1= ',lines
flag=0
tablename='';
files=[]
for i in lines:
    if i=='<begin_table>':
        flag=1
    elif i=='<end_table>':
        flag=0
    elif flag==1:
        tables[i]=collections.OrderedDict()
        tablename=i
        files.append(tablename)
        flag=2
    else:
        tables[tablename][i]=[]

for i in files:
    datafile=open(i+'.csv')
    datafile=datafile.read()
    datafile=datafile.replace('\n',';').replace('\r',';').split(';')
    rows=[]
    for j in datafile:
        if j=='':
            continue
        rows.append(j)
    count=0
    keys=list(tables[i].keys())
    for j in rows:
        cols=j.split(',')
        for k in range(len(cols)):
            tables[i][keys[k]].append(cols[k])
    #print 'rows= ',rows

query=''
query=' '.join(sys.argv[1:])
#print 'tables= ',tables
#print 'query= ',query

statement=sqlparse.format(query,reindent=True,keyword_case='upper')

#print 'statement= ',statement
keywords={'SELECT':[],'FROM':[],'WHERE':[],'DISTINCT':[]}
combinators=['AND','OR']
operators=['=','>','<','>=','<=']
display=collections.OrderedDict();
allflag=0
split1=statement.split('SELECT')
#print 'split1=',split1
if len(split1)<2:
    print 'Error! Incorrect syntax for SELECT'
    sys.exit()
phrase=split1[1]
#print 'phrase= ',phrase
split2=phrase.split('FROM')
if len(split2)<2:
    print 'Error! Incorrect syntax for FROM'
    sys.exit()
#print 'split2=',split2
split3=split2[0].replace('\n','$').replace('\r','$').replace(',','$').replace('\t','$').replace(' ','$').split('$')
#print 'split3=',split3
for i in split3:
    if i=='' or i==' ':
        continue
    keywords['SELECT'].append(i.encode('ascii'))
phrase=split2[1].split('WHERE')
split4=phrase[0].replace(',','$').replace('\n','$').replace('\r','$').replace(' ','$').replace('\t','$').replace(';','$').split('$')
prop=''
for i in split4:
    if i=='' or i==' ':
        continue
    keywords['FROM'].append(i.encode('ascii'))  
for i in keywords['FROM']:
    if i not in files:
        print 'Error! '+i+' is not a valid table name!'
        sys.exit()
    display[i]=collections.OrderedDict()
#print 'display= ',display
if len(phrase)>1:
    phrase[1]=phrase[1].encode('ascii')

if keywords['SELECT']==['*']:
    for i in keywords['FROM']:
        for j in list(tables[i].keys()):
            display[i][j]=[]
else:
    for i in keywords['SELECT']:
        attrflag=0
        if '.' in i:
            split5=i.split('.')
            if split5[1] in list(tables[split5[0]].keys()):
                attrflag=1
                display[split5[0]][split5[1]]=[]
            #print split5
        elif '(' in i:
            if ')' not in i:
                print 'Error! Incorrect brackets!'
                sys.exit()
            split5=i.split('(')
            split6=split5[1].split(')')
            prop=split5[0]
            if split6[0] not in tables[keywords['FROM'][0]]:
                print 'Error! '+split6[0]+' is not a valid attribute!'
                sys.exit()
            display[keywords['FROM'][0]][split6[0]]=[]
            #print "dd",display
            attrflag=1
        else:
            for j in keywords['FROM']:
                if i in list(tables[j].keys()):
                    if attrflag==1:
                        print 'Error! '+i+' is ambiguous!'
                        sys.exit()
                    attrflag=1
                    display[j][i]=[]
        #print "dd",display
        #print "dff",split3
        if(split3[1]=='DISTINCT'):
        	attrflag=1;
        	prop='DISTINCT'
        if attrflag==0:
            print 'Error! '+i+' is not a valid attribute!'
            sys.exit()
#print 'display= ',display
conditions=[]
outputs=[]
#print "phase", phrase
if len(phrase)==1:
    if prop=='':
        for i in display:
            for j in display[i]:
                for k in tables[i][j]:
                    display[i][j].append(k)
    elif prop.upper()=='DISTINCT':
        for i in display:
            for j in display[i]:
                for k in tables[i][j]:
                    if k in display[i][j]:
                        continue
                    else:
                        display[i][j].append(k)
    elif prop.upper()=='MAX':
        for i in display:
            #print i
            for j in display[i]:
                print 'MAX('+i+'.'+j+')'
                maximum=tables[i][j][0]
                for k in tables[i][j]:
                    if eval(k+'>'+maximum)==True:
                        maximum=k
                print maximum
    elif prop.upper()=='AVG':
        for i in display:
            #print i
            for j in display[i]:
                print 'AVG('+i+'.'+j+')'
                average=0
                count=0
                for k in tables[i][j]:
                    average=average+int(k)
                    count=count+1
                average=float(average)/count
                print average
    elif prop.upper()=='SUM':
        for i in display:
            #print i
            for j in display[i]:
                print 'SUM('+i+'.'+j+')'
                add=0
                for k in tables[i][j]:
                    add=add+int(k)
                print add
    elif prop.upper()=='MIN':
        for i in display:
            #print i
            for j in display[i]:
                print 'MIN('+i+'.'+j+')'
                minimum=tables[i][j][0]
                for k in tables[i][j]:
                    if eval(k+'<'+minimum)==True:
                        minimum=k
                print minimum
else:
    combinator=''
    if 'OR' in phrase[1]:
        split6=phrase[1].split('OR')
        conditions.append(split6[0].replace('\n','').replace(' ',''))
        conditions.append(split6[1].replace('\n','').replace(' ',''))
        combinator='or'
    elif 'AND' in phrase[1]:
        split6=phrase[1].split('AND')
        conditions.append(split6[0].replace('\n','').replace(' ',''))
        conditions.append(split6[1].replace('\n','').replace(' ',''))
        combinator='and'
    else:
        conditions.append(phrase[1])
    intermediates=[]
    digitflag=1
    for i in conditions:
        for j in operators:
            if j in i:
                op=j
        split7=i.split(op)
        j=split7[1].strip()
        try:
            j=int(j)
        except ValueError:
            digitflag=0
    if digitflag==0:
        split7=conditions[0].split('=')
        split8=split7[0].strip().split('.')
        split9=split7[1].strip().split('.')
        #print split8
        #print split9
        if split8[0] in tables and split8[1] in tables[split8[0]] and split9[0] in tables and split9[1] in tables[split9[0]]:
            table1=split8[0].strip()
            table2=split9[0].strip()
            attr1=split8[1].strip()
            attr2=split9[1].strip() 
            display[table2].pop(attr2,None)
            for i in range(len(tables[table1][attr1])):
                for j in range(len(tables[table2][attr2])):
                    if tables[table1][attr1][i]==tables[table2][attr2][j]:
                        for k in display[table1]:
                            display[table1][k].append(tables[table1][k][i])
                        for k in display[table2]:
                            display[table2][k].append(tables[table2][k][j])
        elif split8[0] not in tables or split8[1] not in tables[split8[0]]:
            print 'Error! '+split8[1]+' is not a valid attribute of '+split8[0]+'!'
            sys.exit()
        else:
            print 'Error! '+split9[1]+' is not a valid attribute of '+split9[0]+'!'
            sys.exit()
    else:
        count=-1
        for i in conditions:
            count=count+1
            intermediates.append([])
            for j in operators:
                if j in i:
                    op=j
            split7=i.split(op)
            if op=='=':
                op='=='
            j=split7[0]
            j=j.strip()
            if '.' in j:
                split8=j.split('.')
                if split8[0] in tables and split8[1] in tables[split8[0]]:
                    for k in tables[split8[0]][split8[1]]:
                        intermediates[count].append(eval(k+op+split7[1]))
                else:
                    print 'Error! '+split8[1]+' is not a valid attribute of '+split8[0]+'!'
                    sys.exit()
            else:
                attrflag=0
                for k in keywords['FROM']:
                    if j in tables[k]:
                        if attrflag==1:
                            print 'Error! '+j+' is ambiguous!'
                            sys.exit()
                        attrflag=1
                        table_name=k
                if attrflag==0:
                    print 'Error! '+j+' is not a valid attribute!'
                    sys.exit()
                for k in tables[table_name][j]:
                    intermediates[count].append(eval(k+op+split7[1]))
        if combinator=='':
            for i in intermediates[0]:
                outputs.append(i)
        else:
            for i in range(len(intermediates[0])):
                outputs.append(eval(str(intermediates[0][i])+' '+combinator+' '+str(intermediates[1][i])))
        for i in display:
            for j in display[i]:
                for k in range(len(tables[i][j])):
                    if outputs[k]==True:
                        display[i][j].append(tables[i][j][k])

done=[]
#print 'hey',prop
if prop=='' or prop.upper()=='DISTINCT':
    count=0
    if len(list(display.keys()))==1:
        tablename=display.keys()[0]
        for i in display[tablename]:
            print tablename+'.'+i+'\t',
        print
        for i in range(len(display[tablename][list(display[tablename].keys())[0]])):
            for j in display[tablename]:
                print display[tablename][j][i]+'\t',
            print
    else:
        for i in list(display.keys()):
            done.append(i)
            for j in list(display.keys()):
                if j in done:
                    continue
                
                for k in list(display[i].keys()):
                    for l in list(display[j].keys()):
                        if k==l:
                            display[j].pop(k,None)
                for k in display[i]:
                    print i+'.'+k+'\t',
                for k in display[j]:
                    print j+'.'+k+'\t',
                print
                attrs1=list(display[i].keys())
                attrs2=list(display[j].keys())
                if len(phrase[1])==0:
                    for l in range(len(display[i][attrs1[0]])):
                        for m in range(len(display[j][attrs2[0]])):
                            for n in display[i]:
                                print display[i][n][l]+'\t',
                            for n in display[j]:
                                print display[j][n][m]+'\t',
                            print
                            count=count+1
                else:
                    for l in range(len(display[i][attrs1[0]])):
                        for n in display[i]:
                            print display[i][n][l]+'\t',
                        for n in display[j]:
                            print display[j][n][l]+'\t',
                        print
       # print "done=",done                       
#print "final display== ",display
