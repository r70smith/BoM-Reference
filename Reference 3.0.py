"""
Book of Mormon Reference Converter 3.0
Programmer: Ron Smith
Date: October 9, 2020
Converts scripture references from RLDS to LDS and vice versa.
With GUI implemented as class.

New in version 3.0:
Redesgned interface: refEntry is Textbox; Vertical layout
"""

from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from reference import *

"""Globals:
      RLDS, LDS: Tables with (book,chaper:verse) triples
      BOM: BookNames,StyleList, Abbreviations, etc.
"""


class ReferenceApp(Frame):
    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.master.title("Book or Mormon Reference Translation")
        self.pack()

        #Control Variables
        self.ref = Reference("RLDS")
        self.transRef = Reference("LDS")
        self.refEntry = Entry(None)     #Redefined in CreateWidgets
        self.inVar = StringVar()        #Controls refEntry
        self.outVar = StringVar()       #Controls refOut
        self.denomination=""            #'LDS' or 'RLDS' defined later
        self.rbox = None                #Combobox defined later
        self.lbox = None                #Combobox defined later
        self.rldstyle = StringVar()     #Combobox control
        self.ldstyle = StringVar()      #Combobox control
        
        self.createWidgets()
        
        #initialize variables
            #Entry/Output
        self.denomination = "RLDS"  
        self.inVar.set("(RLDS) ")
        self.refEntry.icursor(END)
        self.outVar.set("(LDS) ")
            #Style
        self.rldstyle.set("RLDS 1908")
        self.ldstyle.set("LDS 1982")
        self.rldstyle.trace_add(
            "write",lambda a,b,c,x="RLDS":self.applyStyle(x)) #Magic
        self.ldstyle.trace_add(
            "write",lambda a,b,c,x="LDS":self.applyStyle(x))  #Magic


    def createWidgets(self):
        #set up Frames: endtryFrame,styleFrame,bookFrame,keyFrame
        ioFrame = Frame(self,)
        ioFrame.grid(sticky = NSEW)
        
        inFrame = Frame(ioFrame,border = 10)
        inFrame.grid(row=0,column=0,sticky = EW)
        outFrame = Frame(ioFrame,border = 10)
        outFrame.grid(row=0,column=1,sticky = EW)
        
        styleFrame = Frame(self,border=10)
        styleFrame.grid(sticky = N)
       
        self.lstyleFrame=Frame(styleFrame)  #These are moved in switch()
        self.rstyleFrame=Frame(styleFrame)
        
        bookFrame = Frame(self,border=10)
        bookFrame.grid()
        
        keyFrame = Frame(self,border = 10)
        keyFrame.grid()

        

        #Entry widget
        self.refEntry = Entry(inFrame,width=35,
                              textvariable = self.inVar,)
        self.refEntry.grid(sticky = N)
        self.refEntry.bind("<Return>",self.submit)
 
        #Output widget
        self.refOut = Entry(outFrame,width = 35,
                            textvariable = self.outVar,state="readonly")   
        self.refOut.grid(sticky = NSEW)
        
        #Style Frame
        style = Style()
        style.configure("BigTimesText.TButton",font=('times',20,'bold'),
                        background = "White",)
        style.configure("BigCalibriText.TButton",font=('calibri',20,'bold'),
                        background = "White",)

        lbl = Label(self.rstyleFrame,text = "Style (RLDS)")
        lbl.grid()
        self.rbox = Combobox(self.rstyleFrame,state="readonly",
                             values = BOM.styleList,
                             textvariable = self.rldstyle,
                             width = 10, justify="center")
        self.rbox.grid()
        self.rstyleFrame.grid(column = 0)
        lbl = Label(self.lstyleFrame,text = "Style (LDS)")
        lbl.grid()
        self.lbox = Combobox(self.lstyleFrame,state="readonly",
                             values = BOM.styleList,
                             textvariable = self.ldstyle,
                             width = 10, justify="center")
        self.lbox.grid(row=1)
        self.lstyleFrame.grid(row=0,column=2)
        btn = Button(styleFrame,text = "<=>",style = "BigTimesText.TButton",
                     command = self.switchIO,)
        btn.grid(row=0,column=1,sticky = S)


        #Book buttons
        bookStr="1 Nephi,2 Nephi,Jacob,Enos,Jarom,Omni,W of M," + \
                 "Mosiah,Alma,Helaman,3 Nephi,4 Nephi,Mormon,Ether,Moroni"
        bookList = bookStr.split(",")
        for j in range(3):
            for i in range(5):
                n = 5*j+i
                btn = Button(bookFrame,text=bookList[n],
                             command=lambda x=n+1:self.abbreviate(x))
                btn.grid(row=i,column=j,sticky = W)
        
        #Set up keys
        for i in range(3):
            for j in range(3):
                n = str(3*i+j+1)
                btn = Button(keyFrame,text = n, width=5,
                             command = lambda x=n:self.entryInsert(x),)
                btn.grid(row=i,column=j)
        btn = Button(keyFrame,text = "0",
                     command = lambda x="0":self.entryInsert(x),
                     width=5,)
        btn.grid(row=3,column=1)
        btn = Button(keyFrame,text = ":",style = "BigTimesText.TButton",
                     command = lambda x=":":self.entryInsert(x),
                     width=4,)
        btn.grid(row=4,column=0)
        btn = Button(keyFrame,text = ", ",style = "BigTimesText.TButton",
                     command = lambda x=", ":self.entryInsert(x),
                     width=4,)
        btn.grid(row=4,column=1)
        btn = Button(keyFrame,text = "–",style = "BigTimesText.TButton",
                     command = lambda x="-":self.entryInsert(x),
                     width=4,)
        btn.grid(row=4,column=2)
        btn = Button(keyFrame,text = "Enter",style = "BigCalibriText.TButton",
                     command = self.submit,
                     width=5,)
        btn.grid(row=5,column=1)
        btn = Button(keyFrame,text = "Space",
                     command = lambda x=" ":self.entryInsert(x),
                     width=5,)
        btn.grid(row=3,column=0)
        btn = Button(keyFrame,text = "Delete",
                     command = self.entryDelete,
                     width=5,)
        btn.grid(row=3,column=2)

                
    #Button Control functions

    def toggleDenomination(self): 
        return {"LDS":"RLDS","RLDS":"LDS"}[self.denomination]

    def entryInsert(self,c):
        self.refEntry.insert(INSERT,c)
        self.refEntry.focus_set()
                    
    def entryDelete(self):
        s = self.inVar.get()
        n = self.refEntry.index(INSERT)
        if n>0:
            if not s[n-1].isalpha():
                s=s[:n-1]+s[n:]
            else:
                while n>0 and s[n-1].isalpha():
                    s=s[:n-1]+s[n:]
                    n -= 1
            self.inVar.set(s)
            self.refEntry.icursor(n)
            self.refEntry.focus_set()
        
                    
    def abbreviate(self,bookNum):
        den = self.denomination
        if den == "LDS":
            style = self.lbox.current()
        else:
            style = self.rbox.current()
        name = BOM.spell(bookNum,style)+" "
        self.refEntry.insert(INSERT,name)
        self.refEntry.focus_set()

    def submit(self,*args):  #sometimes an event is passed.
        try:
            ref = self.refEntry.get()
            den,s = extractDenomination(ref)
            if den:
                newSource = Reference(den)
            else:
                newSource = self.ref.copy()
                newSource.reset()
            self.denomination = newSource.denomination #***
            if s:
                newSource.insert(s)
            self.ref = newSource
            self.trans = newSource.translate()
            t = "({}) {}".format(self.trans.denomination,self.trans)
            self.outVar.set(t)
            self.alignDenomination(self.denomination)
        except ValueError:
            s = "One or more References is invalid.\nNo translation was made."
            messagebox.showerror("Error", s)
        
    def alignDenomination(self,den):
        den = den.upper()               #In case of hand entry
        if den not in ["LDS","RLDS"]:
            den = "RLDS"                #Default to RLDS
        if den != self.ref.denomination: #Switch ref/transRef
            t = self.ref
            self.ref = self.transRef
            self.transRef = t
            self.denomination = den
        #Now make the Style boxes line up
        if den == "RLDS":
            self.rstyleFrame.grid(row=0,column=0)
            self.lstyleFrame.grid(row=0,column=2)
        else:
            self.rstyleFrame.grid(row=0,column=2)
            self.lstyleFrame.grid(row=0,column=0)

    def switchIO(self):
        #Switch refEntry, refOut control variables 
        t=self.inVar.get()
        self.inVar.set(self.outVar.get())
        self.outVar.set(t)
        #Reset cursor positions
        self.refEntry.icursor(END)
        self.refOut.icursor(END)
        #Switch denomination
        self.denomination = self.toggleDenomination()
        self.alignDenomination(self.denomination)

    def applyStyle(self,*args):
        """Change book style in ref or trans"""
        changeDen = args[0]    #Updated Denomination
        style = {"LDS":self.lbox.current(),"RLDS":self.rbox.current()}[changeDen]
        if changeDen == self.ref.denomination:
            s = BOM.bookStr(self.inVar.get(),style)
            self.inVar.set(s)
        else:
            s = BOM.bookStr(self.outVar.get(),style)
            self.outVar.set(s)
        self.refEntry.focus_set()
        
        
            
def main():

    ReferenceApp()



if __name__ == "__main__":

    main()






        
        
