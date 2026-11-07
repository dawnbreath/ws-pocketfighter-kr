"""Copy save files of the previous ROM build to the new ROM name (.sav/.sn1 and other slots)."""
import sys, os, shutil, glob
def handoff(prev_rom, new_rom, exts=('.sav','.sn1')):
    pb=os.path.splitext(prev_rom)[0]; nb=os.path.splitext(new_rom)[0]; done=[]
    for e in exts:
        if os.path.exists(pb+e): shutil.copy2(pb+e, nb+e); done.append(nb+e)
    return done
if __name__=='__main__': print(handoff(sys.argv[1],sys.argv[2]))
