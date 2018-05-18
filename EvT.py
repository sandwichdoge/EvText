import Tkinter as tk
import tkFileDialog
import tkMessageBox
import SimplifiedCrypt
import ttk
import sys
from os import path


class APPLICATION(tk.Frame):
    def __init__(self, master=None, sTargetPath = ""):
        self.master=master
        self.master.title("EvText")
        self.frame = tk.Frame(self.master)
        self.sTargetPath = sTargetPath
        self.createwidgets()
        self.frame.pack(fill=tk.BOTH)
        self.sCurPwd = "__USE_PWD_PROMPT__"
        #if program starts with a target, will treat it as plain text file.
        if self.sTargetPath:
            self.sCurPwd = ""
        if self.sTargetPath : self._open(self.sTargetPath, "")
    def createwidgets(self):
        self.menubar = tk.Menu(self.master)
        self.master.config(menu=self.menubar)
        hFileMenu = tk.Menu(self.menubar, tearoff=0)
        hFileMenu.extrawidth = ' ' * 24
        hFileMenu.add_command(label="Open"+" "*(24-len("[Ctrl+O]"))+"[Ctrl+O]", command=self.callback_open)
        hFileMenu.add_command(label="Save"+" "*(24-len("[Ctrl+S]"))+" [Ctrl+S]", command=self.callback_save)
        hFileMenu.add_command(label="Save as..", command=self.callback_saveas)
        hFileMenu.add_separator()
        hFileMenu.add_command(label="Quit"+" "*(24-len("[Esc]"))+"[Esc]", command=self.callback_quit)
        self.menubar.add_cascade(label="File", menu=hFileMenu)
        hSettingsMenu = tk.Menu(self.menubar, tearoff=0)
        hSettingsMenu.add_command(label="Appearance", command=self.callback_appearance)
        hSettingsMenu.add_command(label="Set Current Password", command=self.callback_setdefaultpwd)
        self.menubar.add_cascade(label="Settings", menu=hSettingsMenu)
        self.editor = tk.Text()
        self.editor.pack(fill=tk.BOTH, expand=1)
        self.lStatus = tk.Label(self.master, text = "Status:OK", anchor = tk.W, bd = 1, relief = tk.SUNKEN)
        self.lStatus.place(relx = 0.001, rely = 1, anchor = tk.SW, relwidth = 0.998)
        self.contextmenu = tk.Menu(self.editor, tearoff=0)
        self.contextmenu.add_command(label="Copy"+" "*20, command=self.callback_copy)
        self.contextmenu.add_command(label="Cut", command=self.callback_cut)
        self.contextmenu.add_command(label="Paste", command=self.callback_paste)
        self.editor.bind("<Button-3>", self._popup)
        self.editor.bind("<Button-1>", self._popup_destroy)
        functionalkeys = ["<Control-s>","<Alt-F4>","<Control-a>","<Control-o>"]  #bind functional keys
        self.master.protocol("WM_DELETE_WINDOW", self.callback_quit)
        for i in range(len(functionalkeys)):
            self.master.bind(functionalkeys[i], self.key_input)
    def _popup(self, event):
        self.contextmenu.post(event.x_root, event.y_root)
    def _popup_destroy(self, event):
        self.contextmenu.unpost()
    def key_input(self, event):
        sKeyPressed=event.char
        #print "pressed", repr(sKeyPressed)
        if sKeyPressed == "\x13": self.callback_save()
        elif sKeyPressed == "\x1b": self.callback_quit()
        elif sKeyPressed == "\x01": self.callback_selectall()
        elif sKeyPressed == "\x0f": self.callback_open()
    def callback_copy(self):
        sSelectedText = self.editor.selection_get()
        self.master.clipboard_clear()
        self.master.clipboard_append(sSelectedText)
    def callback_cut(self):
        sSelectedText = self.editor.selection_get()
        self.master.clipboard_clear()
        self.master.clipboard_append(sSelectedText)
        self.editor.delete(tk.SEL_FIRST, tk.SEL_LAST)
    def callback_paste(self):
        sClipboard = self.master.clipboard_get()
        self.editor.insert(tk.CURRENT, sClipboard)
    def callback_setdefaultpwd(self):
        sOldPwd = self.sCurPwd
        sOldPwd = sOldPwd.replace("__USE_PWD_PROMPT__", "")
        self.sCurPwd = self.pwd_box(sOldPwd, "Set default password for encryption/decryption.")
        if self.sCurPwd == "__PWWINDOW_EXPLICITLY_CLOSED__" or self.sCurPwd == "(Current Password)":
            self.sCurPwd = sOldPwd
            return
    def callback_appearance(self):
        mwSettings.deiconify()
    def callback_quit(self):
        self.master.destroy()
        exit(0)
    def callback_save(self):  #save to current file with current password, ask for password if none exists
        sOldTargetPath = self.sTargetPath
        if not self.sTargetPath or self.sCurPwd == "__USE_PWD_PROMPT__":
            self.callback_saveas()
        else:
            sContent = self.editor.get(1.0, tk.END)
            self._save(str(sContent), self.sTargetPath, self.sCurPwd)
    def callback_saveas(self):
        sOldTargetPath = self.sTargetPath
        self.sTargetPath = tkFileDialog.asksaveasfilename(initialdir=path.dirname(sOldTargetPath), title="Save file to..")
        if not self.sTargetPath:
            self.sTargetPath = sOldTargetPath
            return
        self.sCurPwd = self.pwd_box("(Current Password)", "Enter encryption password.")
        if self.sCurPwd == "__PWWINDOW_EXPLICITLY_CLOSED__": return "err"
        sContent = self.editor.get(1.0, tk.END)
        self._save(str(sContent), self.sTargetPath, self.sCurPwd)
    def _save(self, sContent, sTargetPath, sPwd):
        if sContent[-1] == '\n':  #tk.insert() automatically adds newline so additional newline must be removed to prevent duplication
            sContent = sContent[:-1]
        if sPwd:
            try:
                sContentFinal = SimplifiedCrypt.crypt_aed_encrypt(sContent, sPwd)
            except:
                tkMessageBox.showinfo("EvText", "Error occurred\nUnable to encrypt data, please try saving without password.")
                return "err"
        else:  #no pwd provided = save as plain text, no encryption
            sContentFinal = sContent
        del sPwd
        try:
            with open(sTargetPath, "w") as fTargetW:
                fTargetW.write(sContentFinal)
                self.lStatus.config(text = "Saved")
        except IOError:
            tkMessageBox.showerror("EvText", "Unable to save to file!\nPermission denied.")
    def callback_open(self):
        self.sTargetPath = tkFileDialog.askopenfilename()
        if(not self.sTargetPath): return "err"
        self._open(self.sTargetPath, "__USE_PWD_PROMPT__")
    def _open(self, sTargetPath, sPwd = "__USE_PWD_PROMPT__"):
        if sPwd == "__USE_PWD_PROMPT__":
            sPwd = self.pwd_box()
            if sPwd == "__PWWINDOW_EXPLICITLY_CLOSED__": return
        try:
            with open(sTargetPath) as fTargetR:
                sContent = fTargetR.read()
        except IOError:
            tkMessageBox.showerror("EvText", "Unable to read from file!\nPermission denied.")
        if sPwd:
            try:sContentDecrypted = SimplifiedCrypt.crypt_aed_decrypt(sContent, sPwd)
            except ValueError:
                tkMessageBox.showinfo("EvText", "Wrong password!")
                return
        else: sContentDecrypted = sContent
        self.sCurPwd = sPwd
        del sPwd
        self.editor.delete(1.0, tk.END)
        self.editor.insert(1.0, sContentDecrypted)
        self.lStatus.config(text = sTargetPath)
    def pwd_box(self, sDefault="(Current Password)", sMsg = "Enter password for decryption. Leave blank for unencrypted files."):
        mwPWD = tk.Tk()
        mwPWD.geometry("500x120")
        GUIPWD = INPUTBOX(mwPWD, sMsg, True, sDefault)
        set_widget_theme(GUIPWD.frame, sTheme)
        set_widget_theme(GUIPWD.lb1, sTheme)
        set_widget_theme(GUIPWD.bOK, sTheme)
        sPw = GUIPWD.sReturnVal
        if sPw == "(Current Password)": sPw = self.sCurPwd
        return sPw
    def callback_selectall(self):
        self.editor.tag_add(tk.SEL, "1.0", tk.END)



