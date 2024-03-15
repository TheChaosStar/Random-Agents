import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfile
from PIL import Image, ImageTk
from os import path
import random, os, json

COLOR = {
    "Primary": "#007acc",
    "Secondary": "#1e1e1e",
    "Tertiary": "#3e3e42",
    "Success": "#007e33",
    "Info": "#9933cc",
    "Warning": "#ff8800",
    "Danger": "#cc0000"
}

RES_FOLDER = path.abspath(path.join(path.dirname(__file__), 'res'))

NAMES = [
    "Astra", "Breach", "Brimstone", "Chamber", "Cypher", "Deadlock", "Fade", "Gekko", 
    "Harbor", "Iso", "Jett", "KAYO", "Killjoy", "Neon", "Omen", "Phoenix", 
    "Raze", "Reyna", "Sage", "Skye", "Sova", "Viper", "Yoru",
]

class IOFile:
    def Read(path:str, isJson:bool = False) -> list[str] | dict | None:
        """
        Read on file with path and return data.\n
        If wanna this function return json format, passed 'isJson' on 'true'.\n
        If Error this function return 'None'.
        """

        result = None
        try:
            with open(path, "r") as f:
                if isJson: result = json.load(f)
                else: result = [line.rstrip('\n') for line in f]
        except:
            print("[Error] Can't Read File: " + path)

        return result
    
    def Write(path:str, data:str) -> bool:
        """ 
        Write data on file with path.\n
        If OK this function return 'true' else 'false'.
        """
        try:
            with open(path, "w") as f:
                f.write(data)
        except:
            print("[Error] Can't Write File: " + path)
            return False

        return True

class Character:
    def __init__(self, name) -> None:
        self.name = name
        self.active = False
        
        img = Image.open(RES_FOLDER + "/icons/" + str(name) + "_icon.webp")
        self.img = img.resize((50, 50))
    
    def setColorActive(self):
        if self.active:
            self.style.configure(self.name + '.TCheckbutton', background=COLOR["Primary"])
            self.style.configure(self.name + '.TCheckbutton', focuscolor=COLOR["Primary"])
            self.style.configure(self.name + '.TCheckbutton', activebackground=COLOR["Primary"])
        else: 
            self.style.configure(self.name + '.TCheckbutton', background=COLOR["Tertiary"])
            self.style.configure(self.name + '.TCheckbutton', focuscolor=COLOR["Tertiary"])
            self.style.configure(self.name + '.TCheckbutton', activebackground=COLOR["Tertiary"])

    def checkbutton_clicked(self):
        self.active = not self.active
        self.setColorActive()
        
    def GetFrame(self, master) -> ttk.Frame:
        frame = ttk.Frame(master)

        self.style = ttk.Style(frame)
        self.style.theme_use('default')
        self.style.configure("TLabel", background=COLOR["Secondary"], foreground="white")
        self.style.configure("TFrame", background=COLOR["Secondary"])

        self.setColorActive()

        phImg = ImageTk.PhotoImage(self.img)
        self.style.layout(self.name + '.TCheckbutton', [('Checkbutton.padding', {'sticky': 'nswe','children': [('Checkbutton.focus', {'side': 'left', 'sticky': 'w','children': [('Checkbutton.label', {'sticky': 'nswe'})]})]})])

        checkBtn = ttk.Checkbutton(frame, image=phImg, style=self.name + '.TCheckbutton', variable=tk.Variable(None, value=self.active), command=lambda: self.checkbutton_clicked())
        checkBtn.image = phImg
        checkBtn.state(['selected'])
        checkBtn.pack(pady=5)

        lName = ttk.Label(frame, text=self.name)
        lName.pack(pady=5)

        return frame

