import numpy as np
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.optimize import linprog


def oblicz(wspolczynniki_k, ograniczenia_k_dolne, ograniczenia_k_gorne, funckja_celu, result_label):
    wspolczynniki_k_przeciwne = [[value * -1 for value in row] for row in
                                 wspolczynniki_k]
    ograniczenia_k_dolne_przeciwne = [value * -1 if value is not None else None for value in ograniczenia_k_dolne]

    # A_ub i b_ub
    wspolczynniki_funkcji_ograniczajacych = wspolczynniki_k + wspolczynniki_k_przeciwne
    ograniczenia_funkcji = ograniczenia_k_gorne + ograniczenia_k_dolne_przeciwne

    if wspolczynniki_funkcji_ograniczajacych and ograniczenia_funkcji:
        filtered_data = [
            (ograniczenie, wspolczynniki) for ograniczenie, wspolczynniki in
            zip(ograniczenia_funkcji, wspolczynniki_funkcji_ograniczajacych)
            if ograniczenie is not None
        ]

        if filtered_data:
            ograniczenia_funkcji, wspolczynniki_funkcji_ograniczajacych = zip(*filtered_data)
            wspolczynniki_funkcji_ograniczajacych = list(wspolczynniki_funkcji_ograniczajacych)
            ograniczenia_funkcji = list(ograniczenia_funkcji)

            wspolczynniki_funckji_celu = [-x for x in funckja_celu]
            result = linprog(c=wspolczynniki_funckji_celu, A_ub=wspolczynniki_funkcji_ograniczajacych,
                             b_ub=ograniczenia_funkcji,
                             method='simplex')

            if result.success:
                print(f"Maksymalny zysk: {-result.fun} zł")
                print(f"Liczba godzin dla A (x1): {result.x[0]}")
                print(f"Liczba godzin dla B (x2): {result.x[1]}")
                result_label.config(
                    text=f"Maksymalny zysk: {-result.fun} zł | (x1, x2): ({result.x[0]}, {result.x[1]})")
            else:
                print("Nie znaleziono rozwiązania.")
                result_label.config(text="Nie znaleziono rozwiązania.")

            if result.success:
                x = np.linspace(0, result.x[0] + 100)

                plot_window = tk.Toplevel()
                plot_window.title("Wykres ograniczeń i rozwiązanie")
                plot_window.geometry("1200x900")

                fig = Figure(figsize=(7, 5), dpi=100)
                ax = fig.add_subplot(111)
                colors = ['blue', 'green', 'orange', 'purple', 'brown', 'cyan']

                for i in range(len(wspolczynniki_funkcji_ograniczajacych)):
                    x1, x2 = wspolczynniki_funkcji_ograniczajacych[i]
                    color = colors[i % len(colors)]
                    if x2 != 0:  # prosta ukośna
                        y = (ograniczenia_funkcji[i] - x1 * x) / x2
                        ax.plot(x, y, label=f'Ograniczenie {x1}x1 + {x2}x2 = {ograniczenia_funkcji[i]}', color=color)
                    else:  # prosta pionowa
                        x_vert = ograniczenia_funkcji[i] / x1 if x1 != 0 else 0
                        ax.axvline(x=x_vert,
                                   label=f'Ograniczenie {x1}x1 + {x2}x2 = {ograniczenia_funkcji[i]} (P)', color=color)

                ax.scatter(result.x[0], result.x[1], color='red', label='Rozwiązanie optymalne')
                ax.annotate(f"({result.x[0]:.2f}, {result.x[1]:.2f})", (result.x[0], result.x[1]),
                            textcoords="offset points",
                            xytext=(-10, 10), ha='center')

                # funkcja celu
                z = wspolczynniki_funckji_celu[0] * result.x[0] + wspolczynniki_funckji_celu[1] * result.x[
                    1]
                y_cel = (z - wspolczynniki_funckji_celu[0] * x) / wspolczynniki_funckji_celu[
                    1]  # przeksztalcenie na y
                ax.plot(x, y_cel, color='purple', linestyle='--',
                        label=f'Funkcja celu f(x1, x2) = {funckja_celu[0]}x1 {"+" if funckja_celu[1] >= 0 else "-"} {abs(funckja_celu[1])}x2 --> max')

                ax.set_xlim(0, result.x[0] + 10)
                ax.set_ylim(0, result.x[1] + 10)
                ax.set_xlabel('x1')
                ax.set_ylabel('x2')
                ax.set_title('Wykres ograniczeń i rozwiązanie')
                ax.legend()
                ax.grid()

                canvas = FigureCanvasTkAgg(fig, master=plot_window)
                canvas.draw()
                canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        else:
            ograniczenia_funkcji = []
            wspolczynniki_funkcji_ograniczajacych = [[], []]
    else:
        ograniczenia_funkcji = []
        wspolczynniki_funkcji_ograniczajacych = [[], []]

    print(ograniczenia_funkcji, wspolczynniki_funkcji_ograniczajacych)


def validate_entry(new_value):
    if new_value == "":
        return True
    if new_value.isdigit():
        return True
    if new_value.startswith('-') and (new_value[1:].isdigit() or new_value[1:] == ""):
        return True
    return False


