#!/usr/bin/python
import matplotlib as mpl
mpl.use("TkAgg")
mpl.rcParams['axes.formatter.useoffset'] = False

from matplotlib import style
style.use('ggplot')
import Tkinter as tk
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import glob
import subprocess
import sys
from os import path
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class App(tk.Frame):

    def __init__(self, datadir, master=None):

        self.realtime = 262144.0 * 54e-06
        print(self.realtime)

        self.datadir = datadir
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=1)
        self.createWidgets()
        #self.drawFigure()
        #self.drawAnimated()
        self.drawWarnings()
        self.drawLag()
        self.drawErr()
        self.drawHeimdall()
        #self.drawNet()

    def clearFigures(self):
        self.axanim.clear()

        self.axnet.clear()
        self.fganet.show()


    def createWidgets(self):
        top=self.winfo_toplevel()
        top.resizable(False, False)

        self.resetButton = tk.Button(self, text='Reset', fg = 'black', command=self.clearFigures)
        self.resetButton.place(x=5, y=5, height=25, width=100)
        #self.resetButton.grid(column=0, row=0)

        self.quitButton = tk.Button(self, text='Quit', fg='red', command=self.quit)
        self.quitButton.place(x=110, y=5, height=25, width=100)

        #self.quitButton.grid(column=1, row=0)

        #self.netPlot = tk.Canvas(self, width=300, height=200, bg='red')
        #self.netPlot.grid(column=0, row= 1)


    def drawFigure(self):
        fignet = plt.figure(figsize=(5,5), dpi=100)

        self.axnet.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])
        self.axnet.set_title('Network performance')
        self.fganet = FigureCanvasTkAgg(fignet, self)
        self.fganet.show()
        self.fganet.get_tk_widget().place(x=10, y=50, width=700, height=400)

        figerror = plt.figure(figsize=(5,5), dpi=100)
        axerror = figerror.gca()
        axerror.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5], color='red')
        axerror.set_title('Errors and warnings')
        fgaerror = FigureCanvasTkAgg(figerror, self)
        fgaerror.show()
        fgaerror.get_tk_widget().place(x=10, y=460, width=700, height=400)

    def drawWarnings(self):
        self.figwarn, self.axwarn1 = plt.subplots(figsize=(5, 5), dpi=100)
        self.axwarn2 = self.axwarn1.twinx()
        plt.subplots_adjust(left=0.075, bottom=0.075, right=0.975, top=0.90, wspace=0, hspace=0)
        self.fgawarn = FigureCanvasTkAgg(self.figwarn, self)
        self.warnanim = animation.FuncAnimation(self.figwarn, self.animateWarn, interval=10000)
        self.fgawarn.show()
        self.fgawarn.get_tk_widget().place(x=10, y = 50, width = 780, height = 400)

    def drawLag(self):
        self.figlag = plt.figure(figsize=(5,5), dpi=100)
        self.axlag = self.figlag.gca()
        plt.subplots_adjust(left=0.075, bottom=0.075, right=0.975, top=0.95, wspace=0, hspace=0)
        self.fgalag = FigureCanvasTkAgg(self.figlag, self)
        self.laganim = animation.FuncAnimation(self.figlag, self.animateLag, interval = 5000)
        self.fgalag.show()
        self.fgalag.get_tk_widget().place(x=810, y = 50, width = 780, height = 400)


    def drawNet(self):
        self.fignet = plt.figure(figsize=(10, 5), dpi=100)
        self.axnet = self.fignet.gca()
        plt.subplots_adjust(left=0.025, bottom=0.075, right=0.975, top=0.95, wspace=0, hspace=0)
        self.fganet = FigureCanvasTkAgg(self.fignet, self)
        self.netanim = animation.FuncAnimation(self.fignet, self.animateNet, interval=1000)
        self.fganet.show()
        self.fganet.get_tk_widget().place(x=10, y=460, width = 1580, height=400)

    def drawErr(self):
        self.figerr, self.axerr1 = plt.subplots(figsize=(5,5), dpi=100)
        self.axerr2 = self.axerr1.twinx()
        plt.subplots_adjust(left=0.075, bottom=0.075, right=0.925, top=0.95, wspace=0, hspace=0)
        self.fgaerr = FigureCanvasTkAgg(self.figerr, self)
        self.erranim = animation.FuncAnimation(self.figerr, self.animateErr, interval=10000)
        self.fgaerr.show()
        self.fgaerr.get_tk_widget().place(x=10, y=460, width = 780, height=400)

    def drawHeimdall(self):
        self.figheim = plt.figure(figsize=(10, 5), dpi=100)
        self.axheim = self.figheim.gca()
        plt.subplots_adjust(left=0.075, bottom=0.075, right=0.975, top=0.95, wspace=0, hspace=0)
        self.fgaheim = FigureCanvasTkAgg(self.figheim, self)
        self.heimanim = animation.FuncAnimation(self.figheim, self.animateHeim, interval=10000)
        self.fgaheim.show()
        self.fgaheim.get_tk_widget().place(x=810, y=460, width = 780, height=400)

    def drawAnimated(self):
        self.figanim = plt.figure(figsize=(5,5), dpi=100)
        self.axanim = self.figanim.gca()

        fgaanim = FigureCanvasTkAgg(self.figanim, self)
        ani = animation.FuncAnimation(self.figanim, self.animate, interval=5000)
        fgaanim.show()
        fgaanim.get_tk_widget().place(x=800, y=50, width=700, height=400)

    # TODO: Plot only last n points
    # TODO: Reading whole file will get expensive after long observation
    # TODO: Call tail or something like that on the files
    def animate(self, i):
        pullData = open("sampleText.txt","r").read()
        dataList = pullData.split('\n')
        xList = []
        yList = []
        # Plot only 10 values
        for eachLine in dataList:
            if len(eachLine) > 1:
                x, y = eachLine.split(',')
                xList.append(int(x))
                yList.append(int(y))

        self.axanim.clear()
        self.axanim.plot(xList, yList)


    def animateNet(self, i):
        pullData = open(path.join(self.datadir, "sampleText.txt"),"r").read()
        dataList = pullData.split('\n')
        xList = []
        yList = []
        # Plot only 10 values
        for eachLine in dataList:
            if len(eachLine) > 1:
                x, y = eachLine.split(',')
                xList.append(int(x))
                yList.append(int(y))

        self.axnet.clear()
        self.axnet.plot(xList, yList)
        self.axnet.set_title('Network performance', fontsize=10)

    def animateWarn(self, i):
        logfiles = sorted(glob.glob(path.join(datadir, 'pafinder*.log')))
        xList = []
        yList = []
        xLabels = []
        activeList = []
        activeColors = []
        nodes = 0
        for logfile in logfiles:
            nodename = logfile[-7:-4]
            xLabels.append(nodename)
            warnings = subprocess.check_output('grep WARNING ' + logfile + ' | wc -l', shell=True)
            changed = subprocess.check_output('find -samefile ' + logfile + ' -mmin 0.5', shell=True)
            if (changed == ''):
                activeList.append(0.75)
            else:
                activeList.append(-1)
            xList.append(len(yList))
            yList.append(warnings)
            nodes = nodes + 1

        self.axwarn1.clear()
        self.axwarn2.clear()
        self.axwarn1.bar(xList, yList, 1, align = 'center')
        self.axwarn1.set_xlim([-1, 17])
        self.axwarn1.set_xticks(xList)
        self.axwarn1.set_xticklabels(xLabels)
        self.axwarn2.set_ylim([0, 1])
        self.axwarn2.set_yticklabels([])
        self.axwarn2.grid(False)
        self.axwarn2.plot(activeList, marker='x', linestyle='', color='red', markersize=10, markeredgewidth=5)

        #self.axwarn.set_xlabel(xLabels)
        
    def animateLag(self, i):
        logfiles = sorted(glob.glob(path.join(datadir, 'pafinder*.log')))
        xList = []
        yList = []
        xLabels = []
        for logfile in logfiles:
            nodename = logfile[-7:-4]
            xLabels.append(nodename)
            total = subprocess.check_output('grep "WARNING: GPU" ' + logfile + ' | tail -n 10 | grep -o -E "[0-9]+" | paste -sd+ | bc', shell=True)
            numwarnings = int(subprocess.check_output('grep "WARNING: GPU" ' + logfile + ' | tail -n 10 | wc -l', shell=True))
            xList.append(len(yList))
            if total == '':
                yList.append(0.0)
            else:
                yList.append(float(int(total)) / float(numwarnings))

        self.axlag.clear()
        self.axlag.set_title('Average pipeline lags', fontsize=10)
        self.axlag.bar(xList, yList, 1, align = 'center')
        self.axlag.set_xlim([-1, 17])
        self.axlag.set_xticks(xList)
        self.axlag.set_xticklabels(xLabels)

    def animateErr(self, i):
        logfiles = sorted(glob.glob(path.join(datadir, 'pafinder*.log')))
        self.axerr1.set_title('Errors', fontsize=10)

        xList = []
        xLabels = []
        noerrorsList = []
        timeList = []

        for logfile in logfiles:
            xList.append(len(noerrorsList))
            nodename = logfile[-7:-4]
            xLabels.append(nodename)
            noerrors = int(subprocess.check_output('grep "ERROR" ' + logfile + ' | wc -l', shell=True))
            noerrorsList.append(noerrors)
            # CREDIT: https://unix.stackexchange.com/questions/290974/extracting-positive-negative-floating-point-numbers-from-a-string
            numtime = int(subprocess.check_output('grep "Previous buffer sent" ' + logfile + ' | tail -n 10 | wc -l', shell=True))
            if (numtime == 0):
                timeList.append(0.0)
            else:
                sumtime = float(subprocess.check_output('grep "Previous buffer sent" ' + logfile + ' | tail -n 10 | grep -Eo "[+-]?[0-9]+([.][0-9]+)?" | paste -sd+ | bc', shell=True))
                timeList.append(sumtime / float(numtime))            

        self.axerr1.clear()
        self.axerr2.clear()
        self.axerr2.patch.set_visible(False)
        self.axerr1.set_title('Errors', fontsize=10)
        self.axerr2.plot(xList, timeList, color='firebrick')
        self.axerr2.tick_params('y', colors='firebrick')
        self.axerr1.tick_params('y', colors='dodgerblue')
        self.axerr1.bar(xList, noerrorsList, 1, align='center', color='dodgerblue')
        self.axerr1.set_xlim([-1, 17])
        self.axerr1.set_xticks(xList)
        
        self.axerr1.set_xticklabels(xLabels)

    def animateHeim(self, i):
        logfiles = sorted(glob.glob(path.join(datadir, 'heimdall*.log')))

        xList = []
        xLabels = []
        timeList = []
        colors = []

        for logfile in logfiles:
            xList.append(len(timeList))
            nodename = logfile[-7:-4]
            # CREDIT: https://unix.stackexchange.com/questions/290974/extracting-positive-negative-floating-point-numbers-from-a-string
            numtime = int(subprocess.check_output('grep "Total time" ' + logfile + ' | tail -n 10 | wc -l', shell=True))
            if (numtime == 0):
                timeList.append(0.0)
            else:
                sumtime = float(subprocess.check_output('grep "Total time" ' + logfile + ' | tail -n 10 | grep -Eo "[+-]?[0-9]+([.][0-9]+)?" | paste -sd+ | bc', shell=True))
                timeList.append(sumtime / float(numtime))
            print(timeList[-1])

            if (timeList[-1] <= self.realtime):
                colors.append('forestgreen')
            elif ((timeList[-1] > self.realtime) & (timeList[-1] <= 1.1 * self.realtime)):
                colors.append('gold')
            elif ((timeList[-1] > 1.1 * self.realtime) & (timeList[-1] <= 1.25 * self.realtime)):
                colors.append('darkorange')
            elif (timeList[-1] > 1.25 * self.realtime):
                colors.append('darkred')

            xLabels.append(nodename)

        self.axheim.clear()
        self.axheim.set_title('Average Heimdall processing time', fontsize=10)
        self.axheim.bar(xList, timeList, 1, align='center', color=colors)
        self.axheim.set_xlim([-1, 17])
        self.axheim.set_xticks(xList)
        self.axheim.set_xticklabels(xLabels)

#        frame = Frame(master,width=1600,height=900)
#        frame.pack()

#        self.leave = Button(frame, text = "Quit", fg="red", command=frame.quit)
#        self.leave.pack(side=RIGHT)

#        self.hello = Button(frame, text="Hello", command=self.say_hi)
#        self.hello.pack(side=LEFT)

        #Label(master, text="First").grid(row=0)
        #Label(master, text="Second").grid(row=1)



    def say_hi(self):
        print("Hello peoplez")

if __name__ == "__main__":

    datadir = sys.argv[1]

    #root = tk()
    #root.geometry("1600x900")
    #app = App(root)
    app = App(datadir)
    app.master.title('PAFINDER monitor')
    app.master.geometry('1600x900')
    app.mainloop()
