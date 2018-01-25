a = [{"a":1},{"a":2},{"a":3}]

for x in a:
    if x['a']==2:
        a.remove(x)

print(a)