def window():
    window = tk.Tk()
    window.title("Wybor parametrow")
    validate_command = window.register(validate_entry)

    columns = ["Ciasto/Mąka", "Żytnia", "Pszenna"]
    rows = ["A", "B"]

    frame = tk.Frame(window)
    frame.pack(anchor='w', padx=10, pady=10)

    entry_params = {
        "width": 10,
        "justify": "center",
        "validate": "key",
        "validatecommand": (validate_command, '%P')
    }

    for column in columns:
        label = tk.Label(frame, text=column, borderwidth=1, relief="solid", width=12, anchor="center")
        label.grid(row=0, column=columns.index(column))

    for row in rows:
        label = tk.Label(frame, text=row, borderwidth=1, relief="solid", width=12, anchor="center")
        label.grid(row=rows.index(row) + 1, column=0)

    entry_k1_w1 = tk.Entry(frame, **entry_params)
    entry_k1_w1.grid(row=1, column=1)
    entry_k1_w2 = tk.Entry(frame, **entry_params)
    entry_k1_w2.grid(row=2, column=1)
    entry_k2_w1 = tk.Entry(frame, **entry_params)
    entry_k2_w1.grid(row=1, column=2)
    entry_k2_w2 = tk.Entry(frame, **entry_params)
    entry_k2_w2.grid(row=2, column=2)

    entry_k1_w1.insert(0, '2')
    entry_k1_w2.insert(0, '3')
    entry_k2_w1.insert(0, '2')
    entry_k2_w2.insert(0, '0')

    entries = [
        [entry_k1_w1, entry_k1_w2],
        [entry_k2_w1, entry_k2_w2],
    ]

    columns_k = ["Ograniczenia", "MIN", "MAX"]
    rows_k = ["Żytnia", "Przenna"]

    frame_k = tk.Frame(window)
    frame_k.pack(anchor="w", padx=10, pady=10)

    for column in columns_k:
        label = tk.Label(frame_k, text=column, borderwidth=1, relief="solid", width=12, anchor="center")
        label.grid(row=0, column=columns_k.index(column))

    for row in rows_k:
        label = tk.Label(frame_k, text=row, borderwidth=1, relief="solid", width=12, anchor="center")
        label.grid(row=rows_k.index(row) + 1, column=0)

    entry_k1_lower_bound = tk.Entry(frame_k, **entry_params)
    entry_k1_lower_bound.grid(row=1, column=1)
    entry_k1_upper_bound = tk.Entry(frame_k, **entry_params)
    entry_k1_upper_bound.grid(row=1, column=2)
    entry_k2_lower_bound = tk.Entry(frame_k, **entry_params)
    entry_k2_lower_bound.grid(row=2, column=1)
    entry_k2_upper_bound = tk.Entry(frame_k, **entry_params)
    entry_k2_upper_bound.grid(row=2, column=2)

    entry_k1_lower_bound.insert(0, '')
    entry_k1_upper_bound.insert(0, '12')
    entry_k2_lower_bound.insert(0, "")
    entry_k2_upper_bound.insert(0, '6')

    entries_k_dolne = [entry_k1_lower_bound, entry_k2_lower_bound]
    entries_k_gorne = [entry_k1_upper_bound, entry_k2_upper_bound]

    columns_f = ["Funkcja celu", "A", "B"]
    rows_f = ["Zysk"]

    frame_f = tk.Frame(window)
    frame_f.pack(anchor="w", padx=10, pady=10)

    for column in columns_f:
        label = tk.Label(frame_f, text=column, borderwidth=1, relief="solid", width=12, anchor="center")
        label.grid(row=0, column=columns_f.index(column))

    for row in rows_f:
        label = tk.Label(frame_f, text=row, borderwidth=1, relief="solid", width=12, anchor="center")
        label.grid(row=rows_f.index(row) + 1, column=0)

    entry_x1 = tk.Entry(frame_f, **entry_params)
    entry_x1.grid(row=1, column=1)
    entry_x2 = tk.Entry(frame_f, **entry_params)
    entry_x2.grid(row=1, column=2)

    entry_x1.insert(0, '3')
    entry_x2.insert(0, '1')

    entries_funkcja_celu = [entry_x1, entry_x2]

    def ustaw_ograniczenia(entries, ograniczenia_k):
        for entry in entries:
            value = entry.get()
            if value == "":
                value = None
            else:
                value = int(value)
            ograniczenia_k.append(value)

    def update_data():
        wspolczynniki_k = []
        for row in entries:
            row_values = []
            for entry in row:
                value = entry.get()
                if value == "":
                    value = 0
                else:
                    value = int(value)
                row_values.append(value)
            wspolczynniki_k.append(row_values)

        ograniczenia_k_dolne = []
        ograniczenia_k_gorne = []
        funckja_celu = []

        ustaw_ograniczenia(entries_k_dolne, ograniczenia_k_dolne)
        ustaw_ograniczenia(entries_k_gorne, ograniczenia_k_gorne)
        ustaw_ograniczenia(entries_funkcja_celu, funckja_celu)

        print(wspolczynniki_k, ograniczenia_k_dolne, ograniczenia_k_gorne)
        oblicz(wspolczynniki_k, ograniczenia_k_dolne, ograniczenia_k_gorne, funckja_celu, result_label)

    button_label_frame = tk.Frame(window)
    button_label_frame.pack(anchor='w', padx=10, pady=(0, 10))

    update_button = tk.Button(button_label_frame, anchor='w', text="Oblicz", command=update_data)
    update_button.pack(side="left")

    result_label = tk.Label(button_label_frame, text="", fg="red")
    result_label.pack(side="left", padx=10)

    window.mainloop()


if __name__ == "__main__":
    window()
