# import pygame
# from pygame.locals import *

# pygame.init()

# white = (255, 255, 255)
# red = (255, 0, 0)
# green = (0, 255, 0)
# blue = (0, 0, 255)
# (width, height) = (300, 200)
# screen = pygame.display.set_mode((width, height))
# pygame.display.set_caption('Tutorial 1')
# pygame.display.flip()


# RUNNING = True


# while RUNNING:
#     for event in pygame.event.get():
#         print(event)
#         if event.type == pygame.QUIT:
#             pygame.quit()
#             quit()
            
#     screen.fill(white)
#     large_text = pygame.font.Font('freesansbold.ttf',115)

#     pygame.draw.rect(screen, green,(150,450,100,50))
#     pygame.draw.rect(screen, red,(550,450,100,50))


#     pygame.display.updates

# import tkinter as tk
    

# def write_slogan():
#     print("Tkinter is easy to use!")

# root = tk.Tk()
# frame = tk.Frame(root)
# frame.pack()

# button = tk.Button(frame, 
#                    text="QUIT", 
#                    fg="red",
#                    command=quit)
# button.pack(side=tk.LEFT)
# slogan = tk.Button(frame,
#                    text="Hello",
#                    command=write_slogan)
# slogan.pack(side=tk.LEFT)
# T = tk.Text(root, height=2, width=30)
# T.pack()
# T.insert(tk.END, "Just a text Widget\nin two lines\n")
# tk.mainloop()

# root.mainloop()

import tkinter as tk

fields = 'Side', 'Ticker', 'Level', 'PT'

def fetch(entries):
    for entry in entries:
        field = entry[0]
        text  = entry[1].get()
        print('%s: "%s"' % (field, text)) 

def makeform(root, fields):
    entries = []
    for field in fields:
        row = tk.Frame(root)
        lab = tk.Label(row, width=5, text=field, anchor='w')
        ent = tk.Entry(row)
        row.pack(side=tk.LEFT, fill=tk.X, padx=1, pady=5)
        lab.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        entries.append((field, ent))
    return entries

def add_watch(entries):
    for entry in entries:
        field = entry[0]
        text  = entry[1]
        print('%s: "%s"' % (field, text.get())) 
        text.delete(0, tk.END)

if __name__ == '__main__':

    root = tk.Tk()
    ents = makeform(root, fields)
    root.bind('<Return>', (lambda event, e=ents: fetch(e)))   
    b1 = tk.Button(root, text='Add',
                  command=(lambda e=ents: add_watch(e)))
    b1.pack(side=tk.BOTTOM, padx=5, pady=5)
    b2 = tk.Button(root, text='Quit', command=root.quit)
    b2.pack(side=tk.BOTTOM, padx=5, pady=5)
    root.mainloop()