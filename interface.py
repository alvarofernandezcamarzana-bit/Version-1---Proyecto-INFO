"""Simple Tkinter interface for version 1 of ProjectoAeropuerto."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from airport import (
    Airport,
    AddAirport,
    LoadAirports,
    MapAirports,
    PlotAirports,
    PrintAirport,
    RemoveAirport,
    SaveSchengenAirports,
    SetSchengen,
)


class AirportApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Gestor de Aeropuertos - Versión 1")
        self.master.geometry("960x520")
        self.airports = []

        self.code_var = tk.StringVar()
        self.lat_var = tk.StringVar()
        self.lon_var = tk.StringVar()
        self.autoschengen_var = tk.BooleanVar(value=True)

        self._build_widgets()

    def _apply_schengen_flags(self) -> None:
        for airport in self.airports:
            SetSchengen(airport)

    # UI helpers ---------------------------------------------------------
    def _build_widgets(self):
        container = ttk.Frame(self.master, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        controls = ttk.Frame(container, padding=(0, 0, 12, 0))
        controls.pack(side=tk.LEFT, fill=tk.Y)

        display = ttk.Frame(container)
        display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(display, text="Aeropuertos (tabla)").pack(anchor=tk.W)
        columns = ("code", "lat", "lon", "sch")
        self.tree = ttk.Treeview(
            display,
            columns=columns,
            show="headings",
            height=15,
        )
        headings = {
            "code": ("ICAO", 80),
            "lat": ("Latitud", 120),
            "lon": ("Longitud", 120),
            "sch": ("Schengen", 100),
        }
        for column_id in columns:
            text, width = headings[column_id]
            self.tree.heading(column_id, text=text)
            self.tree.column(column_id, width=width, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", lambda _event: self.show_selected())

        ttk.Label(display, text="Bitácora").pack(anchor=tk.W, pady=(8, 0))
        self.details = tk.Text(display, height=8)
        self.details.pack(fill=tk.BOTH, expand=True)

        # Form panel
        form = ttk.LabelFrame(controls, text="Nuevo aeropuerto")
        form.pack(fill=tk.X, pady=10)
        ttk.Label(form, text="ICAO").grid(row=0, column=0, sticky=tk.W, padx=4, pady=4)
        ttk.Entry(form, textvariable=self.code_var, width=8).grid(row=0, column=1, sticky=tk.W)
        ttk.Label(form, text="Latitud").grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        ttk.Entry(form, textvariable=self.lat_var, width=10).grid(row=1, column=1, sticky=tk.W)
        ttk.Label(form, text="Longitud").grid(row=2, column=0, sticky=tk.W, padx=4, pady=4)
        ttk.Entry(form, textvariable=self.lon_var, width=10).grid(row=2, column=1, sticky=tk.W)
        ttk.Checkbutton(
            form,
            text="Asignar Schengen automáticamente",
            variable=self.autoschengen_var,
        ).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=4, pady=2)
        ttk.Button(form, text="Añadir", command=self.add_airport).grid(row=4, column=0, columnspan=2, pady=6)

        # Buttons panel
        buttons = ttk.Frame(controls)
        buttons.pack(fill=tk.X)
        ttk.Button(buttons, text="Cargar fichero", command=self.load_file).grid(row=0, column=0, padx=4, pady=4, sticky=tk.EW)
        ttk.Button(buttons, text="Eliminar seleccionado", command=self.remove_selected).grid(row=0, column=1, padx=4, pady=4, sticky=tk.EW)
        ttk.Button(buttons, text="Detectar Schengen", command=self.detect_schengen).grid(row=1, column=0, padx=4, pady=4, sticky=tk.EW)
        ttk.Button(buttons, text="Guardar Schengen", command=self.save_schengen).grid(row=1, column=1, padx=4, pady=4, sticky=tk.EW)
        ttk.Button(buttons, text="Mostrar lista", command=self.show_all).grid(row=2, column=0, padx=4, pady=4, sticky=tk.EW)
        ttk.Button(buttons, text="Gráfico", command=self.plot_airports).grid(row=2, column=1, padx=4, pady=4, sticky=tk.EW)
        ttk.Button(buttons, text="Mapa", command=self.map_airports).grid(row=3, column=0, padx=4, pady=4, sticky=tk.EW)
        ttk.Button(buttons, text="Refrescar", command=self.refresh_list).grid(row=3, column=1, padx=4, pady=4, sticky=tk.EW)

        for i in range(2):
            buttons.columnconfigure(i, weight=1)

    # Core actions --------------------------------------------------------
    def refresh_list(self):
        self._apply_schengen_flags()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for index, airport in enumerate(self.airports):
            self.tree.insert(
                "",
                tk.END,
                iid=str(index),
                values=(
                    airport.code,
                    f"{airport.latitude:.4f}",
                    f"{airport.longitude:.4f}",
                    "Schengen" if airport.schengen else "No Schengen",
                ),
            )

    def load_file(self):
        filename = filedialog.askopenfilename(
            title="Selecciona fichero de aeropuertos",
            filetypes=[("Text files", "*.txt"), ("Todos", "*.*")],
        )
        if not filename:
            return
        self.airports = LoadAirports(filename)
        self.details.delete("1.0", tk.END)
        self.details.insert(tk.END, f"Cargados {len(self.airports)} aeropuertos\n")
        self.refresh_list()

    def _selected_airport(self):
        selection = self.tree.selection()
        if not selection:
            return None
        iid = selection[0]
        index = int(iid)
        if index < 0 or index >= len(self.airports):
            return None
        return self.airports[index]

    def show_selected(self):
        airport = self._selected_airport()
        if not airport:
            return
        self.details.delete("1.0", tk.END)
        PrintAirport(airport)
        self.details.insert(
            tk.END,
            f"Código: {airport.code}\nLat: {airport.latitude:.5f}\nLon: {airport.longitude:.5f}\nSchengen: {'Sí' if airport.schengen else 'No'}\n",
        )

    def show_all(self):
        self._apply_schengen_flags()
        self.details.delete("1.0", tk.END)
        for airport in self.airports:
            self.details.insert(
                tk.END,
                f"{airport.code} -> Lat {airport.latitude:.4f}, Lon {airport.longitude:.4f}, Schengen={'Sí' if airport.schengen else 'No'}\n",
            )

    def add_airport(self):
        code = self.code_var.get().strip()
        try:
            latitude = float(self.lat_var.get())
            longitude = float(self.lon_var.get())
        except ValueError:
            messagebox.showerror("Error", "Latitud y longitud deben ser números")
            return
        if not code:
            messagebox.showerror("Error", "El código ICAO no puede estar vacío")
            return
        airport = Airport(code, latitude, longitude)
        if self.autoschengen_var.get():
            SetSchengen(airport)
        if not AddAirport(self.airports, airport):
            messagebox.showwarning("Aviso", "Ese aeropuerto ya existe")
            return
        self.refresh_list()
        self.code_var.set("")
        self.lat_var.set("")
        self.lon_var.set("")

    def remove_selected(self):
        airport = self._selected_airport()
        if not airport:
            messagebox.showinfo("Info", "Selecciona un aeropuerto")
            return
        RemoveAirport(self.airports, airport.code)
        self.refresh_list()
        self.details.delete("1.0", tk.END)

    def detect_schengen(self):
        airport = self._selected_airport()
        if airport:
            SetSchengen(airport)
        else:
            self._apply_schengen_flags()
        self.refresh_list()

    def save_schengen(self):
        if not self.airports:
            messagebox.showinfo("Info", "No hay aeropuertos para guardar")
            return
        filename = filedialog.asksaveasfilename(
            title="Guardar sólo aeropuertos Schengen",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
        )
        if not filename:
            return
        self._apply_schengen_flags()
        saved = SaveSchengenAirports(self.airports, filename)
        if saved < 0:
            messagebox.showwarning("Aviso", "No hay aeropuertos Schengen que guardar")
        else:
            messagebox.showinfo("Listo", f"Se guardaron {saved} aeropuertos")

    def plot_airports(self):
        if not self.airports:
            messagebox.showinfo("Info", "Carga aeropuertos primero")
            return
        self._apply_schengen_flags()
        PlotAirports(self.airports)

    def map_airports(self):
        if not self.airports:
            messagebox.showinfo("Info", "Carga aeropuertos primero")
            return
        self._apply_schengen_flags()
        MapAirports(self.airports)


def main():
    root = tk.Tk()
    app = AirportApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
