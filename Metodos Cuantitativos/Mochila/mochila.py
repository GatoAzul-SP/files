# Resolvedor del problema de la mochila con programación entera
import pulp, sys, io

class Objeto:

    def __init__(self, peso, valor):
        if not (isinstance(peso, int) and isinstance(valor, int)):
            raise TypeError("peso y valor deben ser enteros: peso=%s ; valor=%s"
                            % (peso, valor) )
        if peso <= 0 or valor <= 0:
            raise ValueError("peso y valor deben ser positivos: peso=%s ; valor=%s"
                             % (peso, valor) )

        self.peso, self.valor = peso, valor

    def __repr__(self):
        return f"Objeto(peso={self.peso}, valor={self.valor})"

    def __str__(self):
        return repr(self)

class Mochila:
    "Resolvedor del problema de la mochila"

    def __init__(self, capacidad_maxima, objetos):
        if not (isinstance(capacidad_maxima, int) and isinstance(objetos, list)
                and all(isinstance(o, Objeto) for o in objetos)):
            raise TypeError(("capacidad_maxima debe ser un entero"
                             " y objetos debe ser una lista de Objeto:"
                             " capacidad=%r, objetos=%r")
                            % (capacidad_maxima, objetos) )

        self.capacidad_maxima = capacidad_maxima
        self.objetos = objetos

    def resolver(self):
        seleccion = resolver_mochila(self.capacidad_maxima, self.objetos)
        seleccion = [objeto for objeto, solucion in
                     zip(self.objetos, seleccion) if solucion == 1]

        valor_total = peso_total = 0
        for objeto in seleccion:
            valor_total += objeto.valor
            peso_total += objeto.peso

        return seleccion, valor_total, peso_total

    def __repr__(self):
        return (f"Mochila(capacidad_maxima={self.capacidad_maxima}"
                f", objetos=[{len(self.objetos)} objeto(s)...]")

    def __str__(self):
        return repr(self)

def resolver_mochila(capacidad_maxima, objetos):

    problema = pulp.LpProblem("Problema_de_la_mochila", pulp.LpMaximize)

    variables = [pulp.LpVariable(f"o_{i+1}", cat=pulp.LpBinary) for i in range(len(objetos))]

    problema += sum(o.valor * v for o, v in zip(objetos, variables)), "Valor_maximo"

    problema += sum(o.peso * v for o, v in zip(objetos, variables)) <= capacidad_maxima, "Límite_de_capacidad"

    # Silenciar CLI del resolverdor
    orig, pulp.LpSolverDefault.msg = pulp.LpSolverDefault.msg, False
    problema.solve()
    pulp.LpSolverDefault.msg = orig

    if problema.status != pulp.LpStatusOptimal:
        raise RuntimeError("no se pudo hallar la solución del problema")

    return [v.varValue for v in variables]

def main():
    print("Resolvedor del problema de la mochila",
          "Nota: use Ctrl+C para interrumpir\n",
          sep="\n")

    while True:
        capacidad = input("Indique la capacidad maxima de la mochila: ")
        try:
            capacidad = int(capacidad)
            if capacidad <= 0: raise ValueError()
        except ValueError:
            print("Error: la capacidad debe ser un entero positivo")
        else:
            break

    print("Indique a continuación el peso y valor de cada objeto,",
          "separado por espacios, y marque el final con un Enter,",
          "sin especificar valores.",
          sep="\n")

    i = 1; objetos = []
    while True:
        entrada = input(f"Objeto {i} (peso valor): ")
        if entrada == "": break
        entrada = entrada.split()

        if len(entrada) != 2:
            print("Error: especifique peso y valor separado por espacios",
                  "Ej: 23 45", sep="\n")
            continue

        try:
            entrada = list(map(int, entrada))
        except ValueError:
            pass
        try:
            objeto = Objeto(peso=entrada[0], valor=entrada[1])
        except (TypeError, ValueError) as e:
            print("Error:", e)
            continue

        objetos.append(objeto)
        i += 1

    if len(objetos) == 0:
        print("No se indicó ningún objeto. Intente nuevamente")
        return

    mochila = Mochila(capacidad, objetos)
    try:
        objetos, valor, peso = mochila.resolver()
    except RuntimeError as e:
        print("Error:", e)
        return

    print("Objetos seleccionados:")
    for objeto in objetos:
        print(objeto)
    print("Valor total:", valor)
    print("Peso total:", peso)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
