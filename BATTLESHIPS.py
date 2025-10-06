import numpy as np
import random, string, os

# ================= CONFIG =================
TAM = 10
FLOTA = [5, 4, 3, 3, 2]

AGUA, BARCO, AGUA_TIRO, BARCO_TIRO = 0, 1, 2, 3

SIMBOLOS_OCULTO = {AGUA: "·", BARCO: "·", AGUA_TIRO: "o", BARCO_TIRO: "X"}
SIMBOLOS_REVELADO = {AGUA: "·", BARCO: "■", AGUA_TIRO: "o", BARCO_TIRO: "X"}

# ========== IMPRESIÓN ==========
def cabecera_cols(n):
    letras = list(string.ascii_uppercase)[:n]
    return "   " + " ".join(letras)

def render_linea(i, fila, simbolos):
    return f"{i+1:>2} " + " ".join(simbolos[int(x)] for x in fila)

def render_lado_a_lado(tab_izq, tab_der, tit_izq, tit_der):
    left = [tit_izq, cabecera_cols(tab_izq.shape[1])] + [render_linea(i, tab_izq[i], SIMBOLOS_REVELADO) for i in range(tab_izq.shape[0])]
    right = [tit_der, cabecera_cols(tab_der.shape[1])] + [render_linea(i, tab_der[i], SIMBOLOS_OCULTO) for i in range(tab_der.shape[0])]
    ancho = max(len(l) for l in left) + 4
    return "\n".join(l.ljust(ancho) + r for l, r in zip(left, right))

# ========== BARCOS ==========
def dentro(tablero, pos):
    f, c = pos
    return 0 <= f < tablero.shape[0] and 0 <= c < tablero.shape[1]

def adyacentes(pos):
    f, c = pos
    return [(f+df, c+dc) for df in (-1,0,1) for dc in (-1,0,1) if not (df==0 and dc==0)]

def coloca_barco_plus(tablero, posiciones):
    for pos in posiciones:
        if not dentro(tablero, pos) or tablero[pos] == BARCO:
            return None
        for v in adyacentes(pos):
            if dentro(tablero, v) and tablero[v] == BARCO:
                return None
    nuevo = tablero.copy()
    for p in posiciones:
        nuevo[p] = BARCO
    return nuevo

def crea_barco_aleatorio(tablero, eslora=4, num_intentos=1000):
    for _ in range(num_intentos):
        barco = []
        fila, col = random.randint(0,9), random.randint(0,9)
        barco.append((fila, col))
        orientacion = random.choice(["N","S","E","O"])
        f, c = fila, col
        for _ in range(eslora-1):
            if orientacion == "N": f -= 1
            elif orientacion == "S": f += 1
            elif orientacion == "E": c += 1
            else: c -= 1
            barco.append((f, c))
        t_temp = coloca_barco_plus(tablero, barco)
        if isinstance(t_temp, np.ndarray):
            return t_temp
    return None

def coloca_flota(tablero, flota):
    t = tablero.copy()
    for e in flota:
        while True:
            t2 = crea_barco_aleatorio(t, e)
            if t2 is not None:
                t = t2
                break
    return t

# ========== DISPAROS ==========
def disparo(tab, pos):
    f, c = pos
    if tab[f,c] in (AGUA_TIRO, BARCO_TIRO):
        return None
    if tab[f,c] == BARCO:
        tab[f,c] = BARCO_TIRO
        return True
    tab[f,c] = AGUA_TIRO
    return False

def quedan_barcos(tab):
    return np.any(tab == BARCO)

# ========== INPUT ==========
def parse_coord(txt):
    txt = txt.strip().replace(",", " ").upper()
    letras = list(string.ascii_uppercase)
    for ch in txt:
        if ch.isalpha():
            letra = ch
            num = "".join(x for x in txt if x.isdigit())
            if num:
                fila = int(num)-1
                col = letras.index(letra)
                if 0 <= fila < TAM and 0 <= col < TAM:
                    return (fila, col)
    return None

# ========== CPU SIMPLE ==========
class IA:
    def __init__(self):
        self.disparados = set()
    def elige(self):
        while True:
            p = (random.randint(0,9), random.randint(0,9))
            if p not in self.disparados:
                self.disparados.add(p)
                return p

# ========== JUEGO ==========
def prepara_tablero():
    t = np.zeros((TAM,TAM),int)
    return coloca_flota(t,FLOTA)

def main():
    os.system("cls" if os.name=="nt" else "clear")
    print("=== BATALLA NAVAL: Usuario vs Ordenador ===")
    user = prepara_tablero()
    cpu = prepara_tablero()
    ia = IA()

    ronda = 1
    while True:
        os.system("cls" if os.name=="nt" else "clear")
        print(f"===== RONDA {ronda} =====\n")
        print(render_lado_a_lado(user, cpu, "Tu tablero", "CPU (oculto)"))
        
        # Turno usuario
        while True:
            tiro = input("\nTu disparo (A5, 5A...): ")
            pos = parse_coord(tiro)
            if not pos: 
                print("Entrada no válida.")
                continue
            resultado = disparo(cpu, pos)
            if resultado is None:
                print("Ya habías disparado ahí.")
                continue
            print("💥 ¡Tocado!" if resultado else "🌊 Agua...")
            break

        if not quedan_barcos(cpu):
            print("\n🎉 ¡Has ganado!")
            print(render_lado_a_lado(user, cpu, "Tu tablero", "CPU (final revelado)"))
            break

        # Turno CPU
        pos_cpu = ia.elige()
        acierto = disparo(user, pos_cpu)
        letra = string.ascii_uppercase[pos_cpu[1]]
        print(f"\n🖥️  El ordenador dispara a {letra}{pos_cpu[0]+1}: {'💥 Tocado!' if acierto else '🌊 Agua...'}")
        input("\nPresiona ENTER para continuar...")
        if not quedan_barcos(user):
            os.system("cls" if os.name=='nt' else 'clear')
            print("\n💀 El ordenador hundió toda tu flota.")
            print(render_lado_a_lado(user, cpu, "Tu tablero (final)", "CPU (revelado)"))
            break

        ronda += 1

if __name__ == "__main__":
    main()
