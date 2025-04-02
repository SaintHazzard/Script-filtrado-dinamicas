from tkinter import Tk
from tkinter.filedialog import askopenfilenames, askopenfilename

def seleccionar_archivos():
    """Selecciona múltiples archivos."""
    Tk().withdraw()
    archivos = askopenfilenames(
        title="Selecciona los archivos",
        filetypes=[("Excel y CSV", "*.xlsx *.xls *.csv")],
        initialdir="data"
    )
    return archivos


def seleccionar_archivo():
    """Selecciona un único archivo."""
    Tk().withdraw()
    archivo = askopenfilename(
        title="Selecciona un archivo",
        filetypes=[("Excel y CSV", "*.xlsx *.xls *.csv")],
        initialdir="data"
    )
    return archivo
