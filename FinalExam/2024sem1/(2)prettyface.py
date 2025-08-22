import matplotlib.pyplot as plt
from scipy import ndimage
from scipy import datasets

face = datasets.face(gray=True)
cropped_face = face[100:400, 100:400]  # Crop the face image
plt.imshow(face, cmap=plt.cm.gray)
plt.show()