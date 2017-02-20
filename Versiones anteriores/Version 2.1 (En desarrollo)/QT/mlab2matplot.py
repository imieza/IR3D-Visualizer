import numpy as np
from mayavi import mlab
import matplotlib.pyplot as plt
# set up some plotting params
dphi, dtheta = np.pi / 250.0, np.pi / 250.0
[phi, theta] = np.mgrid[0:np.pi + dphi * 1.5:dphi,
                        0:2 * np.pi + dtheta * 1.5:dtheta]
m0, m1, m2, m3 = 4, 3, 2, 3
m4, m5, m6, m7 = 6, 2, 6, 4
r = np.sin(m0 * phi) ** m1 + np.cos(m2 * phi) ** m3 + \
    np.sin(m4 * theta) ** m5 + np.cos(m6 * theta) ** m7
x = r * np.sin(phi) * np.cos(theta)
y = r * np.cos(phi)
z = r * np.sin(phi) * np.sin(theta)
# do the meshplot
fig = mlab.figure(size=(480, 340))
mlab.mesh(x, y, z, colormap='cool')
imgmap = mlab.screenshot(mode='rgba', antialiased=False)
plt.imsave(arr=imgmap, fname="foo.png")

mlab.show()
# do the matplotlib plot
fig2 = plt.figure(figsize=(7, 5))
plt.imshow(imgmap, zorder=4)
plt.plot(np.arange(0, 480), np.arange(480, 0, -1), 'r-')
plt.savefig('example.png')
