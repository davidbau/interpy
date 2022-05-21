import numpy

# This is a comment!
'''
ok
'''
def example():
    def nested():
        return 'ok'
    a = numpy.linspace(0, 1, 100)
    print(a * a)
    return nested()

a = example()
print(a)



