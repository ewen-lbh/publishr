import os


def ask(msg, choices=None, default=None, askfunc=input):
    msg = '[QUESTION] '+msg
    if default:
        # add quotes around values with spaces
        q = '"' if ' ' in default else ''

        msg += f'={q}{default}{q}'
    msg += ': '
    if choices is None:
        return askfunc(msg) or default
    elif choices == 'yn':
        ans = askfunc(msg).lower().strip() or default
        return ans.startswith('y')
    elif type(choices) is list or type(choices) is tuple or type(choices) is set:
        ans = None
        while ans not in choices:
            ans = askfunc(msg).strip()
            if ans == '': ans = default
    else:
        ans = None or default
        while ans is not choices:
            ans = askfunc(msg).lower().strip()


def text(msg, **kw):
    return ask(msg, **kw, askfunc=text_editor)

def text_editor(msg):
    import tkinter

    def save(textarea, root):
        t = textarea.get('1.0', 'end-1c')
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp', 'description.txt'), 'w') as f:
            f.write(t)
        root.destroy()

    root = tkinter.Tk()

    textarea = tkinter.Text(root)
    textarea.grid()
    button = tkinter.Button(root, text="Save", command=lambda: save(textarea, root))
    button.grid()

    root.mainloop()

    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp', 'description.txt'), 'r') as f:
        ret = f.read()

    os.remove(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp', 'description.txt'))

    return ret