def set_widget_theme(oTarget, sTheme):
    if sTheme == "Dark":
        sbgColor = "#3d3f42"
        sfgColor = "#ffffff"
        sbgActive = "#666666"
        sfgActive = sfgColor
    elif sTheme == "Light":
        sbgColor = "#ffffff"
        sfgColor = "#171819"
        sbgActive = "#9ca1a8"
        sfgActive = sfgColor
    try:
        oTarget.config(bg = sbgColor)
        if sfgColor:
            oTarget.config(fg=sfgColor)
        if sbgActive:
            oTarget.config(activebackground = sbgActive)
        if sfgActive:
            oTarget.config(activeforeground = sfgActive)
    except:
        return -1

def set_theme(sTheme):
    set_widget_theme(GUI.editor, sTheme)
    set_widget_theme(GUISETTINGS.master, sTheme)
    set_widget_theme(GUISETTINGS.bOK, sTheme)
    set_widget_theme(GUISETTINGS.lb1, sTheme)



class SETTINGS(tk.Frame):
    def __init__(self, master = None):
        self.master = master
        self.master.title("Settings")
        self.frame = tk.Frame(self.master)
        self.createwidgets()
        self.frame.pack()
        self.master.protocol("WM_DELETE_WINDOW", self.callback_quit)
    def createwidgets(self):
        self.lb1 = tk.Label(self.master, text = "Theme")
        self.lb1.place(relx = 0.04, rely = 0.04)
        self.comboTheme = ttk.Combobox(self.master)
        self.comboTheme["values"] = ("Light", "Dark")
        self.comboTheme.current(0)
        self.comboTheme.place(relx = 0.5, rely = 0.04, relwidth = 0.4)
        self.bOK = tk.Button(self.master, text = "Apply", command = self.callback_confirm)
        self.bOK.place(relx = 0.5, rely = 0.9, width = 80, anchor = tk.CENTER)
    def callback_confirm(self):
        self.sTheme = self.comboTheme.get()
        set_theme(self.sTheme)
        return
    def callback_quit(self):
        self.master.withdraw()



