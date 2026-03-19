import tkinter as tk
import json
from tkinter import ttk, messagebox, scrolledtext, filedialog # Asegúrate que filedialog esté aquí
from tkinter import filedialog
from tkinter import ttk, messagebox, scrolledtext
from Constants import MAX_GENERATED_STRINGS, EPSILON
from GrammarLogic import GrammarLogic


# --- Interfaz Gráfica  ---

class GrammarApp:
    def __init__(self, master):
        self.master = master
        master.title("Generador de grámaticas")
        master.geometry("800x700")

        self.logic = GrammarLogic()
        self.production_rows_widgets = [] # Lista para guardar widgets de cada fila

        # --- Estilos ---
        style = ttk.Style()
        style.configure("TLabel", padding=5, font=('Helvetica', 10))
        style.configure("TButton", padding=3, font=('Helvetica', 9)) # Botones más pequeños
        style.configure("TEntry", padding=5, font=('Helvetica', 10))
        style.configure("Header.TLabel", font=('Helvetica', 12, 'bold'))
        style.configure("Result.TLabel", padding=5, font=('Helvetica', 10))
        style.configure("Error.TLabel", foreground="red", font=('Helvetica', 10))
        style.configure("Success.TLabel", foreground="green", font=('Helvetica', 10))

        # --- Layout Principal ---
        main_frame = ttk.Frame(master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Sección Definición Gramática ---
        grammar_frame = ttk.LabelFrame(main_frame, text="1. Definición de la Gramática", padding="10")
        grammar_frame.pack(fill=tk.X, pady=5)

        # Inputs S, T, NT (Simplificados, sin validación en tiempo real)
        ttk.Label(grammar_frame, text="Símbolo Inicial (S):").grid(row=0, column=0, sticky=tk.W)
        self.start_symbol_var = tk.StringVar()
        self.start_symbol_entry = ttk.Entry(grammar_frame, textvariable=self.start_symbol_var, width=15, font=('Helvetica', 10))
        self.start_symbol_entry.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(grammar_frame, text="Terminales (T) (e.g., a,b,c):").grid(row=1, column=0, sticky=tk.W)
        self.terminals_var = tk.StringVar()
        self.terminals_entry = ttk.Entry(grammar_frame, textvariable=self.terminals_var, width=50, font=('Helvetica', 10))
        self.terminals_entry.grid(row=1, column=1, columnspan=3, sticky=tk.W+tk.E)
        # Guardar T original para CYK
        self.logic.terminals_var = self.terminals_var 


        ttk.Label(grammar_frame, text="No Terminales (NT) (e.g., S,A,B):").grid(row=2, column=0, sticky=tk.W)
        self.non_terminals_var = tk.StringVar()
        self.non_terminals_entry = ttk.Entry(grammar_frame, textvariable=self.non_terminals_var, width=50, font=('Helvetica', 10))
        self.non_terminals_entry.grid(row=2, column=1, columnspan=3, sticky=tk.W+tk.E)

        # Frame para Producciones con botones Add/Remove
        prod_header_frame = ttk.Frame(grammar_frame)
        prod_header_frame.grid(row=3, column=0, columnspan=4, sticky=tk.W+tk.E, pady=(10,0))
        ttk.Label(prod_header_frame, text="Producciones (P):").pack(side=tk.LEFT)
        self.add_prod_button = ttk.Button(prod_header_frame, text="Añadir Producción", command=self.add_production_row)
        self.add_prod_button.pack(side=tk.RIGHT)


        # Canvas y Frame para las filas de producciones
        self.productions_canvas = tk.Canvas(grammar_frame, borderwidth=0, height=150)
        self.productions_frame = ttk.Frame(self.productions_canvas)
        self.productions_scrollbar = ttk.Scrollbar(grammar_frame, orient="vertical", command=self.productions_canvas.yview)
        self.productions_canvas.configure(yscrollcommand=self.productions_scrollbar.set)

        self.productions_canvas.grid(row=4, column=0, columnspan=4, sticky="nsew", pady=5)
        self.productions_scrollbar.grid(row=4, column=4, sticky="ns")

        self.productions_canvas_window = self.productions_canvas.create_window((0, 0), window=self.productions_frame, anchor="nw")
        
        # GrammarApp.py -> __init__

    # Frame para Producciones con botones Add/Remove/Save
        prod_header_frame = ttk.Frame(grammar_frame)
        prod_header_frame.grid(row=3, column=0, columnspan=4, sticky=tk.W+tk.E, pady=(10,0))
        ttk.Label(prod_header_frame, text="Producciones (P):").pack(side=tk.LEFT)

     # Botones a la derecha
        self.add_prod_button = ttk.Button(prod_header_frame, text="Añadir Producción", command=self.add_production_row)
        self.add_prod_button.pack(side=tk.RIGHT)

     # --- INICIO: Botón Guardar ---
        self.save_grammar_button = ttk.Button(prod_header_frame, text="Guardar Gramática", command=self.save_grammar_action)
        self.save_grammar_button.pack(side=tk.RIGHT, padx=(0, 5)) # Añadir padding entre botones
    # --- FIN: Botón Guardar ---

# ... (resto del __init__) ...

        
        def _configure_canvas(event):
             # Actualizar el ancho del frame interno al del canvas
             canvas_width = event.width
             self.productions_canvas.itemconfig(self.productions_canvas_window, width=canvas_width)
             # Actualizar la región de scroll
             self.productions_canvas.configure(scrollregion=self.productions_canvas.bbox("all"))
        
        self.productions_frame.bind("<Configure>", lambda e: self.productions_canvas.configure(scrollregion=self.productions_canvas.bbox("all")))
        self.productions_canvas.bind('<Configure>', _configure_canvas)


        grammar_frame.grid_rowconfigure(4, weight=1)
        grammar_frame.grid_columnconfigure(1, weight=1) # Permitir que las entradas RHS se expandan

        self.add_production_row() # Añadir la primera fila inicial


        # --- Sección Validación Tipo ---
        type_frame = ttk.LabelFrame(main_frame, text="2. Tipo de Gramática", padding="10")
        type_frame.pack(fill=tk.X, pady=5)

        self.validate_type_button = ttk.Button(type_frame, text="Validar Tipo de Gramática", command=self.validate_grammar_type_action)
        self.validate_type_button.pack(side=tk.LEFT, padx=5)
        self.grammar_type_label = ttk.Label(type_frame, text="Tipo: (Presione validar)", style="Result.TLabel")
        self.grammar_type_label.pack(side=tk.LEFT, padx=5)

        # --- Sección Validación Cadena ---
        validation_frame = ttk.LabelFrame(main_frame, text="3. Validación de Cadena", padding="10")
        validation_frame.pack(fill=tk.X, pady=5)

        ttk.Label(validation_frame, text="Cadena a validar:").pack(side=tk.LEFT, padx=5)
        self.string_to_validate_var = tk.StringVar()
        self.string_to_validate_entry = ttk.Entry(validation_frame, textvariable=self.string_to_validate_var, width=30, font=('Helvetica', 10))
        self.string_to_validate_entry.pack(side=tk.LEFT, padx=5)
        self.validate_string_button = ttk.Button(validation_frame, text="Validar Cadena", command=self.validate_string_action)
        self.validate_string_button.pack(side=tk.LEFT, padx=5)

        self.validation_result_label = ttk.Label(validation_frame, text="Resultado: (Ingrese cadena y valide)", style="Result.TLabel")
        self.validation_result_label.pack(side=tk.LEFT, padx=(10,0))


        # --- Sección Generación Cadenas ---
        generation_frame = ttk.LabelFrame(main_frame, text="4. Generación de Cadenas", padding="10")
        generation_frame.pack(fill=tk.BOTH, expand=True, pady=5) # Expandir esta sección

        gen_options_frame = ttk.Frame(generation_frame)
        gen_options_frame.pack(fill=tk.X)

        ttk.Label(gen_options_frame, text="Longitud (n):").pack(side=tk.LEFT, padx=5)
        self.generation_n_var = tk.StringVar()
        self.generation_n_entry = ttk.Entry(gen_options_frame, textvariable=self.generation_n_var, width=5, font=('Helvetica', 10))
        self.generation_n_entry.pack(side=tk.LEFT, padx=5)
        self.generate_strings_button = ttk.Button(gen_options_frame, text=f"Generar Cadenas (max {MAX_GENERATED_STRINGS})", command=self.generate_strings_action)
        self.generate_strings_button.pack(side=tk.LEFT, padx=5)
        
        self.generation_count_label = ttk.Label(generation_frame, text="Cadenas generadas: 0", style="Result.TLabel")
        self.generation_count_label.pack(anchor=tk.W, padx=5, pady=(5,0))

        self.generated_strings_text = scrolledtext.ScrolledText(generation_frame, height=6, width=70, wrap=tk.WORD, state=tk.DISABLED, font=('Courier New', 10))
        self.generated_strings_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


    def add_production_row(self):
        """ Añade una fila de widgets para ingresar una producción (con botón Remove) """
        row_frame = ttk.Frame(self.productions_frame)
        row_frame.pack(fill=tk.X, pady=1) # pady añade espacio entre filas

        lhs_entry = ttk.Entry(row_frame, width=10, font=('Helvetica', 10)) # LHS editable
        lhs_entry.pack(side=tk.LEFT, padx=(0, 0))
        
        ttk.Label(row_frame, text=" ->").pack(side=tk.LEFT, padx=(0, 5))
        
        rhs_entry = ttk.Entry(row_frame, font=('Helvetica', 10))
        rhs_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))

        remove_button = ttk.Button(row_frame, text="X", width=2, style="Toolbutton", 
                                  command=lambda rf=row_frame: self.remove_production_row(rf))
        remove_button.pack(side=tk.RIGHT)

        # Guardar referencia a los widgets para recolección y eliminación
        row_data = {'frame': row_frame, 'lhs': lhs_entry, 'rhs': rhs_entry}
        self.production_rows_widgets.append(row_data)
        
        # Actualizar scroll region después de añadir
        self.productions_frame.update_idletasks()
        self.productions_canvas.configure(scrollregion=self.productions_canvas.bbox("all"))
        # Scroll al final si es necesario
        self.productions_canvas.yview_moveto(1)


    def remove_production_row(self, row_frame_to_remove):
        """ Elimina una fila de producción de la GUI y de la lista interna """
        
        # Encontrar el índice de la fila a eliminar
        index_to_remove = -1
        for i, row_data in enumerate(self.production_rows_widgets):
            if row_data['frame'] == row_frame_to_remove:
                index_to_remove = i
                break
        
        if index_to_remove != -1:
            # Destruir widgets de la GUI
            self.production_rows_widgets[index_to_remove]['frame'].destroy()
            # Eliminar de la lista interna
            del self.production_rows_widgets[index_to_remove]

            # Actualizar scroll region
            self.productions_frame.update_idletasks()
            self.productions_canvas.configure(scrollregion=self.productions_canvas.bbox("all"))


    def _collect_productions(self):
        """ Recoge las producciones de los widgets de la GUI (simplificado) """
        productions_list = []
        for row_data in self.production_rows_widgets:
            lhs_val = row_data['lhs'].get()
            rhs_val = row_data['rhs'].get()
            # Añadir solo si el LHS tiene algo (evita filas completamente vacías)
            if lhs_val.strip():
                 productions_list.append((lhs_val, rhs_val))
        return productions_list

    def _parse_and_validate_grammar(self):
        """ Orquesta la lectura y validación (simplificada) de la gramática """
        start_symbol = self.start_symbol_var.get()
        terminals_str = self.terminals_var.get()
        non_terminals_str = self.non_terminals_var.get()
        productions_list = self._collect_productions()

        errors = self.logic.set_grammar(start_symbol, terminals_str, non_terminals_str, productions_list)
        
        if errors:
            # Mostrar errores como advertencias o errores dependiendo de la severidad
            error_str = "\n".join(errors)
            is_fatal = any("Error:" in e for e in errors) 
            if is_fatal:
                 messagebox.showerror("Error de Gramática", error_str)
                 self.grammar_type_label.config(text="Tipo: Error", style="Error.TLabel")
                 return False
            else: # Solo advertencias
                 messagebox.showwarning("Advertencia de Gramática", error_str)
                 # Permitir continuar pero marcar tipo como indefinido
                 self.grammar_type_label.config(text="Tipo: (Corregir advertencias)", style="Result.TLabel") 
                 # return True # O False si queremos que corrijan advertencias también
                 return True # Dejamos continuar

        return True # Sin errores ni advertencias graves

    def validate_grammar_type_action(self):
        """ Acción del botón 'Validar Tipo de Gramática' """
        self.grammar_type_label.config(text="Tipo: Validando...", style="Result.TLabel")
        self.master.update_idletasks() # Actualización visual

        if not self._parse_and_validate_grammar():
             # Si _parse_and_validate retorna False por errores fatales
             if "Error" not in self.grammar_type_label.cget("text"): # Si no puso ya el mensaje de error
                  self.grammar_type_label.config(text="Tipo: Error en definición", style="Error.TLabel")
             return 

        # Si _parse_and_validate retorna True (ok o solo warnings) procedemos a determinar tipo
        grammar_type_result = self.logic.determine_grammar_type()
        
        if "Error" in grammar_type_result: # Errores detectados en determine_grammar_type
             self.grammar_type_label.config(text=f"Tipo: {grammar_type_result}", style="Error.TLabel")
        else:
            self.grammar_type_label.config(text=f"Tipo: {grammar_type_result}", style="Result.TLabel")


    def validate_string_action(self):
        """ Acción del botón 'Validar Cadena' """
        self.validation_result_label.config(text="Resultado: Validando...", style="Result.TLabel")
        self.master.update_idletasks()

        # 1. Re-parsear y validar la gramática CADA VEZ para asegurar consistencia
        if not self._parse_and_validate_grammar():
             self.validation_result_label.config(text="Resultado: Corrija la gramática primero", style="Error.TLabel")
             return
        # 2. Determinar tipo si no se ha hecho o si hubo cambios/errores
        if not self.logic.grammar_type or "Error" in self.logic.grammar_type:
             grammar_type_result = self.logic.determine_grammar_type()
             if "Error" in grammar_type_result:
                  self.validation_result_label.config(text=f"Resultado: {grammar_type_result}", style="Error.TLabel")
                  self.grammar_type_label.config(text=f"Tipo: {grammar_type_result}", style="Error.TLabel") # Actualizar ambos
                  return
             else:
                 self.grammar_type_label.config(text=f"Tipo: {grammar_type_result}", style="Result.TLabel") # Actualizar tipo si ahora es válido

        # 3. Proceder con la validación de la cadena
        input_string = self.string_to_validate_var.get()
        
        # Validar si la cadena contiene símbolos que NO son terminales
        temp_input_str_check = input_string
        original_terminals = set(t.strip() for t in self.terminals_var.get().split(',') if t.strip()) # Usar T original
        while temp_input_str_check:
             found_term_val = False
             sorted_terms_val = sorted(list(original_terminals), key=len, reverse=True)
             if not sorted_terms_val and temp_input_str_check: # No hay terminales definidos pero hay cadena
                  self.validation_result_label.config(text=f"Error: No hay terminales definidos para validar '{input_string}'", style="Error.TLabel")
                  return
             for term in sorted_terms_val:
                 if temp_input_str_check.startswith(term):
                     temp_input_str_check = temp_input_str_check[len(term):]
                     found_term_val = True
                     break
             if not found_term_val and temp_input_str_check: # Queda cadena pero no hizo match con ningún terminal
                  self.validation_result_label.config(text=f"Error: Cadena '{input_string}' contiene símbolos inválidos/no terminales.", style="Error.TLabel")
                  return
        
        # Si pasó la validación de caracteres, proceder con el algoritmo
        # GrammarApp.py -> dentro de validate_string_action

