def disassemble(v):
  vlst = []
  while (v > 0):
    if (v < 1):
      vlst.append(v)
    else:
      vlst.append(1)
    v = v - 1
  return vlst