class INPUTBOX(tk.Frame):
    def __init__(self, master = None, sText = "Enter password for decryption.", bPwdWindow = False, sDefault = ""):
        self.sReturnVal = ""
        self.sDefault = sDefault
        self.master = master
        self.frame = tk.Frame(self.master)
        self.sText = sText
        self.createwidgets()
        self.frame.pack(fill=tk.BOTH, expand=1)
        self.master.attributes('-topmost', 1)
        self.master.protocol("WM_DELETE_WINDOW", self.gui_event_close)
        self.hPwdBox.focus_set()
        self.hPwdBox.select_range(0, tk.END)
        if bPwdWindow == True: self.hPwdBox.bind("<Key>", self.callback_keypressed)
        self.master.bind("<Return>", self.callback_confirmpwd)
        self.master.bind("<Escape>", self.callback_close)
        self.hPwdBox.wait_window(self.master)
    def createwidgets(self):
        self.lb1 = tk.Label(self.master, text=self.sText)
        self.lb1.place(relx=0.5, rely=0.15, anchor=tk.CENTER)
        self.hPwdBox = tk.Entry(self.master)
        self.hPwdBox.place(relx=0.04, rely=0.3, width=460)
        self.bOK = tk.Button(self.master, text="OK")
        self.bOK.place(relx=0.5, rely=0.74, width=140, anchor=tk.CENTER)
        self.bOK.config(command=self.confirmpwd)
        self.hPwdBox.insert(0, self.sDefault)
    def callback_keypressed(self, event):
        self.hPwdBox.config(show="*")
        self.hPwdBox.unbind("<Key>")
    def confirmpwd(self):
        self.sReturnVal = self.hPwdBox.get()
        self.master.destroy()
    def callback_confirmpwd(self, event):
        self.confirmpwd()
    def callback_close(self, event):
        self.gui_event_close()
    def gui_event_close(self):
        self.sReturnVal = "__PWWINDOW_EXPLICITLY_CLOSED__"
        self.master.destroy()




global sTheme
sTheme = "Dark"

fp = ""
for i in range(1, len(sys.argv)):
    if path.isfile(sys.argv[i]):
        fp = sys.argv[i]


mw = tk.Tk()
mw.geometry("600x400")
GUI = APPLICATION(mw, fp)

mwSettings = tk.Tk()
mwSettings.geometry("300x300")
GUISETTINGS = SETTINGS(mwSettings)
mwSettings.withdraw()

set_theme(sTheme)

mw.mainloop()
