import copy
import random

import networkx as nx

from database.DAO import DAO
from geopy.distance import distance


class Model:
    def __init__(self):
        self._allProviders = DAO.getProviders()
        self._grafo = nx.Graph()

    def getCammino(self, target, substring):
        sources = self.getNodesMostVicini()
        source= sources[random.randint(0, len(sources) - 1)][0]
        if not nx.has_path(self._grafo, source, target):
            return [], source
        self._bestPath = []
        self._bestLen = 0
        parziale=[source]
        self._ricorsione(parziale, target, substring)
        return self._bestPath, source

    def _ricorsione(self, parziale, target, substring):
        if parziale[-1] == target:
            if len(parziale) > self._bestLen:
                self._bestLen = len(parziale)
                self._bestPath = copy.deepcopy(parziale)
            return
        for v in self._grafo.neighbors(parziale[-1]):
            if v not in parziale and substring not in v.Location:
                parziale.append(v)
                self._ricorsione(parziale, target, substring)
                parziale.pop()

    def buildGraph(self, provider, soglia):
        self._nodes = DAO.getLocationsOfProviderV2(provider)
        self._grafo.add_nodes_from(self._nodes)
        for u in self._nodes:
            for v in self._nodes:
                if u != v:
                    dist = distance((u.latitude, u.longitude), (v.latitude, v.longitude)).km
                    if dist < soglia:
                        self._grafo.add_edge(u, v, weight=dist)

    def getNodesMostVicini(self):
        listTuples = []
        for n in self._nodes:
            listTuples.append((n, len(list(self._grafo.neighbors(n)))))
        listTuples.sort(key=lambda x: x[1], reverse=True)
        # per prendere solo i nodi con il maggior numero di vicini
        result = [x for x in listTuples if x[1] == listTuples[0][1]]
        return result

    def getGraphDetails(self):
        return len(self._grafo.nodes), len(self._grafo.edges)

    def getGraphNodes(self):
        return self._grafo.nodes
