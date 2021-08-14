from queue import Queue
import numpy as np
import ntpath
import os
from time import time

def combine_columns(singletonMatrixPartition):
    #VIENE UTILIZZATO -1 al posto di 'x'
    res = np.zeros((singletonMatrixPartition.shape[0], 1), dtype=np.int64)
    while singletonMatrixPartition.shape[1] >= 2:
        c1 = np.array(singletonMatrixPartition[:, 0], dtype=np.int64)
        c2 = np.array(singletonMatrixPartition[:, 1], dtype=np.int64)
        i = 0
        while i < singletonMatrixPartition.shape[0]:
            if c1[i] != 0 and c2[i] != 0:
                res[i] = -1
            elif c1[i] == -1 or c2[i] == -1:
                res[i] = -1
            elif c1[i] != 0 and c2[i] == 0:
                res[i] = c1[i]
            elif c1[i] == 0 and c2[i] != 0:
                res[i] = c2[i]
            elif c1[i] == 0 and c2[i] == 0:
                res[i] = 0
            i += 1
        singletonMatrixPartition = np.delete(singletonMatrixPartition, [0, 1], 1)
        singletonMatrixPartition = np.concatenate((res, singletonMatrixPartition), axis=1)
    return singletonMatrixPartition

def build_representativeVector(lamda, singletonRepresentativeMatrix):
    '''
    Costruisce il vettore rappresentativo di un insieme lamda
    :param lamda: insieme di cui costruire il vettore rappresentative
    :param singletonRepresentativeMatrix: matrice dei vettori rappresentativi dei
    sottoinsiemi singoletti di M
    :return: il vettore rappresentativo
    '''
    if lamda.size == 0:
        return np.zeros((singletonRepresentativeMatrix.shape[0], lamda.size), dtype=np.int64)
    elif lamda.size == 1: #singoletto
        return np.array(singletonRepresentativeMatrix[:, lamda[0]-1])
    else:
        return combine_columns(singletonRepresentativeMatrix[:, lamda - [1]])

def build_projection(lamda, representativeVector):
    '''
    Costruisce la proiezione del contenuto del
    vettore rappresentativo sull'insieme lamda associato
    :param lamda: insieme associato al vettore rappresentativo
    :param representativeVector: vettore rappresentativo di lamda
    :return: la proiezione intesa come insieme di elementi di lamda
    contenuti nel vettore rappresentativo
    '''
    projection = np.array([], dtype=np.int64)
    for elem in representativeVector:
        if elem in lamda:
            projection = np.append(projection,[elem])
    return set(projection)

def check(lamda, singletonRepresentativeMatrix):
    '''
    Effettua il controllo  CHECK sull'insieme lamda che gli viene passato
    :param lamda: insieme lamda di cui effettuare il CHECK
    :param singletonRepresentativeMatrix matrice dei vettori rappresentative dei singoletti
    :return: OK se l'insieme è un potenziale hitting set, KO se l'insieme non è un
    hitting set né può diventarlo, MHS se l'insieme è già un minimum hitting set
    '''

    representativeVector = build_representativeVector(lamda, singletonRepresentativeMatrix)
    projection = build_projection(lamda, representativeVector)

    #CHECK RULE
    if projection == set(lamda):
            if np.count_nonzero(representativeVector) == len(representativeVector):
                return 'MHS'
            else:
                return 'OK'
    else:
        return 'KO'


def output(lamda, counMHS):
    '''
    effettua l'ouput dell'insieme lamda, rivelatosi un mhs, insieme alla sua cardinalità e al conteggio corrente di mhs trovati
    :param lamda: di cui effettuare l'output
    :return: l'output di lamda mhs
    '''

    #VERSIONE DI PROVA
    print('MHS found: {} of dimension {}'.format(lamda, lamda.size))
    print('MHS encountered : {} \n'.format(counMHS))

def getSingletonRepresentativeMatrix(A):
    '''
    Restituisce una matrice, intesa come vettore di vettori, contenente i vettori
    rappresentativi degli sotto-insiemi singoletti di M
    :param A: matrice di input
    :return: i vettori rappresentativi degli insiemi singoletti
    '''
    singletonMatrix = A
    for i in range(singletonMatrix.shape[0]):
        for j in range(singletonMatrix.shape[1]):
            if singletonMatrix[i, j] == 1:
                singletonMatrix[i, j] = j + 1
    return singletonMatrix

