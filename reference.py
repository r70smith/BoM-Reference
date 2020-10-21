"""
Book of Mormon Scripture Reference Converter Module Version 1.1
Programmer: Ron Smith
Date: September 5, 2020
Converts scripture references from RLDS to LDS and vice versa.
"""


debug = False

def initializeGlobals():
    global BOM,RLDS,LDS
    BOM = BookNames()
    inFile = open("BoMConversion.txt","r")
    RLDS,LDS = getTables(inFile)
    inFile.close()

class IntRange(list):
    """List of inclusive integer ranges [a,b] with a <= b.
         Ranges are sorted AND separate. That is,
         0 ≤ i < len(list)-1 => list[i][1] + 1 < list[i+1][0]
    """
        
    def isSeparate(self,a,b):
        """Return 0 if ranges a,b overlap or are contiguous, otherwise +-1"""
        if a[1] < b[0]-1:
            result = -1
        elif a[0] > b[1]+1:
            result = 1
        else:
            result = 0
        return result


    def insert(self,a,b):
        if debug: print("insert [{},{}]".format(a,b))
        if a > b:
            raise ValueError("Decreasing Integer Range.")
        self.append([a,b])
        self.sort()
        t = [i for i in range(len(self)) if not self.isSeparate((a,b),self[i]) ]
        self[t[0]][1] = max(b,self[t[-1]][1])   #Replace all with this range
        for i in t[:0:-1]:
            self.pop(i)