class PresetManager():
    objs: list[dict]
    preset_path: str
    chars: list[Character]
    filetype: list[tuple]

    def __init__(self, chars:list[Character]):
        self.preset_path = RES_FOLDER + "/presets.json"
        self.chars = chars
        self.filetype = [("Custom Type", ".agents")]

        _objs = IOFile.Read(self.preset_path, True)
        if _objs == None:
            print("[Info] Create presets file...")
            IOFile.Write(self.preset_path, json.dumps([]))
            _objs = IOFile.Read(self.preset_path, True)

        self.objs = _objs

    def addPreset(self, master):
        path = askopenfilename(title="Choose the file to open", filetypes=self.filetype, defaultextension=self.filetype)
        if path == "": 
            print("[Error] Path not found")
            return
        name = (path.split("/")[-1]).split(".")[0]
        _obj = { "name": name, "path": path }

        for obj in self.objs:
            if name == obj["name"]: 
                print("[Error] This Preset exist: " + name)
                return

        self.objs.append(_obj)

        IOFile.Write(self.preset_path, json.dumps(self.objs))
            
        self.loadPreset(_obj["name"])
        self.InitMenu(master)

    def getDataPreset(self, name:str) -> list[str] | None:
        for obj in self.objs:
            if name == obj["name"]:
                data = IOFile.Read(obj["path"])
                return data
        
        print("[Error] Preset not found: " + name)
        return None

    def InitMenu(self, master:tk.Tk):
        menu = tk.Menu(master, tearoff=0)

        presetMenu = tk.Menu(menu, tearoff=0)
        nbChild = 0
        for obj in self.objs:
            presetMenu.add_command(label=obj["name"], command= lambda name = obj["name"]: self.loadPreset(name))
            nbChild += 1
        

        otherMenu = tk.Menu(menu, tearoff=0)
        if nbChild != 0: otherMenu.add_cascade(label="Load", underline=0, menu=presetMenu)
        otherMenu.add_command(label="Open...", command=lambda: self.addPreset(master))
        otherMenu.add_command(label="Save as", command=self.savePreset)

        menu.add_cascade(label="Presets", underline=0, menu=otherMenu)

        master.config(menu=menu)

    def loadPreset(self, name:str):
        data = self.getDataPreset(name)
        if data == None:
            print("[Error] Can't Read Data from Preset")
            return

        for char in self.chars:
            if char.name in data:
                if not char.active: char.checkbutton_clicked()
            elif char.active: char.checkbutton_clicked()
    
    def savePreset(self):
        file = asksaveasfile(filetypes=self.filetype, defaultextension=self.filetype)
        [file.write(str(char.name + '\n')) for char in self.chars if char.active]
        file.close()

class App(tk.Tk):
    def __init__(self, title:str, width:int, height:int):
        super().__init__()

        self.title(title)
        self.resizable(False, False)
        self.geometry("{}x{}+{}+{}".format(width, height, *self.GetCenterPos((width, height))))
        self.config(background=COLOR["Secondary"])
        self.iconbitmap(RES_FOLDER + '/icon.ico')

    def GetCenterPos(self, size:tuple) -> tuple[int, int]:
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = size[0]
        window_height = size[1]
        x, y = int((screen_width/2) - (window_width/2)), int((screen_height/2) - (window_height/2))
        return (x, y)

    def Create_menu_bar(self, chars: list[Character]):
        presetManager = PresetManager(chars)
        presetManager.InitMenu(self)
   
class ShowAgent(tk.Toplevel):
    def __init__(self, parent:tk.Tk, agent:Character):
        super().__init__(parent)

        self.overrideredirect(1)
        self.config(borderwidth=1, relief="solid")

        px, py = parent.winfo_x(), parent.winfo_y()
        pwidth, pheight = parent.winfo_width(), parent.winfo_height()
        cwidth, cheight = 150, 100

        self.geometry('%dx%d+%d+%d' % (cwidth, cheight, px + (pwidth / 2 - cwidth / 2), py + (pheight / 2 - cheight / 2)))

        self.title("Agent")
        self.resizable(False, False)
        self.config(background=COLOR["Secondary"])

        phI = ImageTk.PhotoImage(agent.img)
        imageAgent = tk.Label(self, image=phI, bg=COLOR["Secondary"])
        imageAgent.image = phI
        imageAgent.pack(pady=5)

        tk.Label(self, text="L'agent est : " + str(agent.name), bg=COLOR["Secondary"], fg="white").pack(pady=5, padx=10)

# Main -------------------------
def getRandom(master:tk.Tk, list:list[Character]):
    temp = [char for char in list if char.active]
    if (temp.__len__() == 0): 
        messagebox.showinfo("Error", "Selection au moins un agent")
        return
    
    w = ShowAgent(master, random.choice(temp))
    w.focus()
    w.grab_set()
    w.after(1500,lambda:w.destroy())

def DrawCharacters(app, chars:list[Character], ItemInRow = 8) -> None:
    width=70
    height=100
    x, y = 0, 0
    for char in chars:
        if x >= ItemInRow:
            y += 1
            x = 0

        char.GetFrame(app).place(x=x*width, y=y*height, width=70, height=100)
        x += 1

chars = [Character(name) for name in NAMES]

app = App("Random Agents", 560, 350)

# Init style
style = ttk.Style(app)
style.theme_use('default')
style.map("Success.TButton", background=[ 
    ('!active',COLOR["Primary"]),
    ('pressed',COLOR["Primary"]),
    ('active', COLOR["Primary"])
    ]
)

DrawCharacters(app, chars)

app.Create_menu_bar(chars)

btn = ttk.Button(app, text="Start", style="Success.TButton", command=lambda: getRandom(app, chars))
btn.pack(side=tk.BOTTOM, pady=10)

app.mainloop()