def mbase(A, timeEnabled=True):
    if timeEnabled:
        start = time()
    coda = Queue(maxsize=0)
    coda.put(np.array([], dtype=np.int64))
    countMHS = 0

    singletonRepresentativeMatrix = getSingletonRepresentativeMatrix(A)
    M = list(range(1,A.shape[1]+1)) #prendo gli elementi di M
    #NB: M è già ordinato in ordine crescente per costruzione

    while not coda.empty():
        alpha = coda.get()

        if alpha.size == 0:
            e = min(M)
        else:
            e = np.amax(alpha) + 1
        while e <= max(M):
            lamda = np.append(alpha, np.array(e, dtype=np.int64))
            #print('Esaminando lamda {}'.format(lamda))
            result = check(lamda, singletonRepresentativeMatrix)
            if result == 'OK' and e != max(M):
                coda.put(lamda)
            elif result == 'MHS':
                countMHS += 1
                output(lamda, countMHS)
            # else:
            #     print('{} KO'.format(lamda))
            e += 1 #succ(e)
    if timeEnabled:
        end = time()
        print("MBASE required %.4f seconds to execute" % (end-start))

def getMatrixFromFile(filename):
    '''
    Legge un file .matrix dato il filename e restituisce una matrice a partire
    dal suo contenuto
    Per esempio a partire da './benchmarks1/74L85.000.matrix' si analizza il
    contenuto del file 74L85.000.matrix per creare la matrice
    :param filename: nome del file .matrix (indirizzo completo)
    :return: la matrice A costruita a partire dal contenuto del file
    '''
    print(ntpath.basename(filename))
    if os.stat(filename).st_size == 0:
        return np.array([[]],dtype=np.int64)
    else:
        file = open(filename, 'r')
        lines = file.readlines()
        lines = lines[5:]
        lines = [str.replace(line, ' -\n', '') for line in lines]
        lines = [str.replace(line, ' ', ',') for line in lines]
        #adesso abbiamo le righe della matrice A e possiamo costruirla
        rows = []
        for line in lines:
            rows.append(np.fromstring(line, sep=','))
        A = np.array(rows, dtype=np.int64)
        file.close()
        return A

def del_rows(A):
    toBeRemoved = np.array([], dtype=np.int64)
    i, ii = 0, A.shape[0]-1
    while i <= A.shape[0] - 2 and ii >= 1:
        j, jj = i + 1, ii - 1
        while j <= A.shape[0] - 1 and jj >= 0:
            diff = A[i] - A[j]
            if np.count_nonzero(diff == -1) == 0:  # A[i] super A[j]
                toBeRemoved = np.append(toBeRemoved, [i])
            diff = A[ii] - A[jj]
            if np.count_nonzero(diff == -1) == 0:  # A[ii] super A[jj]
                toBeRemoved = np.append(toBeRemoved, [ii])
            j += 1
            jj -= 1
        i += 1
        ii -= 1
    toBeRemoved = np.unique(toBeRemoved)
    A = np.delete(A, toBeRemoved, axis=0)
    return A

def del_cols(A):
    A = A[:, ~np.all(A == 0, axis=0)]
    return A

def pre_processing(A):
    A = del_rows(A)
    A = del_cols(A)
    return A

#PRIMO FILE DI UN BENCHMARK -> OK!
A = getMatrixFromFile(filename='74L85.008.matrix')
if np.size(A) == 0:
    print("The specified file is empty. Can't start the computation")
else:
    A = pre_processing(A)
    print('(|N| = {}, |M| = {}) \n'.format(A.shape[0], A.shape[1]))
    mbase(A)

#ESEMPIO VISTO IN AULA -> OK!
    # A = np.matrix([[1, 1, 1, 0, 0, 0],
    #               [0, 1, 1, 1, 0, 1],
    #               [0, 1, 1, 0, 0, 0],
    #               [1, 0, 1, 0, 0, 1],
    #               [1, 1, 1, 1, 0, 0],
    #               [0, 1, 1, 1, 0, 1],
    #               [0, 0, 1, 1, 0, 0]], dtype=np.int64)