import matplotlib.pyplot as plt
import numpy as np

def quicklook(x,y,data, dd=100, xlim=None, ylim=None, vmin=8, vmax=38, vn=11, fig=None, ax=None, show=False):
    x_ql = x[::dd,::dd]
    y_ql = y[::dd,::dd]
    data_ql = 10*np.log10(data[::dd,::dd])
    #print(np.max(data), np.min(data))
    lmin = np.min(data) if vmin is None else  vmin
    lmax = np.max(data) if vmax is None  else vmax
    levels = np.linspace(lmin, lmax, vn, endpoint=True)
    if (fig is None) and (ax is None):
        show=True
        fig, ax = plt.subplots(1,1, figsize=(8,5))
    im = ax.contourf(x_ql,y_ql,data_ql, levels, cmap="gist_earth")
    #im = ax.contourf(np.log10(data_ql), levels, cmap="gist_earth")
    cbar = fig.colorbar(im)#, label='dB', labelpad=-40, y=1.05, rotation=0
    cbar.ax.set_title('dB')
    ax.axis('equal')
    if xlim is not None:
        ax.set_xlim(xlim[0], xlim[1])
    if ylim is not None:
        ax.set_ylim(ylim[0], ylim[1])
    if show:
        plt.show()
