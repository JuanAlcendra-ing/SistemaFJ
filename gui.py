"""Interfaz gráfica (Tkinter) de Software FJ. Ejecutar: python gui.py"""
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from excepciones import DatosInvalidosError, SoftwareFJError
from gestor import SistemaGestion
from logger_config import RUTA_LOG, log
from reserva import Estado
from servicios import AlquilerEquipo, Asesoria, ReservaSala

COLOR = "#1f4e79"


def a_numero(texto, tipo, campo):
    """Convierte texto a número si falla lanza una excepción personalizada."""
    try:
        return tipo(str(texto).strip().replace(",", "."))
    except ValueError as err:
        raise DatosInvalidosError(f"El campo '{campo}' debe ser numérico: {texto!r}") from err


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Software FJ – Gestión de Clientes, Servicios y Reservas")
        self.geometry("980x640")
        self.minsize(900, 600)
        self._sin_popups = False   
        self.sistema = SistemaGestion(notificar=self.mostrar_mensaje)

        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 14, "bold"), foreground=COLOR)
        estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        estilo.configure("TButton", padding=5)

        ttk.Label(self, text="Software FJ", style="Titulo.TLabel").pack(anchor="w", padx=12, pady=(10, 0))
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=8)

        self._tab_clientes()
        self._tab_servicios()
        self._tab_reservas()
        self._tab_registro()

        self.estado = tk.StringVar(value="Listo.")
        ttk.Label(self, textvariable=self.estado, relief="sunken", anchor="w").pack(fill="x", side="bottom")
        log.info("Interfaz gráfica iniciada")
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

   
    def mostrar_mensaje(self, exito, mensaje):
        """Callback del gestor: actualiza barra de estado, panel de registro y popup."""
        hora = datetime.now().strftime("%H:%M:%S")
        self.estado.set(("✓ " if exito else "✗ ") + mensaje)
        self.txt.configure(state="normal")
        self.txt.insert("end", f"[{hora}] {'OK ' if exito else 'ERR'} {mensaje}\n",
                        "ok" if exito else "err")
        self.txt.see("end")
        self.txt.configure(state="disabled")
        if not exito and not self._sin_popups:
            messagebox.showerror("Operación no realizada", mensaje, parent=self)

    def _ejecutar(self, descripcion, funcion):
        """Para pasos de la GUI (conversión de datos) que pueden fallar antes del gestor."""
        try:
            return funcion()
        except SoftwareFJError as err:
            self.sistema.registrar_error(descripcion, err)
        except Exception as err:
            self.sistema.registrar_error(descripcion, err)
        return None

    def _tabla(self, padre, columnas, anchos):
        marco = ttk.Frame(padre)
        tabla = ttk.Treeview(marco, columns=columnas, show="headings", height=9)
        for c, a in zip(columnas, anchos):
            tabla.heading(c, text=c)
            tabla.column(c, width=a, anchor="w")
        sb = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=sb.set)
        tabla.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        marco.pack(fill="both", expand=True, padx=8, pady=8)
        return tabla

    def _campo(self, padre, etiqueta, fila, col=0, ancho=24):
        ttk.Label(padre, text=etiqueta).grid(row=fila, column=col, sticky="e", padx=4, pady=3)
        var = tk.StringVar()
        ttk.Entry(padre, textvariable=var, width=ancho).grid(row=fila, column=col + 1, sticky="w", padx=4, pady=3)
        return var

    def _cerrar(self):
        log.info("Interfaz gráfica cerrada")
        self.destroy()

   
    def _tab_clientes(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="  Clientes  ")
        form = ttk.LabelFrame(tab, text="Nuevo cliente")
        form.pack(fill="x", padx=8, pady=8)
        self.c_nombre = self._campo(form, "Nombre:", 0)
        self.c_email = self._campo(form, "Email:", 0, 2)
        self.c_tel = self._campo(form, "Teléfono:", 1)
        self.c_doc = self._campo(form, "Documento:", 1, 2)
        ttk.Button(form, text="Registrar cliente", command=self.registrar_cliente).grid(
            row=2, column=0, columnspan=4, pady=6)
        self.t_clientes = self._tabla(tab, ("ID", "Nombre", "Email", "Teléfono"), (50, 250, 300, 150))

    def registrar_cliente(self):
      
        v = lambda var: var.get().strip() or None
        self.sistema.registrar_cliente(nombre=v(self.c_nombre), email=v(self.c_email),
                                       telefono=v(self.c_tel), documento=v(self.c_doc))
        self.refrescar()

    def _tab_servicios(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="  Servicios  ")
        form = ttk.LabelFrame(tab, text="Nuevo servicio")
        form.pack(fill="x", padx=8, pady=8)
        ttk.Label(form, text="Tipo:").grid(row=0, column=0, sticky="e", padx=4, pady=3)
        self.s_tipo = tk.StringVar(value="Sala")
        cb = ttk.Combobox(form, textvariable=self.s_tipo, state="readonly", width=22,
                          values=("Sala", "Equipo", "Asesoría"))
        cb.grid(row=0, column=1, sticky="w", padx=4)
        cb.bind("<<ComboboxSelected>>", lambda e: self._etiquetas_servicio())
        self.s_nombre = self._campo(form, "Nombre:", 0, 2)
        self.s_tarifa = self._campo(form, "Tarifa ($):", 1)
        self.l_extra1 = ttk.Label(form)
        self.l_extra1.grid(row=1, column=2, sticky="e", padx=4)
        self.s_extra1 = tk.StringVar()
        ttk.Entry(form, textvariable=self.s_extra1, width=24).grid(row=1, column=3, sticky="w", padx=4)
        self.l_extra2 = ttk.Label(form)
        self.l_extra2.grid(row=2, column=0, sticky="e", padx=4)
        self.s_extra2 = tk.StringVar()
        self.e_extra2 = ttk.Combobox(form, textvariable=self.s_extra2, width=22,
                                     values=("junior", "senior", "experto"))
        self.e_extra2.grid(row=2, column=1, sticky="w", padx=4)
        botones = ttk.Frame(form)
        botones.grid(row=3, column=0, columnspan=4, pady=6)
        ttk.Button(botones, text="Crear servicio", command=self.crear_servicio).pack(side="left", padx=4)
        ttk.Button(botones, text="Activar / desactivar seleccionado",
                   command=self.alternar_disponibilidad).pack(side="left", padx=4)
        self._etiquetas_servicio()
        self.t_servicios = self._tabla(tab, ("ID", "Tipo", "Nombre", "Tarifa", "Disponible", "Detalle"),
                                       (40, 110, 160, 90, 80, 380))

    def _etiquetas_servicio(self):
        tipo = self.s_tipo.get()
        textos = {"Sala": ("Capacidad:", ""), "Equipo": ("Depósito ($):", ""),
                  "Asesoría": ("Especialidad:", "Nivel:")}[tipo]
        self.l_extra1.configure(text=textos[0])
        self.l_extra2.configure(text=textos[1])
        self.e_extra2.configure(state="normal" if tipo == "Asesoría" else "disabled")
        self.s_extra1.set("")
        self.s_extra2.set("junior" if tipo == "Asesoría" else "")

    def crear_servicio(self):
        tipo = self.s_tipo.get()
        nombre = self.s_nombre.get()

        def construir():
            tarifa = a_numero(self.s_tarifa.get(), float, "Tarifa")
            if tipo == "Sala":
                return ReservaSala, (nombre, tarifa, a_numero(self.s_extra1.get(), int, "Capacidad"))
            if tipo == "Equipo":
                dep = self.s_extra1.get().strip() or "0"
                return AlquilerEquipo, (nombre, tarifa, a_numero(dep, float, "Depósito"))
            return Asesoria, (nombre, tarifa, self.s_extra1.get(), self.s_extra2.get())

        datos = self._ejecutar(f"Preparar servicio {tipo}", construir)
        if datos:
            self.sistema.agregar_servicio(datos[0], *datos[1])
        self.refrescar()

    def alternar_disponibilidad(self):
        sel = self.t_servicios.selection()
        if not sel:
            return messagebox.showinfo("Servicios", "Seleccione un servicio de la tabla.")
        sid = int(self.t_servicios.item(sel[0])["values"][0])
        for s in self.sistema.servicios:
            if s.id == sid:
                s.disponible = not s.disponible
                self.mostrar_mensaje(True, f"{s.nombre}: ahora {'disponible' if s.disponible else 'NO disponible'}")
                log.info("Disponibilidad de servicio #%s cambiada a %s", s.id, s.disponible)
        self.refrescar()

   
    def _tab_reservas(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="  Reservas  ")
        form = ttk.LabelFrame(tab, text="Nueva reserva")
        form.pack(fill="x", padx=8, pady=8)
        ttk.Label(form, text="Cliente:").grid(row=0, column=0, sticky="e", padx=4, pady=3)
        self.r_cliente = ttk.Combobox(form, state="readonly", width=34)
        self.r_cliente.grid(row=0, column=1, sticky="w", padx=4)
        ttk.Label(form, text="Servicio:").grid(row=0, column=2, sticky="e", padx=4)
        self.r_servicio = ttk.Combobox(form, state="readonly", width=34)
        self.r_servicio.grid(row=0, column=3, sticky="w", padx=4)
        self.r_duracion = self._campo(form, "Duración (h/días):", 1, ancho=10)
        ttk.Button(form, text="Crear y confirmar reserva", command=self.crear_reserva).grid(
            row=1, column=2, columnspan=2, pady=4)

        proc = ttk.LabelFrame(tab, text="Procesar / cancelar la reserva seleccionada")
        proc.pack(fill="x", padx=8, pady=4)
        self.r_imp = self._campo(proc, "Impuesto (%):", 0, ancho=8)
        self.r_imp.set("19")
        self.r_desc = self._campo(proc, "Descuento (%):", 0, 2, ancho=8)
        self.r_desc.set("0")
        ttk.Button(proc, text="Procesar", command=self.procesar_reserva).grid(row=0, column=4, padx=6)
        ttk.Button(proc, text="Cancelar reserva", command=self.cancelar_reserva).grid(row=0, column=5, padx=6)
        self.t_reservas = self._tabla(tab, ("ID", "Cliente", "Servicio", "Duración", "Estado", "Costo"),
                                      (40, 200, 220, 80, 100, 130))

    def _reserva_seleccionada(self):
        sel = self.t_reservas.selection()
        if not sel:
            messagebox.showinfo("Reservas", "Seleccione una reserva de la tabla.")
            return None
        rid = int(self.t_reservas.item(sel[0])["values"][0])
        return next((r for r in self.sistema.reservas if r.id == rid), None)

    def crear_reserva(self):
        ic, is_ = self.r_cliente.current(), self.r_servicio.current()
        cliente = self.sistema.clientes[ic] if ic >= 0 else None
        servicio = self.sistema.servicios[is_] if is_ >= 0 else None
        dur = self._ejecutar("Leer duración", lambda: a_numero(self.r_duracion.get(), int, "Duración"))
        if dur is None and self.r_duracion.get().strip():
            return          # error de conversión ya notificado
        self.sistema.crear_reserva(cliente, servicio, dur)   # None -> ParametroFaltanteError
        self.refrescar()

    def procesar_reserva(self):
        reserva = self._reserva_seleccionada()
        if not reserva:
            return
        datos = self._ejecutar("Leer impuesto/descuento", lambda: (
            a_numero(self.r_imp.get(), float, "Impuesto") / 100,
            a_numero(self.r_desc.get(), float, "Descuento") / 100))
        if datos:
            self.sistema.procesar_reserva(reserva, impuesto=datos[0], descuento=datos[1])
        self.refrescar()

    def cancelar_reserva(self):
        reserva = self._reserva_seleccionada()
        if reserva:
            self.sistema.cancelar_reserva(reserva)
        self.refrescar()

   
    def _tab_registro(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="  Registro de eventos  ")
        ttk.Label(tab, text=f"Todo error y evento queda guardado en: {RUTA_LOG}").pack(anchor="w", padx=8, pady=6)
        marco = ttk.Frame(tab)
        marco.pack(fill="both", expand=True, padx=8, pady=4)
        self.txt = tk.Text(marco, state="disabled", wrap="word", font=("Consolas", 10))
        self.txt.tag_configure("ok", foreground="#1b7f3b")
        self.txt.tag_configure("err", foreground="#b3261e")
        sb = ttk.Scrollbar(marco, command=self.txt.yview)
        self.txt.configure(yscrollcommand=sb.set)
        self.txt.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        ttk.Button(tab, text="Ejecutar simulación de operaciones válidas e inválidas",
                   command=self.simular).pack(pady=8)

    def simular(self):
        """Carga datos de ejemplo mezclando casos válidos e inválidos."""
        s = self.sistema
        self._sin_popups = True
        ana = s.registrar_cliente(nombre="Ana Gómez", email="ana@correo.com",
                                  telefono="3001234567", documento="1020304050")
        s.registrar_cliente(nombre="Pedro Ruiz", email="pedro#correo", telefono="3001112222", documento="99887766")
        luis = s.registrar_cliente(nombre="Luis Pérez", email="luis@correo.com",
                                   telefono="+573105556677", documento="80123456")
        sala = s.agregar_servicio(ReservaSala, "Sala Innovación", 50000, 12)
        s.agregar_servicio(ReservaSala, "Sala Fantasma", 40000, -5)
        equipo = s.agregar_servicio(AlquilerEquipo, "Portátil Pro", 30000, deposito=100000)
        ase = s.agregar_servicio(Asesoria, "Asesoría Cloud", 80000, "Cloud", "senior")
        if ana and sala:
            r1 = s.crear_reserva(ana, sala, 5)
            if r1:
                s.procesar_reserva(r1)
                s.cancelar_reserva(r1)
        if luis and sala:
            s.crear_reserva(luis, sala, 20)
        if luis and ase:
            r2 = s.crear_reserva(luis, ase, 2)
            if r2:
                s.procesar_reserva(r2, descuento=0.8)
                s.procesar_reserva(r2, impuesto=0.0, descuento=0.10)
        if ana and equipo:
            s.crear_reserva(ana, equipo, 4)
        self._sin_popups = False
        self.refrescar()
        messagebox.showinfo("Simulación", "Simulación terminada. Revise la pestaña de registro y el archivo de logs.")


    def refrescar(self):
        for t in (self.t_clientes, self.t_servicios, self.t_reservas):
            t.delete(*t.get_children())
        for c in self.sistema.clientes:
            self.t_clientes.insert("", "end", values=(c.id, c.nombre, c.email, c.telefono))
        for s in self.sistema.servicios:
            self.t_servicios.insert("", "end", values=(
                s.id, type(s).__name__, s.nombre, f"${s.tarifa_base:,.0f}",
                "Sí" if s.disponible else "No", s.describir().split(" - ", 1)[-1]))
        for r in self.sistema.reservas:
            c, sv = r._cliente, r._servicio
            self.t_reservas.insert("", "end", values=(
                r.id, c.nombre, sv.nombre, r._duracion, r.estado.value,
                f"${r.costo:,.2f}" if r.costo is not None else "—"))
        self.r_cliente["values"] = [f"{c.nombre} ({c.documento})" for c in self.sistema.clientes]
        self.r_servicio["values"] = [f"{s.nombre} [{type(s).__name__}]" for s in self.sistema.servicios]


if __name__ == "__main__":
    log.info("===== INICIO (modo gráfico) =====")
    App().mainloop()