class BookNames():
    """Manage Book of Mormon book names and printing styles.
        ATTRIBUTE     TYPE     COMMENT
        styleList     list     [str] Abbreviation style names, e.g. "RCE"
        rldstyle      int      Default for RLDS references (chosen by user)
        ldstyle       int      Default for LDS references (chosen by user)
        nameList      list     Book names indexed by [book,style] integers
        nameDict      dict     Book Numbers indexed by hashed abbreviation

        METHOD             COMMENT
        bookNum(s)         Book str to int 1Nephi=1 ... Moroni=15
        spell(s,style)     Bootk str <s> to str with style number <style>
        setStyle(den,style) Sets default for denomination to style number
        bookStr(s,styleNo) Rewrite str w/ style number w/o error correnction

        PRIVATE METHODS    COMMENT
        chunk(s)           Splits str into strings of alpha, digit, non-blank
        bigChunk(s)        Combines chunks for book name lookup
        hsh (s)            Simple hash function for nameDict
    """
    
    def __init__(self,rldstyle=1,ldstyle=3):    #Default styles: RLDS 1908,LDS 1951
        self.styleList = "Long,RLDS 1908,Zion Bound,LDS 1982,Temple Lot,RCE".split(",")
        self.rldstyle = rldstyle    #index to styleList: Output style for RLDS refs
        self.ldstyle = ldstyle      #index to styleList: Output style for LDS refs
        self.nameList = None        #For name output. Filled below
        self.nameDict = {}          #name input->book num. Filled below
        self.hsh = lambda x: x.replace(" ","").replace(".","").upper()

        long = "1 Nephi,2 Nephi,Jacob,Enos,Jarom,Omni,Words of Mormon,Mosiah," + \
               "Alma,Helaman,3 Nephi,4 Nephi,Mormon,Ether,Moroni"
        long = long.split(",")
        r1908 = "1 N,2 N,Jb,En,Jm,O,WM,Mos,A,H,3 N,4 N,Mn,E,Mi".split(",")
        zb = "1N,2N,Jac,En,Jar,Om,WoM,Mos,Al,He,3N,4N,Mor,Eth,Mni".split(",")
        l1981 = "1 Ne.,2 Ne.,Jacob,Enos,Jarom,Omni,W of M,Mosiah,Alma,Hel.," + \
                "3 Ne.,4 Ne.,Morm.,Ether,Moro."
        l1981 = l1981.split(",")
        t1990 = "I Ne.,II Ne.,Jacob,Enos,Jarom,Omni,WM,Mos.,Alma,Hel.," + \
                "III Ne.,IV Ne.,Mor.,Ether,Mrni."
        t1990 = t1990.split(",")
        rce   = "1N,2N,Jac,En,Jar,O,WM,Mos,A,H,3N,4N,Mn,Eth,Mi".split(",")
        self.nameList = [long,r1908,zb,l1981,t1990,rce]
        for i in range(len(self.nameList)):
            for j in range(len(self.nameList[i])):
                name = self.nameList[i][j]
                self.nameDict[self.hsh(name)] = j+1
        N1 = [(num + name,1) for num in ["FIRST","1ST"] for name in ["N","NE","NEPHI"]]
        N2 = [(num + name,2) for num in ["SECOND","2ND"] for name in ["N","NE","NEPHI"]]
        N3 = [(num + name,11) for num in ["THIRD","3RD"] for name in ["N","NE","NEPHI"]]
        N4 = [(num + name,12) for num in ["FOURTH","4TH"] for name in ["N","NE","NEPHI"]]
        for name,n in N1+N2+N3+N4:
            self.nameDict[name]=n
          

    def __str__(self):
        return ",".join(self.nameList[0])   #Long

    def __repr__(self):
        s = "BookNames:\n   styleList: {}\n   rldstyle: {} ldstyle: {}\n   " + \
            "nameList: {}\n   nameDict: {}\n   hsh(): {}"
        return s.format(self.styleList,self.rldstyle,self.ldstyle,self.nameList,
                        self.nameDict,self.hsh)

    def bookNum(self,s):
        """Return book number for (any abbr. of) s; 1 = 1 Nephi .. 15 = Moroni"""
        if self.hsh(s) in self.nameDict:
            return self.nameDict[self.hsh(s)]
        return 0

    def spell(self,book,style = 0):
        return self.nameList[style][book-1]

    def setStyle(self,denomination,style):
        if denomination == "RLDS":
            self.rldstyle = style
        elif denomination == "LDS":
            self.ldstyle = style

    def chunk(self,s):
        """Split s into chunks: groups of alpha, digit, non-blanks."""
        if len(s)==0:
            return []
        i=0
        c = s[0]
        if c == " ":
            return self.chunk(s[1:])
        else:
            while i<len(s) and                              \
                 s[i].isalpha()==c.isalpha() and s[i].isdigit()==c.isdigit():
                 i += 1
            return [s[:i]] + self.chunk(s[i:])

    def bigChunks(self,s):
        """Combine chunks as needed"""
        combine = "ST,ND,RD,RTH,TH,OF,. ,N,NE,NEPHI".split(",")
        big = []
        chunkList = self.chunk(s)
        for i in range(len(chunkList)):
            c = chunkList[i]
            if i > 0:
                b = big[-1]
                if c.upper() in combine:
                    big[-1] = b+c
                elif len(b)>2 and b[-2:].upper() == "OF":
                    big[-1] = b+c
                else:
                    big.append(c)
            else:
                big.append(c)
        return big
            

    def bookStr(self,s,styleNo):
        """reWrite string s using book style number. No error correction."""
        chunkList = self.bigChunks(s)
        newList = []
        for c in chunkList:
            n = BOM.bookNum(c)
            if c in ";,":       #Restore <Space> after comma or semicolon
                c += " "    
            elif  n > 0:        #Translate bookName
                c = BOM.spell(n,styleNo)+" "
            newList.append(c)
        return ''.join(newList)

        
