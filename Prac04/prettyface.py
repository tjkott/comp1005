#
# prettyface.py
#
import matplotlib.pyplot as plt
from skimage import data    

face = data.camera()  # Load a sample image from skimage
plt.imshow(face, cmap=plt.cm.gray)
plt.show()