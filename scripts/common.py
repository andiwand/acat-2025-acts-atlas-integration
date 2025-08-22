import numpy as np
import scipy.stats
import math
import matplotlib.pyplot as plt


markers = ["o", "^", "s", "D"]
colors = ["C0", "C1", "C2", "C3"]


def apply_style():
    SMALL_SIZE = 8
    MEDIUM_SIZE = 10
    BIGGER_SIZE = 12

    plt.rc("font", size=SMALL_SIZE)  # controls default text sizes
    plt.rc("axes", titlesize=SMALL_SIZE)  # fontsize of the axes title
    plt.rc("axes", labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
    plt.rc("xtick", labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc("ytick", labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc("legend", fontsize=SMALL_SIZE)  # legend fontsize
    plt.rc("figure", titlesize=BIGGER_SIZE)  # fontsize of the figure title


def robust_mean(data):
    (m, s), cov = robust_gauss_fit(data)
    return m


def robust_std(data):
    (m, s), cov = robust_gauss_fit(data)
    return s


def robust_std_std(data):
    (m, s), cov = robust_gauss_fit(data)
    return cov[1, 1] ** 0.5


def robust_gauss_fit_naive(data):
    def fit(data):
        return np.mean(data), np.std(data)

    if len(data) == 0:
        return (0, 0), np.zeros((2, 2))

    for _ in range(3):
        m, s = fit(data)
        data = data[np.abs(data - np.median(data)) < 3 * s]

    return (m, s), np.zeros((2, 2))


def robust_gauss_fit(data):
    def fit(data):
        try:
            if len(data) < 20:
                raise ValueError(f"Not enough data to fit a Gaussian: {len(data)}")

            m, s = scipy.stats.norm.fit(data)

            hist_range = (m - 3 * s, m + 3 * s)
            bins = int(math.sqrt(len(data)))
            binned, edges = np.histogram(
                data, range=hist_range, bins=bins, density=True
            )
            centers = 0.5 * (edges[1:] + edges[:-1])

            params, cov = scipy.optimize.curve_fit(
                scipy.stats.norm.pdf, centers, binned, p0=(m, s), maxfev=1000000
            )
        except Exception as e:
            print(f"Falling back to naive mean/std. Error: {e}")
            params, cov = (np.mean(data), np.std(data)), np.zeros((2, 2))

        return params, cov

    (m, s), cov = (0, 0), np.zeros((2, 2))

    for _ in range(3):
        if len(data) == 0:
            return (m, s), cov

        (m, s), cov = fit(data)
        data = data[np.abs(data - m) < 3 * s]

    return (m, s), cov


class TH1:
    def __init__(self, th1_tefficiency, xrange=None):
        try:
            th1 = th1_tefficiency.GetTotalHistogram()
        except:
            th1 = th1_tefficiency

        bins = list(range(1, th1.GetNbinsX() + 1))

        if xrange is not None:
            bins = [
                i
                for i in bins
                if th1.GetBinCenter(i) >= xrange[0] and th1.GetBinCenter(i) <= xrange[1]
            ]

        self.x = np.array([th1.GetBinCenter(i) for i in bins])

        self.x_lo = np.array([th1.GetBinLowEdge(i) for i in bins])
        self.x_width = np.array([th1.GetBinWidth(i) for i in bins])
        self.x_hi = np.add(self.x_lo, self.x_width)
        self.x_err_lo = np.subtract(self.x, self.x_lo)
        self.x_err_hi = np.subtract(self.x_hi, self.x)

        try:
            self.y = np.array([th1_tefficiency.GetEfficiency(i) for i in bins])
            self.y_err_lo = np.array(
                [th1_tefficiency.GetEfficiencyErrorLow(i) for i in bins]
            )
            self.y_err_hi = np.array(
                [th1_tefficiency.GetEfficiencyErrorUp(i) for i in bins]
            )
        except Exception as e:
            self.y = np.array([th1_tefficiency.GetBinContent(i) for i in bins])
            self.y_err_lo = np.array([th1_tefficiency.GetBinError(i) for i in bins])
            self.y_err_hi = np.array([th1_tefficiency.GetBinError(i) for i in bins])

    def errorbar(self, ax, **errorbar_kwargs):
        ax.errorbar(
            self.x,
            self.y,
            yerr=(self.y_err_lo, self.y_err_hi),
            xerr=(self.x_err_lo, self.x_err_hi),
            **errorbar_kwargs,
        )
        return ax

    def step(self, ax, **step_kwargs):
        ax.step(self.x_hi, self.y, **step_kwargs)
        return ax

    def bar(self, ax, **bar_kwargs):
        ax.bar(self.x, height=self.y, yerr=(self.y_err_lo, self.y_err_hi), **bar_kwargs)
        return ax


def ratio_std(x, y, std_x, std_y):
    """
    Calculate the standard deviation of the ratio of two variables x/y.

    Parameters:
    x (float): The first variable.
    y (float): The second variable.
    std_x (float): The standard deviation of the first variable.
    std_y (float): The standard deviation of the second variable.

    Returns:
    float: The standard deviation of the ratio x/y.
    """
    return np.sqrt((std_x / y) ** 2 + (std_y * x / y**2) ** 2)