# ... (después de las validaciones de tipo y parseo de cadena) ...

        try:
               belongs = False
               grammar_valid_for_derivation = True # Asumimos que sí inicialmente

               if self.logic.grammar_type == "Regular (Tipo 3)":
                    belongs = self.logic.validate_string_type3_direct(input_string)
               elif self.logic.grammar_type == "Libre de Contexto (Tipo 2)":
                    # CYK es bueno para pertenencia, pero no da la derivación fácil.
                    # Usaremos CYK para saber SI pertenece, y luego el backtracking para
                    # OBTENER la derivación si pertenece.
                    # Podríamos llamar directamente a get_derivation_steps y ver si
                    # devuelve algo, pero CYK suele ser más eficiente para solo chequear pertenencia.
                    try:
                         belongs = self.logic.run_cyk(input_string)
                    except ValueError as e:
                         # Errores como FNC fallida o símbolos inválidos manejados por CYK
                         self.validation_result_label.config(text=f"Error validación CYK: {e}", style="Error.TLabel")
                         belongs = False
                         grammar_valid_for_derivation = False # No intentar derivación si CYK falló así
               else:
                    # Para otros tipos o errores, no validamos
                    self.validation_result_label.config(text=f"Resultado: Tipo de gramática no soportado para validación", style="Error.TLabel")
                    belongs = False
                    grammar_valid_for_derivation = False


               if belongs:
                    self.validation_result_label.config(text=f"Resultado: Cadena '{input_string}' PERTENECE", style="Success.TLabel")

                    # --- INICIO: Código para mostrar derivación ---
                    if grammar_valid_for_derivation:
                         self.master.update_idletasks() # Actualizar UI antes de posible cálculo largo
                         print("Intentando obtener derivación...") # Log para depuración
                         deriv_steps = self.logic.get_derivation_steps(input_string)
                         print(f"Derivación obtenida: {deriv_steps is not None}") # Log

                         if deriv_steps:
                              # Mostrar la ventana con los pasos
                              self.show_derivation_window(input_string, deriv_steps)
                         else:
                              # Informar si pertenece pero no se pudo encontrar/mostrar derivación
                              messagebox.showinfo("Derivación", f"La cadena '{input_string}' pertenece, pero no se pudo reconstruir una derivación paso a paso con el método actual.", parent=self.master)
                    # --- FIN: Código para mostrar derivación ---

               else:
                    # Solo mostrar "NO PERTENECE" si no hubo un error previo que ya mostró mensaje
                    if "Error" not in self.validation_result_label.cget("style"):
                         self.validation_result_label.config(text=f"Resultado: Cadena '{input_string}' NO PERTENECE", style="Error.TLabel")

            # ... (resto del bloque try...except) ...     
        except ValueError as e: 
                    self.validation_result_label.config(text=f"Error validación: {e}", style="Error.TLabel")
                    # No mostrar messagebox para errores esperados como FNC incompleta o símbolos inválidos
        except NotImplementedError as e: 
                    self.validation_result_label.config(text=f"Error: {e}", style="Error.TLabel")
                    messagebox.showerror("Error de Implementación", str(e))
        except Exception as e: 
                    self.validation_result_label.config(text=f"Error inesperado: {e}", style="Error.TLabel")
                    import traceback
                    traceback.print_exc() # Imprimir traceback en consola para depuración
                    messagebox.showerror("Error Inesperado", f"Ocurrió un error durante la validación:\n{e}")

    # GrammarApp.py (dentro de la clase GrammarApp)