class Reference():
    """Maintain Denomination (LDS or RLDS), list of (Book, Chapter, Verse-range).

            ATTRIBUTE     TYPE     FORM             COMMENT
            denomination  String   'LDS' | 'RLDS'         
            refList       IntRange [[i,j]]          Inclusive range of indices 

            PUBLIC METHODs         ARG              COMMENT
            printStyle(style)      range(6)         defined in BOM
            reset()                                 set refList = [] only
            getDenomination()                       Return 'LDS' | 'RLDS'
            otherDenomination()                     Return 'RLDS' | 'LDS'
            getDenoinationPtr()                     (book,chapter,verse) list
            insert(s)              String           Insert RefString(s)
            translate()                             Return Reference

            PRIVATE METHODS        ARG              COMMENT
            
        New in this version:
        1.  Reference does not specify print style.
        2.  Reference initializes without string. They must be inserted.
        3.  Reference cannot change denomination.
    """
    
    def __init__(self,denomination):
        if denomination.upper() in ["RLDS","LDS"]:
            self.denomination = denomination
        else:
            raise ValueError("Unrecognized denomination")
        self.refList = IntRange([])
                    
    def __repr__(self):
        return "Reference denomination:{} refList:{}".format(
            self.denomination,self.refList)

    def __str__(self):
        style = {"RLDS":BOM.rldstyle,"LDS":BOM.ldstyle}[self.denomination]
        return self.printStyle(style)

    def printStyle(self,style):
        den = self.getDenominationPtr()
        cvList = []
        previous = ["","",""]
        for i in range(len(self.refList)):
            p0,p1 = self.refList[i]
            s,previous = self.bcvStr(p0,p1,previous,style)
            cvList.append(s)
        return ", ".join(cvList)

    def reset(self):
        self.refList = IntRange([])

    def getDenomination(self):
        return self.denomination        #Return "LDS" or "RLDS"

    def getDenominationPtr(self):
        t = {"LDS":LDS,"RLDS":RLDS}
        return t[self.denomination]     #Return pointer to table LDS or RLDS

    def otherDenomination(self):
        t = {"RLDS":"LDS","LDS":"RLDS"}
        return t[self.denomination]

    def insert(self,s):
        r = RefString(s)
        den = self.getDenominationPtr()
        m = r.bcvList
        for i in range(0,len(m),2):
            try:
                j = den.index(m[i])
                k = den.index(m[i+1])
                self.refList.insert(j,k)  #Integer range [j,k]
            except ValueError:
                print(r)
                raise
        
    def bcvStr(self,p0,p1,previous = ["","",""],style = 0):
        """Reconstruct b c:v-v string from denomination table, eliminating previous."""
        
        def gather(book,chapter,verse,previous):
            s = ""
            if book != previous[0]:
                previous = [book,chapter,verse]
                s = "{} {}:{}".format(book,chapter,verse)
            elif chapter != previous[1]:
                previous[1:] = [chapter,verse]
                s = "{}:{}".format(chapter,verse)
            elif verse != previous[2]:
                previous[2] = verse
                s = verse
            return s,previous
                    
        if debug: print("bcvStr p0:{} p1:{}".format(p0,p1))
        den = self.getDenominationPtr()
        b0,c0,v0 = den[p0]                  #Convert to [book,chapter,verse] strings
        s0,previous = gather(BOM.spell(b0,style),str(c0),str(v0),previous)
        b1,c1,v1 = den[p1]   
        s1,previous = gather(BOM.spell(b1,style),str(c1),str(v1),previous)
        if not s1:
            s = s0
        else:
            s = "{}–{}".format(s0,s1)
        if debug: print(s)
        return s,previous
        
    def  copy(self):
        new = Reference(self.denomination)
        new.refList = self.refList[:] 
        return new

    def expand(self):
        """Include largest index of same (b,c,v) """
        den = self.getDenominationPtr()
        newList = IntRange([])
        for p0,p1 in self.refList:      #Increase p1 to include larger verses
            a = den[p1]              #a = (book,chapter,verse)
            p = p1
            while p < len(den) and den[p]==a and p-p0 < 5:  #infinity
                p1 = p
                p += 1
            newList.insert(p0,p1)
        self.refList = newList

        
    def translate(self):
        t = self.copy()
        t.expand()                                  #Expand uses original denomination
        t.denomination = self.otherDenomination()   #Must follow expansion!
        return t
        

def getTables(inFile):
    """Flatten inFile and split into two lists [(book,chapter,verse)]"""
##    global BOM
    rTable = []  
    lTable = []
    for line in inFile:
        line = line.strip()
        if len(line)>0:
            n = BOM.bookNum(line)
            if n > 0:
                bookNum = n
            else:       #line form is 'c0:v0[-v2]   c1:v1'
                line = line.replace("–","-")
                rlds,lds = line.split()
                c0,v02 = rlds.split(":")
                v02 = v02.split("-")
                v0 = v02[0]
                v2 = v02[-1]  #incase '-v2' is not in line
                c1,v1 = lds.split(":")
                try:
                    c0,v0,v2,c1,v1 = int(c0),int(v0),int(v2),int(c1),int(v1)
                except ValueError:
                    print("Error in geTables:{}".format(line))
                    print("c0:{} v0:{} v2:{} c1:{} v1:{}".format(c0,v0,v2,c1,v1))
                    raise
                for v in range(v0,v2+1):
                    rTable.append((bookNum,c0,v))
                    lTable.append((bookNum,c1,v1))
    return rTable,lTable

