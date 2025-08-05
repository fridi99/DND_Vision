import random
def kill_repeated_elements (li):
    """The following loop removes repeated elements in a list in linear time."""
    i = 0
    while i < len(li):
        print(li[:i])
        if li[i] in li[:i]:
            li.pop(i)
        else:
            i += 1
    return li

i = 0
tester = []
while i < 10000:
    i += 1
    tester.append(random.randint(1, 20))
print(kill_repeated_elements(tester))