import random
from Enemy import *
def progress_bar(fill, max):
    if max > 25:
        dividend = max/25
        fill /= dividend
    bar = "|"
    for i in range(25):
        bar += "---"
    bar += "|"
    b = list(bar)
    for i in range(round(fill)):
        b.remove(b[i+1])
        b.remove(b[i + 1])
        b[i+1] = "█"
    return "".join(b)

def percentage(number):
    number *= 100
    num = str(number)+"%"
    return num


# maplist = []
# top_exit = random.randint(2, 6)
# bottom_start = random.randint(37, 41)
# block = random.randint(15, 28)
# maplist.append(top_exit)
# maplist.append(bottom_start)
# maplist.append(bottom_start-7)
# maplist.append(top_exit+7)
# maplist.append(block)
# mapimproved = []
#
# if block in [15, 16, 17, 18, 19, 20, 21]:
#     maplist.append(block-7)
#     for i in range(abs((block-7)-(top_exit+7))):
#         if (block-7)-(top_exit+7) > 0:
#             maplist.append((top_exit+7)+(i+1))
#         else:
#             maplist.append((top_exit+7) - (i + 1))
#     maplist.append(block+7)
#     maplist.append(block + 14)
#     for i in range(abs((block+14)-(bottom_start-7))):
#         if (block+14)-(bottom_start-7) > 0:
#             maplist.append((bottom_start-7) + (i + 1))
#         else:
#             maplist.append((bottom_start-7) - (i + 1))
#
# for item in maplist:
#     if item not in mapimproved:
#         mapimproved.append(item)
# print(mapimproved)
# print(maplist)