# ... (después de otros métodos) ...

    def save_grammar_action(self):
     """ Recoge la gramática de la UI y la guarda en un archivo JSON. """

     # 1. Recoger datos de la UI
     start_symbol = self.start_symbol_var.get().strip()
     terminals_str = self.terminals_var.get().strip()
     non_terminals_str = self.non_terminals_var.get().strip()
     productions_list_tuples = self._collect_productions() # [(lhs_str, rhs_str), ...]

     # Validaciones básicas (opcional, pero recomendable)
     if not start_symbol or not non_terminals_str or not productions_list_tuples:
          messagebox.showwarning("Guardar Gramática", "Faltan elementos esenciales de la gramática (S, NT o Producciones) para guardar.", parent=self.master)
          return

     terminals_list = [t.strip() for t in terminals_str.split(',') if t.strip()]
     non_terminals_list = [nt.strip() for nt in non_terminals_str.split(',') if nt.strip()]

     # Convertir producciones a un formato más estructurado para JSON
     # Aquí asumimos que RHS es una secuencia de símbolos concatenados
     # (Podría mejorarse si se parseara el RHS en símbolos individuales antes)
     productions_dict_list = []
     for lhs, rhs_str in productions_list_tuples:
          # Tratamos el RHS como una cadena por ahora, tal como se ingresa
          # Si se quisiera guardar como lista de símbolos, se necesitaría parseo
          productions_dict_list.append({"lhs": lhs.strip(), "rhs": rhs_str}) 
          # Alternativa (si parseas RHS a lista de símbolos en el futuro):
          # productions_dict_list.append({"lhs": lhs.strip(), "rhs": list_of_symbols_in_rhs})

     # 2. Crear el diccionario de la gramática
     grammar_data = {
          "start_symbol": start_symbol,
          "terminals": terminals_list,
          "non_terminals": non_terminals_list,
          "productions": productions_dict_list
     }

     # 3. Pedir al usuario la ubicación del archivo
     file_path = filedialog.asksaveasfilename(
          title="Guardar Gramática como JSON",
          defaultextension=".json",
          filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
          parent=self.master
     )

     # 4. Si el usuario seleccionó un archivo, guardarlo
     if file_path:
          try:
               with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(grammar_data, f, indent=4, ensure_ascii=False) # indent=4 para formato legible
               messagebox.showinfo("Guardar Gramática", f"Gramática guardada exitosamente en:\n{file_path}", parent=self.master)
          except IOError as e:
               messagebox.showerror("Error al Guardar", f"No se pudo escribir en el archivo:\n{e}", parent=self.master)
          except Exception as e:
               messagebox.showerror("Error Inesperado", f"Ocurrió un error al guardar:\n{e}", parent=self.master)

     # ... (después de otros métodos como generate_strings_action) ...

    def show_derivation_window(self, input_string, deriv_steps):
          """ Muestra una nueva ventana con los pasos de derivación. """
          deriv_win = tk.Toplevel(self.master)
          deriv_win.title(f"Derivación para: '{input_string}'")
          deriv_win.geometry("500x400") # Tamaño inicial

     # Frame para mejor layout
          frame = ttk.Frame(deriv_win, padding="10")
          frame.pack(expand=True, fill=tk.BOTH)

     # Etiqueta
          lbl = ttk.Label(frame, text="Pasos de Derivación (Izquierda):", font=('Helvetica', 11, 'bold'))
          lbl.pack(pady=(0, 5))

     # Área de texto con scroll
          text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=('Courier New', 10), height=15)
          text_area.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

     # Formatear los pasos
          derivation_text = ""
          if deriv_steps:
          # Añadir flechas entre pasos para claridad
               derivation_text += deriv_steps[0] # Paso inicial (S)
               for i in range(1, len(deriv_steps)):
               # Usar -> para producciones directas, => para derivaciones
                    derivation_text += f"\n  => {deriv_steps[i]}"
          else:
               derivation_text = "No se pudo generar la derivación."

          text_area.insert(tk.END, derivation_text)
          text_area.config(state=tk.DISABLED) # Hacerla de solo lectura

     # Botón para cerrar
          close_button = ttk.Button(frame, text="Cerrar", command=deriv_win.destroy)
          close_button.pack(pady=(10, 0))

     # Hacer la ventana modal (opcional, bloquea la ventana principal)
          deriv_win.grab_set()
          deriv_win.transient(self.master)
          self.master.wait_window(deriv_win)


    def generate_strings_action(self):
          """ Acción del botón 'Generar Cadenas' """
          self.generated_strings_text.config(state=tk.NORMAL)
          self.generated_strings_text.delete(1.0, tk.END)
          self.generated_strings_text.insert(tk.END, "Generando...")
          self.generated_strings_text.config(state=tk.DISABLED)
          self.generation_count_label.config(text="Cadenas generadas: Calculando...", style="Result.TLabel")
          self.master.update_idletasks()

          # Revalidar gramática y tipo antes de generar
          if not self._parse_and_validate_grammar():
               self.generated_strings_text.config(state=tk.NORMAL); self.generated_strings_text.delete(1.0, tk.END)
               self.generated_strings_text.insert(tk.END, "Corrija la gramática primero."); self.generated_strings_text.config(state=tk.DISABLED)
               self.generation_count_label.config(text="Cadenas generadas: Error", style="Error.TLabel")
               return
          if not self.logic.grammar_type or "Error" in self.logic.grammar_type:
               grammar_type_result = self.logic.determine_grammar_type()
               if "Error" in grammar_type_result:
                    self.generated_strings_text.config(state=tk.NORMAL); self.generated_strings_text.delete(1.0, tk.END)
                    self.generated_strings_text.insert(tk.END, f"Error en gramática: {grammar_type_result}"); self.generated_strings_text.config(state=tk.DISABLED)
                    self.generation_count_label.config(text="Cadenas generadas: Error", style="Error.TLabel")
                    self.grammar_type_label.config(text=f"Tipo: {grammar_type_result}", style="Error.TLabel")
                    return
               else:
                    self.grammar_type_label.config(text=f"Tipo: {grammar_type_result}", style="Result.TLabel")


          try:
               n_str = self.generation_n_var.get()
               n = int(n_str)
               if n < 0: raise ValueError("Longitud 'n' no puede ser negativa.")
          except ValueError:
               self.generated_strings_text.config(state=tk.NORMAL); self.generated_strings_text.delete(1.0, tk.END)
               self.generated_strings_text.insert(tk.END, "Error: Longitud 'n' debe ser un entero no negativo."); self.generated_strings_text.config(state=tk.DISABLED)
               self.generation_count_label.config(text="Cadenas generadas: Error", style="Error.TLabel")
               return

          try:
               # Usar T original para calcular longitud de cadenas generadas
               self.logic.terminals = set(t.strip() for t in self.terminals_var.get().split(',') if t.strip())
               generated = self.logic.generate_random_strings(n)
               
               self.generated_strings_text.config(state=tk.NORMAL)
               self.generated_strings_text.delete(1.0, tk.END)
               if generated:
                    self.generated_strings_text.insert(tk.END, "\n".join(generated))
               else:
                    # Podría ser que n=0 y S deriva epsilon
                    can_produce_epsilon = any(rule == [EPSILON] for rule in self.logic.productions.get(self.logic.start_symbol, []))
                    if n == 0 and can_produce_epsilon:
                         self.generated_strings_text.insert(tk.END, "(ε - Cadena Vacía)")
                         self.generation_count_label.config(text="Cadenas generadas: 1", style="Result.TLabel")
                    else:
                         self.generated_strings_text.insert(tk.END, "(Ninguna encontrada)")
                         self.generation_count_label.config(text="Cadenas generadas: 0", style="Result.TLabel")

               self.generated_strings_text.config(state=tk.DISABLED)
               if len(generated) > 0 : # Actualizar contador si encontró algo
                    self.generation_count_label.config(text=f"Cadenas generadas: {len(generated)}", style="Result.TLabel")


          except Exception as e:
               self.generated_strings_text.config(state=tk.NORMAL)
               self.generated_strings_text.delete(1.0, tk.END)
               self.generated_strings_text.insert(tk.END, f"Error inesperado durante la generación:\n{e}")
               self.generated_strings_text.config(state=tk.DISABLED)
               self.generation_count_label.config(text="Cadenas generadas: Error", style="Error.TLabel")
               import traceback
               traceback.print_exc()
               messagebox.showerror("Error de Generación", f"Ocurrió un error inesperado:\n{e}")

