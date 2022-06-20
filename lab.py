import timeit





ret=timeit.timeit('(list_a[i]+list_b[i] for i in range(3))','from random import randint;list_a=[randint(-5,5) for i in range(3)];list_b=[randint(-5,5) for i in range(3)];import operator', number=100000)
print(ret)

ret=timeit.timeit('tuple(map(operator.add,list_a,list_b))','from random import randint;list_a=[randint(-5,5) for i in range(3)];list_b=[randint(-5,5) for i in range(3)];import operator', number=100000)
print(ret)

