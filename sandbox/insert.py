

# a = [0, 1, 2, 3, 4, 5, 6]
# c = len(a)
# a[3:0] = ['end']
# print(a)

# a[i:i] indsætter mellem i - 1 og i
# a[i:i+1] erstatter i

a = [
    (0, 'a'),
    (3, 'b'),
    (2, 'c'),
    (1, 'd'),
    (4, 'e'),
]

a.sort(key=lambda t: t[0])
print(a)

