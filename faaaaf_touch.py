#!/usr/bin/python2
# -*- coding: utf-8 -*-

'''
adapted from pimenu (https://github.com/splitbrain/pimenu/)
this code is written for the visual art installation faigh ar ais as an fharraige, by Irish
visual artist Shane Finan. It controls a touchscreen that starts/stops video playback via subprocess
on a second monitor. The touchscreen is linked to a Raspberry Pi 3 Model B+
'''
import Tkconstants as TkC
import os
import subprocess
from subprocess import PIPE, Popen
import sys
from Tkinter import Tk, Frame, Button, Label, PhotoImage
from math import sqrt, floor, ceil
#import omxcontrol
import paramiko
from paramiko import SSHClient

import yaml

ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.connect(hostname="192.168.8.105", username="pi", password="faaaaf")

class FlatButton(Button):
    def __init__(self, master=None, cnf=None, **kw):
        Button.__init__(self, master, cnf, **kw)

        self.config(
            compound=TkC.TOP,
            relief=TkC.FLAT,
            bd=0,
            bg="#b91d47",  # dark-red
            fg="white",
            activebackground="#b91d47",  # dark-red
            activeforeground="white",
            highlightthickness=0
        )

    def set_color(self, color):
        self.configure(
            bg=color,
            fg="black",
            activebackground=color,
            activeforeground="white"
        )


class faaaaf_item(Frame):
    framestack = []
    icons = {}
    path = ''
    lastinit = 0

    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")
        self.parent = parent
        self.pack(fill=TkC.BOTH, expand=1)

        self.path = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.initialize()

    def initialize(self):
        """
        (re)load the the items from the yaml configuration and (re)init
        the whole menu system

        :return: None
        """
        with open(self.path + '/pimenu.yaml', 'r') as f:
            doc = yaml.load(f)
        self.lastinit = os.path.getmtime(self.path + '/pimenu.yaml')

        if len(self.framestack):
            self.destroy_all()
            self.destroy_top()
        
        self.show_items(doc)

    def has_config_changed(self):
        """
        Checks if the configuration has been changed since last loading

        :return: Boolean
        """
        return self.lastinit != os.path.getmtime(self.path + '/pimenu.yaml')

    def show_items(self, items, upper=None):
        """
        Creates a new page on the stack, automatically adds a back button when there are
        pages on the stack already

        :param items: list the items to display
        :param upper: list previous levels' ids
        :return: None
        """
        if upper is None:
            upper = []
        num = 0
        
        # create a new frame
        wrap = Frame(self, bg="black")

        if len(self.framestack):
            # when there were previous frames, hide the top one and add a back button for the new one
            self.hide_top()
            back = FlatButton(
                wrap,
                text="back",
                image=self.get_icon("arrow.left"),
                command=self.go_back,
            )
            back.set_color("#9CEEAC")  # green
            back.grid(row=0, column=0, padx=1, pady=1, sticky=TkC.W + TkC.E + TkC.N + TkC.S)
            num += 1
        
        # add the new frame to the stack and display it
        self.framestack.append(wrap)
        self.show_top()

        # calculate tile distribution
        allitems = len(items) + num
        rows = floor(sqrt(allitems))
        cols = ceil(allitems / rows)

        # make cells autoscale
        for x in range(int(cols)):
            wrap.columnconfigure(x, weight=1)
        for y in range(int(rows)):
            wrap.rowconfigure(y, weight=1)

        # display all given buttons
        for item in items:
            act = upper + [item['name']]

            if 'icon' in item:
                image = self.get_icon(item['icon'])
            else:
                image = self.get_icon('scrabble.' + item['label'][0:1].lower())

            btn = FlatButton(
                wrap,
                text=item['label'],
                image=image
            )

            if 'items' in item:
                # this is a deeper level
                btn.configure(command=lambda act=act, item=item: self.show_items(item['items'], act),
                              text=item['label'])
                btn.set_color("#2b5797")  # dark-blue
            else:
                # this is an action
                btn.configure(command=lambda act=act: self.go_action(act), )

            if 'color' in item:
                btn.set_color(item['color'])
                
            if 'name' in item:
                current_film = item['name']

            # add buton to the grid
            btn.grid(
                row=int(floor(num / cols)),
                column=int(num % cols),
                padx=1,
                pady=1,
                sticky=TkC.W + TkC.E + TkC.N + TkC.S
            )
            num += 1
        
        #play the films if necessary
        play_films(num, current_film)

    def get_icon(self, name):
        """
        Loads the given icon and keeps a reference

        :param name: string
        :return:
        """
        if name in self.icons:
            return self.icons[name]

        ico = self.path + '/ico/' + name + '.gif'
        if not os.path.isfile(ico):
            ico = self.path + '/faaaaf_icons/' + name + '.png'
            if not os.path.isfile(ico):
                ico = self.path + '/faaaaf_icons/faaaaf_screens/faaaaf_img_' + name + '.png'
                if not os.path.isfile(ico):
                    ico = self.path + '/faaaaf_icons/arrow.gif'

        self.icons[name] = PhotoImage(file=ico)
        return self.icons[name]

    def hide_top(self):
        """
        hide the top page
        :return:
        """
        self.framestack[len(self.framestack) - 1].pack_forget()

    def show_top(self):
        """
        show the top page
        :return:
        """
        (stdin, stdout, stderr) = ssh.exec_command("killall omxplayer.bin")
        #os.system("killall omxplayer.bin")
        self.framestack[len(self.framestack) - 1].pack(fill=TkC.BOTH, expand=1)

    def destroy_top(self):
        """
        destroy the top page
        :return:
        """
        self.framestack[len(self.framestack) - 1].destroy()
        self.framestack.pop()

    def destroy_all(self):
        """
        destroy all pages except the first aka. go back to start
        :return:
        """
        while len(self.framestack) > 1:
            self.destroy_top()

    def go_action(self, actions):
        """
        execute the actionsudo apt-get install -y libdbus-1{,-dev} script
        :param actions:
        :return:
        """
        

    def go_back(self):
        """
        destroy the current frame and reshow the one below, except when the config has changed
        then reinitialize everything
        :return:
        """
        if self.has_config_changed():
            self.initialize()
        else:
            self.destroy_top()
            self.show_top()

def play_films(stack_level, curr_film):
    args = "omxplayer -o local --win \"200 200 400 400\" --no-osd"
    omx_arguments = "omxplayer --loop -o local --no-osd "
    faaaaf_film_path = "Desktop/faaaaf/faaaaf_" + curr_film + ".mp4"
    if (stack_level > 0):
        #playing = subprocess.Popen(['omxplayer','-o','local','--win','200,200,400,400','--no-osd',faaaaf_film_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True,bufsize=0)
        (stdin, stdout, stderr) = ssh.exec_command(omx_arguments+faaaaf_film_path)

def main():
    root = Tk()
    root.geometry("800x480")
    root.wm_title('faigh ar ais as an fharraige')
    if len(sys.argv) > 1 and sys.argv[1] == 'fs':
        root.wm_attributes('-fullscreen', True)
    faaaaf_item(root)
    root.config(cursor='none')
    root.mainloop()


if __name__ == '__main__':
    main()