def extractDenomination(s):
    """Return (denomination,remainder)"""
    if "RLDS" in s:
        den = "RLDS"
        t = s.split("RLDS")
        s = "".join(t)
    elif "LDS" in s:
        den = "LDS"
        t = s.split("LDS")
        s = "".join(t)
    else:
        den = ""
    if "(" in s:
        s = s.replace("(","")
        s = s.replace(")","")
    s = s.strip()
    return den,s


class RefString():
    """A RefString is a list of 'book chapter:verse' references. Specifically:
          RefString -> ";" delimited list of RefList
          RefList   -> "," delimited list of bcvString omitting redundancies (see note)
          RefString  -> "-" delimited pair of bcvStrings omitting redundancies (see note)
          bcvString -> '<book> <chapter>:<verse>'
       Note: Normal form of a RefString is 'book0 chapter0:verse0-book1 chapter1:verse1'
             If book1 == book0, the RefString is 'book0 chapter0:verse0-chapter1:verse1'
             If also chapter1 == chapter0, RefString is 'book0 chapter0:vers0-verse1'
             If also verse1 == verse0, the RefString is 'book0 chapter0:verse0'
             Reduncancies in RefLists are treated similarly
      Internally, a bcv is an integer tuple (<bookNum>,<chapter>,<verse>).
      Each bcvString is represented by a pair of bcv's with no redundancy.
      Consequently, each ReString is represented internally with a list of bcv pairs with no redundancy.
    """
    def __init__(self,s):
        
        def splitList(aList,s):
            """split each item of aList on character s; return union"""
            return [ x for y in aList for x in y.split(s)]

        def bcv(s):
            """s = 'b c:v' ->(b,c,v) """
            s = s.strip()
            if s.isdigit():             #Verse only
                return (-1,-1,int(s))
            bc,v = s.split(":")
            bc = bc.strip()
            v = int(v.strip())
            if bc.isdigit():            #Chapter only
                return (-1,int(bc),int(v))
            b,c = bc.rsplit(" ",1)
            b = b.strip()
            return (BOM.bookNum(b),int(c),int(v))

        def inherit(bcvList,b0=-1,c0=-1,v0=-1):
            if len(bcvList) == 0:
                    return []
            b,c,v = bcvList[0]
            if b == -1:
                b = b0
            else:
                b0 = b
            if c == -1:
                c = c0
            else:
                c0 = c
            return [(b,c,v)] + inherit(bcvList[1:],b0,c0,v0)
                    

        def parse(s):
            s = s.replace("–","-")      #Short dash only
            t = splitList([s],";")      #Eliminate Semicolon
            t = splitList(t,",")        #Eliminate Comma
            bcvStrings = []
            for item in t:              #Dash-separated bcv pairs, duplicate where needed
                if "-" in item:
                    bcvStrings += item.split("-")
                else:
                    bcvStrings += [item,item]
            bcvTuples = [bcv(item) for item in bcvStrings]
            bcvList = inherit(bcvTuples)
            return bcvList

        #Body of __init__                 
        self.s = s
        self.bcvList = parse(s)

    def __str__(self):
        return self.s

    def __repr__(self):
        return "RefString(s:{}, bcvList:{})".format(self.s,self.bcvList)
         
    
initializeGlobals()

def main():
    global LDS,RLDS
    s = "Third N 10:22, 1st N 2:231-235, III Ne. 6:1, Jb 2:22; W of M 1:1"
    print(s)
    for n in range(len(BOM.styleList)):
        print(BOM.bookStr(s,n))
    ##print(bookStr(s,0))        
    ref = Reference("RLDS")
    s = input("Reference (RLDS):")
    while len(s) > 0:
        den,s = extractDenomination(s)
        if den:
            ref = Reference(den)
        else:
            ref.reset()
        if s:
            ref.insert(s)
            tref = ref.translate()
            print("=> {} ({})".format
                  (tref,tref.getDenomination()))
            ref.reset()
        s = input("Reference ({}):".format(ref.getDenomination()))

if __name__ == "__main__":
    
    main()
