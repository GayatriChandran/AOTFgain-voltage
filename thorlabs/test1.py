import numpy

wl = 460
mappings = [[561, 1, 7023] , [488, 2, 12873] , [460, 3, 6633]]
search = wl
for (wav, ch, amp) in mappings:
    if wav == wl:
        channel = ch
        rfamp = amp
    else :
        pass
print("Channel = ", channel)
print("Amplitude = ", rfamp)

for i in range(0,11 ):
    print(i)


