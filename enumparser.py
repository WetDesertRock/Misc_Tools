import sys, os, pprint

if len(sys.argv) != 3:
    print("Invalid usage, enumparser.py <outtype> <directory>")
else:
    targetdir = sys.argv[2]
    outtype = sys.argv[1]
    
files = []
for f in os.listdir(targetdir):
    if f.endswith('.cpp') or f.endswith('.h'):
        files.append(os.path.join(targetdir,f))


rawenums = []
for fpath in files:
    with open(fpath,'r') as file:
        inenum = False
        curenum = ""
        for line in file:
            line = line.strip()
            if inenum:
                curenum += "\n"+line
                
            if line.startswith("enum ") or line.startswith("enum{") or line == "enum":
                inenum = True
                curenum += line
            
            if "}" in line:
                if inenum:
                    inenum = False
                    rawenums.append(curenum)
                    curenum = ""

enums = []
for enum in rawenums:
    enum = enum[enum.find("{")+1:enum.find("}")]
    lines = enum.split('\n')
    for i,line in enumerate(lines):
        if "//" in line:
            cstart = max(0,line.find('//')-1) #Deal with if our comment is on the same line
            line = line[:cstart]
        
        lines[i] = line.strip()
    
    values = "".join(lines).split(',')
    
    edict = {}
    counter = 0
    for entry in values:
        entry = entry.replace(' ','').replace('\t','')
        if "=" in entry:
            name,value = entry.split('=')
            value = eval(value) #eval because we might get stuff like 1<<2
            counter = value+1
        else:
            name = entry
            value = counter
            counter += 1
        
        edict[name] = value

    enums.append(edict)


if outtype.lower() == "vars":
    for d in enums:
        l = sorted(d,key=lambda x:d[x])
        for i in l:
            print("%s = %d"%(i,d[i]))
        print("\n")
elif outtype.lower() == "dicts":
    for d in enums:
        pprint.pprint(d)
elif outtype.lower() == "dictlist":
    pprint.pprint(enums)