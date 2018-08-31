#!/usr/bin/python
import matplotlib as mpl
mpl.use("TkAgg")
mpl.rcParams['axes.formatter.useoffset'] = False

from matplotlib import style
style.use('ggplot')
# import Tkinter for Python 2.x
import Tkinter as tk
# import ttk for Python 2.x
import ttk
#from tkinter import ttk
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.ticker import FormatStrFormatter
import numpy as np
import glob
import subprocess
import sys
from os import path
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import warnings


class App(tk.Frame):

    def __init__(self, datadir, candsdir, master=None):

        self.colors = ['firebrick', 'grey', 'darkgreen', 'yellow', 'navy', 'indigo', 'sienna', 'lime', 'red', 'black', 'magenta', 'olive']
        self.markers = ['o', '^', 's']

        self.realtime = 262144.0 * 54e-06
        self.dmmin = 0.0
        self.dmmax = 2000.0

        self.startcand = [-1.0, -1.0]
        self.endcand = [-1.0, -1.0]

        self.pstartcand = [-1.0, -1.0]
        self.pendcand = [-1.0, -1.0]

        self.datadir = datadir
        self.candsdir = candsdir
        tk.Frame.__init__(self, master)
        self.pack(fill=tk.BOTH, expand=1)
        self.createWidgets()
        self.drawWarnings()
        self.drawLag()
        self.drawErr()
        self.drawHeimdall()
        self.drawCands()
        #self.drawNet()

    def createWidgets(self):
        top=self.winfo_toplevel()
        top.resizable(False, False)

        self.nb = ttk.Notebook(self)
        self.nb.place(x=0, y=0, height=900, width=1600)

        self.proc = ttk.Frame(self.nb)
        self.nb.add(self.proc, text='Processing')

        self.cands = ttk.Frame(self.nb)
        self.nb.add(self.cands, text='Candidates')

        self.quitButton = tk.Button(self, text='Quit', fg='red', command=self.quit)
        self.quitButton.place(x=10, y=25, height=20, width=100)

        self.candbeams = 18

        self.cvars = []
        self.cbuttons = []

        for candbeam in np.arange(self.candbeams):

            self.cvars.append(tk.IntVar())
            self.cbuttons.append(tk.Checkbutton(self.cands, text="Beam " + str(candbeam), variable=self.cvars[candbeam]))
            self.cbuttons[candbeam].place(x=1400, y=25 + candbeam * 20)

        self.clearBeams = tk.Button(self.cands, text='Clear All', fg='darkorange', command=self.clearBeams)
        self.clearBeams.place(x=1400, y = 50 + self.candbeams * 20, width = 100)

    def drawWarnings(self):
        self.figwarn, self.axwarn1 = plt.subplots(figsize=(5, 5), dpi=100)
        self.axwarn2 = self.axwarn1.twinx()
        plt.subplots_adjust(left=0.075, bottom=0.075, right=0.975, top=0.90, wspace=0, hspace=0)
        self.fgawarn = FigureCanvasTkAgg(self.figwarn, self.proc)
        self.warnanim = animation.FuncAnimation(self.figwarn, self.animateWarn, interval=10000)
        self.fgawarn.show()
        self.fgawarn.get_tk_widget().place(x=10, y = 35, width = 780, height = 400)

    def drawLag(self):
        self.figlag = plt.figure(figsize=(5,5), dpi=100)
        self.axlag = self.figlag.gca()
        plt.subplots_adjust(left=0.075, bottom=0.075, right=0.975, top=0.90, wspace=0, hspace=0)
        self.fgalag = FigureCanvasTkAgg(self.figlag, self.proc)
        self.laganim = animation.FuncAnimation(self.figlag, self.animateLag, interval = 10000)
        self.fgalag.show()
        self.fgalag.get_tk_widget().place(x=810, y = 35, width = 780, height = 400)

    def drawErr(self):
        self.figerr, self.axerr1 = plt.subplots(figsize=(5,5), dpi=100)
        self.axerr2 = self.axerr1.twinx()
        plt.subplots_adjust(left=0.075, bottom=0.075, right=0.925, top=0.90, wspace=0, hspace=0)
        self.fgaerr = FigureCanvasTkAgg(self.figerr, self.proc)
        self.erranim = animation.FuncAnimation(self.figerr, self.animateErr, interval=10000)
        self.fgaerr.show()
        self.fgaerr.get_tk_widget().place(x=10, y=460, width = 780, height=400)

    def drawHeimdall(self):
        self.figheim = plt.figure(figsize=(10, 5), dpi=100)
        self.axheim = self.figheim.gca()
        plt.subplots_adjust(left=0.075, bottom=0.075, right=0.975, top=0.90, wspace=0, hspace=0)
        self.fgaheim = FigureCanvasTkAgg(self.figheim, self.proc)
        self.heimanim = animation.FuncAnimation(self.figheim, self.animateHeim, interval=10000)
        self.fgaheim.show()
        self.fgaheim.get_tk_widget().place(x=810, y=460, width = 780, height=400)

    def drawCands(self):
        self.figcands = plt.figure(figsize=(15,10), dpi=150)
        self.axcand = self.figcands.gca()
        plt.subplots_adjust(left=0.075, bottom=0.075, right=0.975, top=0.95, wspace=0, hspace=0)
        self.fgacands = FigureCanvasTkAgg(self.figcands, self.cands)
        self.candsanim = animation.FuncAnimation(self.figcands, self.animateCands, interval=5000)
        self.fgacands.show()
        self.fgacands.get_tk_widget().place(x=10, y=35, width = 1200, height=800)
        self.fgacands.get_tk_widget().bind('<Button-1>', self.getCandCoords)
        self.fgacands.get_tk_widget().bind('<Button-3>', self.cancelCandCoords)

    def getCandCoords(self, event):
        if (self.startcand[0] == -1):
            self.startcand[0] = event.x
            self.startcand[1] = event.y
        else:
            self.endcand[0] = event.x
            self.endcand[1] = event.y

    def cancelCandCoords(self, even):
        print "Resetting the selected coordinates"
        
        # Shouldn't reset to default, but to the last used
        self.startcand[0] = -1
        self.startcand[1] = -1
        self.endcand[0] = -1
        self.endcand[1] = -1

    def animateWarn(self, i):     
        logfiles = sorted(glob.glob(path.join(datadir, 'pafinder*.log')))
        xList = []
        yList = []
        xLabels = []
        activeList = []
        nodes = 0
        numnodes = len(logfiles)
        for logfile in logfiles:
            nodename = logfile[-7:-4]
            xLabels.append(nodename)
            warnings = subprocess.check_output('grep WARNING ' + logfile + ' | wc -l', shell=True)
            #changed = subprocess.check_output('find -samefile ' + logfile + ' -mmin 0.5', shell=True)
            #if (changed == ''):
            activeList.append(0.75)
            #else:
            #    activeList.append(-1)
            xList.append(len(yList))
            yList.append(int(warnings))
            nodes = nodes + 1

        self.axwarn1.clear()
        self.axwarn1.set_title('Number of warnings and pipeline status', fontsize=10)
        #self.axwarn2.clear()
        #self.axwarn2.patch.set_visible(False)
        self.axwarn1.bar(xList, yList, 0.90, align = 'center', color='orangered')
        self.axwarn1.set_xlim([-1, numnodes])
        self.axwarn1.set_xticks(xList)
        self.axwarn1.set_xticklabels(xLabels)
        #self.axwarn2.set_ylim([0, 1])
        #self.axwarn2.set_yticklabels([])
        self.axwarn1.grid(False)
        self.axwarn2.grid(False)
        self.axwarn2.set_yticklabels([])
        #self.axwarn2.plot(activeList, marker='x', linestyle='', color='red', markersize=10, markeredgewidth=5)
 
    def animateLag(self, i):
        logfiles = sorted(glob.glob(path.join(datadir, 'pafinder*.log')))
        xList = []
        yList = []
        xLabels = []
        numnodes = len(logfiles)
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
        self.axlag.set_title('Average queue lags', fontsize=10)
        self.axlag.bar(xList, yList, 0.90, align = 'center', color='orangered')
        self.axlag.set_xlim([-1, numnodes])
        self.axlag.set_xticks(xList)
        self.axlag.set_xticklabels(xLabels)

    def animateErr(self, i):
        logfiles = sorted(glob.glob(path.join(datadir, 'pafinder*.log')))
        self.axerr1.set_title('Errors', fontsize=10)

        xList = []
        xLabels = []
        noerrorsList = []
        timeList = []
        numnodes = len(logfiles)
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
        self.axerr1.set_title('Errors and average time between buffer saves', fontsize=10)
        self.axerr1.tick_params('y', colors='dodgerblue')
        self.axerr1.bar(xList, noerrorsList, 0.90, align='center', color='red')
        self.axerr2.clear()
        self.axerr2.patch.set_visible(False)
        self.axerr2.plot(xList, timeList, marker='.', color='black')
        self.axerr1.grid(False)
        self.axerr2.grid(False)
        self.axerr2.tick_params('y', colors='black')
        self.axerr2.set_ylabel('Time [s]', fontsize=8, weight='bold')
        self.axerr1.set_xlim([-1, numnodes])
        self.axerr1.set_xticks(xList)
        self.axerr1.set_xticklabels(xLabels)
        self.axerr2.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        self.axerr2.set_ylim([0, max(timeList) + 1])

    def animateHeim(self, i):
        logfiles = sorted(glob.glob(path.join(datadir, 'heimdall*.log')))

        xList = []
        xLabels = []
        timeList = []
        colors = []
        numnodes = len(logfiles)
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
        self.axheim.bar(xList, timeList, 0.90, align='center', color=colors)
        self.axheim.set_xlim([-1, numnodes])
        self.axheim.set_xticks(xList)
        self.axheim.set_xticklabels(xLabels)
        self.axheim.axhline(14.1, linestyle='--', color='red')

    def animateCands(self, i):
        self.axcand.clear()

        active = []

        for ibeam in np.arange(self.candbeams):

            if self.cvars[ibeam].get():
                active.append(ibeam)

        #self.cbuttons[0].config(state='disabled')
        self.axcand.set_title('Candidates', fontsize=10)
        self.axcand.set_xlabel('Time [s]', fontsize=8)
        self.axcand.set_ylabel('DM + 1', fontsize=8)
        self.axcand.tick_params(axis='both', which='major', labelsize=8)

        for iabeam, abeam in enumerate(active):
            abeamstr = str(abeam + 1).zfill(2)
            acands = sorted(glob.glob(path.join(candsdir, '*' + abeamstr + '.cand')))


            times = []
            dms = []
            snrs = []

            for acand in acands:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    canddata = np.loadtxt(acand).reshape(-1, 9)
                
                if len(canddata) > 0:
                
                    snrs.extend(canddata[:, 0])
                    times.extend(canddata[:, 2])
                    dms.extend(canddata[:, 5])

            for idm, dm in enumerate(dms):
                dms[idm] = dm + 1.0

            self.axcand.scatter(times, dms, 10.0, facecolor='none', edgecolor=self.colors[abeam % 12], marker=self.markers[int(abeam / 12)], linewidth=0.5)

        self.axcand.set_yscale('log')
        print "Current limits", self.axcand.get_ylim(), self.axcand.get_xlim()
        self.axcand.grid(False)

        if ((self.startcand[0] == -1) and (self.endcand[0] == -1)):
            self.axcand.set_ylim([self.dmmin+1, self.dmmax+1])
        else:

            top = 0
            bottom = 0
            left = 0
            right = 0

            if (self.startcand[1] < self.endcand[1]):
                top = self.startcand[1]
                bottom = self.endcand[1]
            else:
                top = self.endcand[1]
                bottom = self.startcand[1]

            if (self.startcand[0] < self.endcand[0]):
                left = self.startcand[0]
                right = self.endcand[0]
            else:
                left = self.endcand[0]
                right = self.startcand[0]

            xstep = (self.axcand.get_xlim()[1] - self.axcand.get_xlim()[0]) / 1080.0
            ystep = (self.axcand.get_ylim()[1] - self.axcand.get_ylim()[0]) / 700.0

            #print xstep, ystep

            xlow = (left - 90) * xstep
            xhigh = (right - 90) * xstep
            ylow = (700 - bottom) * ystep
            yhigh = (700 - top) * ystep
            self.axcand.set_ylim([ylow, yhigh])
            self.axcand.set_xlim([xlow, xhigh]) 

    def clearBeams(self):
        for button in self.cvars:
            button.set(0)
        
if __name__ == "__main__":

    datadir = sys.argv[1]
    candsdir = sys.argv[2]

    #root = tk()
    #root.geometry("1600x900")
    #app = App(root)
    app = App(datadir, candsdir)
    app.master.title('PAFINDER monitor')
    app.master.geometry('1600x900')
    app.mainloop()
