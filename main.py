import networkx as nx  # Estructura de grafos
import heapq  # Optimización de datos ordenados
import matplotlib.pyplot as plt  # Creación de gráficos
from matplotlib.animation import FuncAnimation  # Animación de gráficos
import math  # Para calcular distancias entre puntos

class Grafo:
    def __init__(self):
        self.grafo = nx.Graph()
        self.nodos = {
            'Almacen': (0, 0),
            'Area1': (2, 3), 'Area2': (4, 6), 'Area3': (6, 4),
            'Area4': (4, 0), 'Area5': (8, 0),
            'Recarga': (4, 3)
        }
        for nodo, pos in self.nodos.items():
            self.grafo.add_node(nodo, pos=pos)

        self.aristas = self.calcular_distancias()  # Se calculan las distancias automáticamente
        for u, v, w in self.aristas:
            self.grafo.add_edge(u, v, weight=w)

    def calcular_distancias(self):
        conexiones = [
            ('Almacen', 'Area1'), ('Area1', 'Area2'), ('Area2', 'Area3'),
            ('Area1', 'Area4'), ('Area4', 'Area5'), ('Area3', 'Area5'),
            ('Area2', 'Recarga'), ('Area3', 'Recarga'),
            ('Area4', 'Recarga'), ('Recarga', 'Area5')
        ]
        return [(u, v, self.distancia_euclidiana(u, v)) for u, v in conexiones]

    def distancia_euclidiana(self, nodo1, nodo2):
        x1, y1 = self.nodos[nodo1]
        x2, y2 = self.nodos[nodo2]
        return round(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2), 2)

    def dijkstra(self, inicio, destino):
        queue = [(0, inicio)]
        distancias = {nodo: float('inf') for nodo in self.grafo.nodes}
        previos = {nodo: None for nodo in self.grafo.nodes}
        distancias[inicio] = 0

        while queue:
            distancia_actual , nodo_actual = heapq.heappop(queue)
            if nodo_actual == destino:
                break

            for vecino in self.grafo.neighbors(nodo_actual):
                peso = self.grafo[nodo_actual][vecino]['weight']
                nueva_distancia = distancia_actual + peso
                if nueva_distancia < distancias[vecino]:
                    distancias[vecino] = nueva_distancia
                    previos[vecino] = nodo_actual
                    heapq.heappush(queue, (nueva_distancia, vecino))

        ruta, actual = [], destino
        while actual is not None:
            ruta.append(actual)
            actual = previos[actual]
        ruta.reverse()

        return ruta, distancias[destino] if distancias[destino] != float('inf') else None

class Robot:
    def __init__(self, capacidad_bateria=100, consumo_por_km=15, tarifa=0.5): #aqui se podra cambiar los datos q se
        #requiera, el porcentaje de consumo por km, la bateria y la tarifa
        self.bateria = capacidad_bateria
        self.consumo_por_km = consumo_por_km
        self.tarifa = tarifa

def simular():
    grafo = Grafo()
    robot = Robot(capacidad_bateria=100)  # Puedes cambiar la batería inicial aquí
    inicio = 'Almacen'
    destino = input("Ingrese el destino (Area1, Area2, Area3, Area4, Area5): ")

    if destino not in grafo.nodos:
        print("El destino no es válido.")
        return

    ruta, distancia_total = grafo.dijkstra(inicio, destino)

    if distancia_total is None:
        print("Disculpe, no hay ruta disponible.")
        return

    bateria_restante = robot.bateria
    distancia_total_real = 0
    ruta_completa = [inicio]  # Asegurar que siempre inicie en el Almacén

    print(f"🚀 Iniciando en {inicio} con {robot.bateria}% de batería.")

    for i in range(len(ruta) - 1):
        tramo = grafo.grafo[ruta[i]][ruta[i + 1]]['weight']
        bateria_gastada = tramo * robot.consumo_por_km

        if bateria_restante - bateria_gastada <= 10 and ruta[i] != "Almacen":
            print("⚠️ Batería baja. Redirigiendo a estación de recarga...")
            ruta_recarga, distancia_recarga = grafo.dijkstra(ruta[i], 'Recarga')
            if ruta_recarga and 'Recarga' not in ruta_completa:
                print(f"Parada en estación de recarga: {' -> '.join(ruta_recarga)}")
                bateria_restante = robot.bateria  # Recarga completa
                distancia_total_real += distancia_recarga
                ruta_completa.extend(ruta_recarga[1:])
                continue

        bateria_restante -= bateria_gastada
        distancia_total_real += tramo
        ruta_completa.append(ruta[i + 1])

        print(f"De {ruta[i]} a {ruta[i + 1]}: {tramo} km - Batería usada: {bateria_gastada}% - Batería restante: {bateria_restante}%")

    costo = distancia_total_real * robot.tarifa
    print(f"\n Ruta óptima: {' -> '.join(ruta_completa)}")
    print(f" Distancia total: {distancia_total_real} km")
    print(f" Tarifa del viaje: ${costo:.2f}")
    visualizar_ruta(grafo, ruta_completa)

def visualizar_ruta(grafo, ruta):
    pos = nx.get_node_attributes(grafo.grafo, 'pos')
    fig, ax = plt.subplots()

    def update(frame):
        ax.clear()
        nx.draw(grafo.grafo, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2000,
                font_size=10)
        path_edges = [(ruta[i], ruta[i + 1]) for i in range(len(ruta) - 1)]
        nx.draw_networkx_edges(grafo.grafo, pos, edgelist=path_edges, edge_color='red', width=2)
        nx.draw_networkx_nodes(grafo.grafo, pos, nodelist=ruta[:frame + 1], node_color='green', node_size=2000)
        edge_labels = nx.get_edge_attributes(grafo.grafo, 'weight')
        nx.draw_networkx_edge_labels(grafo.grafo, pos, edge_labels=edge_labels)

    ani = FuncAnimation(fig, update, frames=len(ruta), repeat=False, interval=800)
    plt.show()

if __name__ == "__main__":
    simular()
