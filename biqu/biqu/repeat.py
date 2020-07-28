from multiprocessing import  Process
import os

TIMEOUT=600

def task():
    os.system('cd biqu && scrapy crawl update')

if  __name__=="__main__":
    index=0
    while True:
        p = Process(target=task)
        p.start()
        p.join(TIMEOUT)
        if p.is_alive():
            p.terminate()
        print ('========= At [%d] times  ===========\n'%(index))
        index+=1
