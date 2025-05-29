import mapplotlib.pyplot as plt
from scipy import ndimage
from scipy import miscface = misc.face(gray=True)
plt.imshow(face, cmap=plt.cm.gray)
plt.show()

