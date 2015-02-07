import sys
import elmustachio

elmustachio.init()

for filename in sys.argv[1:]:
    print(filename +':')
    result = elmustachio.goMustachioGo(filename)
    if result != None:
        print(result)
    else:
        print('Failed.')
