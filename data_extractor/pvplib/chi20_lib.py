import os
import numpy
import seaborn
import statsmodels.regression
import statsmodels.tools
import scipy.optimize as opti
import math
import scipy.interpolate as sint
import scipy.signal as ssig
import random

# from make_tex import *
import pandas
import itertools
import matplotlib.pyplot as plt

norm = lambda x: numpy.divide(x, numpy.max(x))

linestyle_tuple = [
    ("solid", "solid"),  # Same as (0, ()) or '-'
    ("dotted", "dotted"),  # Same as (0, (1, 1)) or '.'
    ("dashed", "dashed"),  # Same as '--'
    ("dashdot", "dashdot"),
    ("densely dashdotdotted", (0, (3, 1, 1, 1, 1, 1))),
    ("densely dashed", (0, (5, 1))),
    ("densely dashdotted", (0, (3, 1, 1, 1))),
    ("dashdotdotted", (0, (3, 5, 1, 5, 1, 5))),
]


def interp_filt(
    t,
    x,
    *args,
    _filter={"filtername": "kaiser", "fc": 10, "rdb": 10, "width": 5},
    deriv=2,
    zero_time=True,
):
    #### Accounts for unequal sampling times, by reinterpolating x and y at multiples of the average sampling timeself. Filters the data using the filter: _filter. By default a kaiser window is used with parameters that should work for most movement data, but you can provide any filter by using a dictionnary specifying taps 'b' and 'a', see scipy.signal filtfilt documentation. Also computes naïve derivatives of y up to arbitrary order. This might work only for low derivative orders; stronger low-pass filtering might improve this behavior.

    ## Verify if arrays have been provided
    if type(x) is not numpy.ndarray or type(t) is not numpy.ndarray:
        print("Please Input numpy arrays")
        return -1

    ## For zero time_shift
    t0 = t[0]
    t = t - t0

    # _diff = numpy.diff(t)[numpy.diff(t) < .1]
    # TS = numpy.mean(_diff)
    try:
        TS = args[0]
    except IndexError:
        TS = 1e-2
    interp = sint.interp1d(t, x, fill_value="extrapolate")
    _time = numpy.array([TS * i for i in range(0, int(t[-1] / TS + 1))])

    x_interp = interp(_time)
    if _filter["filtername"] == "kaiser":
        N, beta = ssig.kaiserord(_filter["rdb"], _filter["width"] * 2 * TS)
        taps = ssig.firwin(N, _filter["fc"] * 2 * TS, window=("kaiser", beta))
        filtered_x = ssig.filtfilt(taps, 1, x_interp)
    else:
        b, a = _filter["b"], _filter["a"]
        filtered_x = ssig.filtfilt(b, a, x_interp)
    sig = filtered_x
    if not zero_time:
        _time = _time + t0

    _time = _time.reshape(1, -1)
    sig = sig.reshape(1, -1)
    container = numpy.concatenate((_time, sig), axis=0)

    ## Compute derivatives
    _time = numpy.concatenate(
        (_time, numpy.array([_time[0, -1] + TS]).reshape(1, -1)), axis=1
    )

    for i in range(1, deriv + 1):
        sig = numpy.concatenate((numpy.array([0]).reshape(1, -1), sig), axis=1)
        sig = numpy.divide(numpy.diff(sig), numpy.diff(_time))
        container = numpy.concatenate((container, sig), axis=0)
    return container, TS


class FITTS_single:
    def __init__(self, participant, container_data, container_condition=0):
        self.participant = participant
        self.container = container_data
        if container_condition:
            self.conditions = container_condition
        else:
            self.conditions = [c.condition[1:] for c in container_data]
        self.compute_end_movement(self.end_event)
        self.caption = "Fitts Summary for Participant {}".format(participant)

    # def compute_end_movement(self, func, *args):
    #     print()
    #     end_all = numpy.empty((len(self.container), len(self.container[0].traj_raw)))
    #     conditions_all = numpy.empty((len(self.container), len(self.container[0].traj_raw)))
    #     for nc,container in enumerate(self.container):
    #         end_condition = []
    #         cond_cond = []
    #         ts = container.TS
    #         _cond = self.conditions[nc]
    #         for traj in container.traj_raw:
    #             # print(traj)
    #             timestamps = [ts*i for i in range(len(traj))]
    #             # print(timestamps)
    #             # plt.plot(timestamps, traj , '-')
    #             # plt.show()
    #             # exit()
    #             end_elem = func(timestamps, traj, args)
    #             end_condition.append(end_elem)
    #             cond_cond.append(nc)
    #         end_all[nc,:] = end_condition
    #         conditions_all[nc,:] = cond_cond
    #     self.mt = end_all
    #     self.cond_indx = conditions_all

    def compute_end_movement(self, func, *args):
        mx = max([len(i.traj_raw) for i in self.container])

        end_all = numpy.full([len(self.container), mx], numpy.nan)
        conditions_all = numpy.full([len(self.container), mx], numpy.nan)

        # end_all = []
        # conditions_all = []

        for nc, container in enumerate(self.container):
            end_condition = []
            cond_cond = []
            ts = container.TS
            _cond = self.conditions[nc]
            for traj in container.traj_raw:
                timestamps = [ts * i for i in range(len(traj))]
                end_elem = func(timestamps, traj, args)
                end_condition.append(end_elem)
                cond_cond.append(nc)
            end_all[nc, 0 : len(end_condition)] = end_condition
            conditions_all[nc, 0 : len(cond_cond)] = cond_cond
            # end_all.append(end_condition)
            # conditions_all.append(cond_cond)
        self.mt = numpy.ma.masked_array(end_all, mask=numpy.isnan(end_all))
        self.cond_indx = numpy.ma.masked_array(
            conditions_all, mask=numpy.isnan(conditions_all)
        )

    def subsample(self, sample_number):
        self.sample_number = int(sample_number)
        print("Subsampling {}".format(self.sample_number))
        u = [i for i in range(0, (len(self.conditions)) * (len(self.mt[1])))]
        _indx = random.sample(u, self.sample_number)
        indexes_dim_one = [math.floor(u / len(self.mt[1])) for u in _indx]
        indexes_dim_two = [u % len(self.mt[1]) for u in _indx]
        mt_tmp_index = self.mt[indexes_dim_one, indexes_dim_two]
        cond_tmp_indx = self.cond_indx[indexes_dim_one, indexes_dim_two]
        self.mt = [[] for i in range(len(self.conditions))]
        for n, mt in enumerate(mt_tmp_index):
            self.mt[int(cond_tmp_indx[int(n)])].append(mt)

    def end_event(self, timestamps, traj, *args):
        return timestamps[-1] - timestamps[0]

    def compute_regression(self, print_flag=0):
        MT_container = []
        ID_container = []
        for u, v in zip(self.mt, self.conditions):
            u = u.compressed()
            _id = [float(v[1]) for i in u]
            _mt = [float(i) for i in u]
            ID_container += _id
            MT_container += _mt
        print(ID_container)
        print(MT_container)
        ID_container = statsmodels.tools.add_constant(ID_container)
        model = statsmodels.regression.linear_model.OLS(MT_container, ID_container)
        result = model.fit()
        self.result = result
        if print_flag:
            print(result.summary())

    def make_table_summary(self, latex_path):
        self.get_summary()
        dic = self.dic
        tex_begin_tabular(latex_path, 8, position_str="lrlrlrlr", caption=self.caption)
        tex_add_row_tabular(
            latex_path,
            [
                "",
                "N Obs",
                "df$_r$/df$_m$",
                "$R^2$/R$^2_{adj}$",
                "F/p(F)",
                "log-llh",
                "AIC",
                "BIC",
            ],
        )
        tex_add_row_tabular(
            latex_path,
            [
                "",
                dic["No. Observations"],
                str(dic["df Residuals"]) + "/" + str(dic["df Model"]),
                str(dic["r-squared"]) + "/" + str(dic["Adj. r-squared"]),
                str(dic["F-statistic"]) + "/" + str(dic["Prob (F-statistic)"]),
                dic["Log-likelihood"],
                dic["AIC"],
                dic["BIC"],
            ],
            tol=3,
        )
        tex_add_custom_line(latex_path, "midrule")
        tex_add_row_tabular(
            latex_path,
            ["", "Estimate", "Std Error", "$t$", "p(t)", "CI:", "[0.025", "0.975]"],
            tol=3,
        )
        tex_add_row_tabular(
            latex_path,
            [
                "Intercept",
                dic["Intercept-a"],
                dic["Std Error-a"],
                dic["t-a"],
                dic["P>t-a"],
                "",
                float(dic["CI-a"][0]),
                float(dic["CI-a"][1]),
            ],
            tol=3,
        )
        tex_add_row_tabular(
            latex_path,
            [
                "Slope",
                dic["Slope-b"],
                dic["Std Error-b"],
                dic["t-b"],
                dic["P>t-b"],
                "",
                float(dic["CI-b"][0]),
                float(dic["CI-b"][1]),
            ],
            tol=3,
        )
        tex_end_tabular(latex_path)

    def get_summary(self):
        self.compute_regression()
        result = self.result
        dic = {
            "No. Observations": int(result.nobs),
            "df Residuals": int(result.df_resid),
            "df Model": int(result.df_model),
            "r-squared": float(result.rsquared),
            "Adj. r-squared": float(result.rsquared_adj),
            "F-statistic": float(result.fvalue),
            "Prob (F-statistic)": float(result.f_pvalue),
            "Log-likelihood": float(result.llf),
            "AIC": float(result.aic),
            "BIC": float(result.bic),
            "Intercept-a": float(result.params[0]),
            "Slope-b": float(result.params[1]),
            "Std Error-a": math.sqrt(float(result.cov_params()[0][0])),
            "Std Error-b": math.sqrt(float(result.cov_params()[1][1])),
            ### Cast to float in self.make_table_summary()
            "CI-a": result.conf_int()[0],
            "CI-b": result.conf_int()[1],
            "t-a": float(result.tvalues[0]),
            "t-b": float(result.tvalues[1]),
            "P>t-a": float(result.pvalues[0]),
            "P>t-b": float(result.pvalues[1]),
        }
        self.dic = dic
        return dic

    def plot_fitts(self, ax):
        MT_container = []
        ID_container = []
        for u, v in zip(self.mt, self.conditions):
            _id = [float(v[1]) for i in u]
            MT_container += u.tolist()
            ID_container += _id
        ax.plot(ID_container, MT_container, "o", color="#1f77b4", ms=3)
        seaborn.regplot(ID_container, MT_container, ax=ax)

        MT_container = []
        ID_container = []
        for u, v in zip(self.mt, self.conditions):
            _id = float(v[1])
            mt = numpy.mean(u)
            MT_container.append(mt)
            ID_container.append(_id)
            ax.plot(_id, mt, "o", color="#ff7f0e")


class PVP_container:
    def __init__(self, participant, container_data):
        self.participant = participant
        self.container = container_data
        self.dataframe = self.make_data_frame()

    def make_data_frame(self):
        dataframe = pandas.DataFrame(
            columns=[
                "Participant",
                "D",
                "ID",
                "W",
                "tau",
                "Dtau",
                "sigma0",
                "Omega",
                "C",
                "rsq",
            ]
        )
        for i, container in enumerate(self.container):
            row = [
                self.participant,
                *[float(u) for u in container.condition[1:]],
                container.tau,
                container.Dtau,
                container.sigma_0,
                container.pvp_params[2],
                -container.pvp_params[1],
                container.secondphase_fit.rsquared,
            ]
            dataframe.loc[i] = row
        return dataframe

    def dataframe_to_latex(self, latex_path):
        df = self.dataframe
        tex_begin_tabular(
            latex_path,
            9,
            position_str="rrrrrrrrr",
            caption="Summary of PVP statistics for Participant {}".format(
                self.participant
            ),
        )
        latex_columns = [
            "D\,(mm)",
            "ID",
            "W\,(mm)",
            "$\\tau$\,(s)",
            "D$_{\\tau}$\,(eq. mm)",
            "$\\sigma_0$\,(eq. mm)",
            "$\Omega$\,(s)",
            "C\,(bit/s)",
            "$R^2$",
        ]
        tex_add_row_tabular(latex_path, latex_columns, tol=3)
        tex_add_custom_line(latex_path, "midrule")
        for val in df.values:
            tex_add_row_tabular(latex_path, val[1:], tol=3)
        tex_end_tabular(latex_path)

    def plot_all_pvps(self, ax, labels):
        # nrow = 2
        # ncol = int(math.ceil(len(self.container)/nrow))
        # lstyle = itertools.cycle(linestyle_tuple[::-1])

        for i, container in enumerate(self.container):
            # exec("ax"+str(i)+"=fig.add_subplot("+str(nrow)+str(ncol)+str(i)")")
            y = container.std_prof
            x = container.timestamps
            y = y[: len(x)]
            ax.semilogy(x, y, "-", label=labels[i])


class PVP:
    def __init__(self, condition):
        self.condition = condition
        self.sigma = []
        self.t = []
        self.traj_raw = []
        self.traj = numpy.empty(0)

    def add_2D_traj_raw(self, x, y, t, *args, correct_start="yes"):
        tx, ty = args[1], args[2]
        d = [math.sqrt((u - tx) ** 2 + (v - ty) ** 2) for u, v in zip(x, y)]
        container, TS = interp_filt(
            numpy.array(t),
            numpy.array(d),
            1e-2,
            _filter={"filtername": "kaiser", "fc": 8, "rdb": 10, "width": 5},
            deriv=1,
            zero_time=True,
        )
        self.TS = TS
        if correct_start == "yes":
            container, _ = self.find_start(container, "threshold", 3)
        else:
            pass
        self.traj_raw.append(container[1, :].tolist())

        try:
            self.extend(container[1, :], args[0])
        except IndexError:
            self.extend(container[1, :])

    def add_1D_traj_raw(self, x, t, *args, correct_start="yes"):
        tx = args[1]
        vec = (tx - x[0]) / abs(tx - x[0])
        d = [(tx - u) * vec for u in x]
        container, TS = interp_filt(
            numpy.array(t),
            numpy.array(d),
            1e-2,
            _filter={"filtername": "kaiser", "fc": 8, "rdb": 10, "width": 5},
            deriv=1,
            zero_time=True,
        )
        self.TS = TS
        if correct_start == "yes":
            container, _ = self.find_start(container, "threshold", 3)
        else:
            pass
        self.traj_raw.append(container[1, :].tolist())
        try:
            self.extend(container[1, :], args[0])
        except IndexError:
            self.extend(container[1, :])

    def find_start(self, container, method, *args):
        time = container[0, :]
        traj = container[1, :]
        speed = container[2, :]
        indx = 1
        ms = numpy.max(numpy.abs(speed[1:]))
        if method == "threshold":
            try:
                _threshold = args[0]
            except IndexError:
                _threshold = 1
            while abs(speed[indx]) < ms * _threshold / 100:
                indx += 1

        container = numpy.concatenate(
            (time[indx:].reshape(1, -1), traj[indx:].reshape(1, -1)), axis=0
        )
        container = numpy.concatenate((container, speed[indx:].reshape(1, -1)), axis=0)
        return container, indx

    def extend(self, _traj, *args):
        _traj = _traj.reshape((1, -1))
        if self.traj.shape[0] == 0:
            try:
                _ = args[0]
                while math.ceil(args[0] / self.TS) > _traj.shape[1]:
                    _traj = numpy.append(_traj, _traj[0, -1]).reshape(1, -1)
            except IndexError:
                pass
            self.traj = _traj
        else:
            while self.traj.shape[1] < _traj.shape[1]:
                self.traj = numpy.concatenate(
                    (self.traj, self.traj[:, -1].reshape((-1, 1))), axis=1
                )
            while self.traj.shape[1] > _traj.shape[1]:
                _traj = numpy.append(_traj, _traj[0, -1]).reshape(1, -1)
            self.traj = numpy.concatenate((self.traj, _traj), axis=0)

    def pvp_routine(
        self,
        sigma_away,
        *args,
    ):
        self.compute_timestamps()
        self.compute_profiles()
        if sigma_away:
            self.remove_outliers(sigma_away, *args)

        self.clean_routine(*args)

    def clean_routine(self, *args):
        self.compute_timestamps()
        self.compute_profiles()
        try:
            self.fit_profiles(args[0])
        except IndexError:
            self.fit_profiles()

    def compute_timestamps(self):
        self.timestamps = [self.TS * i for i in range(self.traj.shape[1])]

    def compute_profiles(self):
        self.mean_prof = numpy.mean(self.traj, axis=0)
        self.std_prof = numpy.std(self.traj, axis=0)
        # fig = plt.figure()
        # ax = fig.add_subplot(111)
        # for i in self.traj:
        #     ax.plot(i)
        # plt.show()

    def fit_profiles(self, *args):
        ### Leave availability for user to specify parameters for the global optimizer
        try:
            n_iter = args[0]
        except IndexError:
            n_iter = 50

        ### Define cost function for optimization procedure
        def monospline(THETA, *args):
            x = args[0]
            y = args[1]
            a, b, mt = THETA
            out = 0
            for i, v in enumerate(x):
                if v < mt:
                    out += (a + b * v - y[i]) ** 2
                else:
                    out += (a + b * mt - y[i]) ** 2
            return out

        def get_fit_second_phase(y, indx_omega):
            ## Once Omega has been determined, run a classical linear regression on the second phase to get some parameters more easily
            x = [self.TS * i for i in range(indx_omega)]
            yy = y[:indx_omega]
            xx = statsmodels.tools.add_constant(x)
            model = statsmodels.regression.linear_model.OLS(yy, xx)
            result = model.fit()
            self.secondphase_fit = result

        self.get_profile_params()

        ### Initialize optimization algorithm - Data and start parameters

        indx_tau = self.tau_index
        theta0 = [self.sigma_0, -5, 1]
        if indx_tau:
            x = self.timestamps[0:-indx_tau]
            y = numpy.log2(self.std_prof[indx_tau:])
        else:
            x = self.timestamps
            y = numpy.log2(self.std_prof)

        ## Global Optimization

        res = opti.basinhopping(
            func=monospline,
            x0=theta0,
            niter=n_iter,
            minimizer_kwargs={
                "method": "Nelder-Mead",
                "args": (x, y),
                "options": {"maxiter": 1000, "disp": 0},
            },
        )

        a, b, c = res.x
        c0 = math.ceil(c / self.TS)
        self.omega = c
        get_fit_second_phase(y, c0)
        a, b = self.secondphase_fit.params
        _yy = [a + b * i * self.TS for i in range(0, c0)] + [
            a + c * b for i in range(c0, len(y[indx_tau:]))
        ]
        _yy = [2 ** v for v in _yy]
        t_abs = [self.tau + i * self.TS for i in range(0, len(_yy))]
        self.pvp_x = t_abs
        self.pvp_y = _yy
        self.pvp_params = [a, b, c + self.tau]

    def get_profile_params(self):
        self.tau_index = numpy.argmax(self.std_prof)
        self.tau = self.tau_index * self.TS
        self.sigma_0 = numpy.max(self.std_prof)
        # self.Dtau = self.condition[1] - self.mean_prof[self.tau_index]
        self.Dtau = self.mean_prof[self.tau_index]

    ### Print/plot whatever you like
    def _print(self):
        print(self.traj.shape)

    def _print_pvp_params(self):
        print(self.tau, self.sigma_0, self.Dtau)

    def plot_traj_raw(self, ax):
        for v in self.traj_raw:
            _abs = [self.TS * i for i in range(len(v))]
            ax.plot(_abs, v, "-", color="#1f77b4")

    def plot_traj_extend(self, ax):
        _abs = [self.TS * i for i in range(self.traj.shape[1])]
        for v in range(self.traj.shape[0]):
            ax.plot(_abs, self.traj[v, :].tolist(), "-", lw=1, color="#1f77b4")

    def plot_stdprofiles(self, ax, fit=1):
        y = self.std_prof
        _abs = self.timestamps
        ax.semilogy(_abs, y, "k-", lw=3, label="PVP")
        if fit:
            ax.semilogy(self.pvp_x, self.pvp_y, "r-", lw=3, label="Spline fit")
        ax.grid(b=True, which="minor", linestyle="--")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel(r"$\sigma(t) (m)$")
        # ax.set_ylim([0.9,5e2])

    def subsample_routine(self, sample_number, pvprout_args):
        self.sample_number = int(sample_number)
        # print("Subsampling {}".format(self.sample_number))
        indexes = random.sample(range(self.traj.shape[0]), self.sample_number)
        self.traj = self.traj[indexes, :]
        self.pvp_routine(*pvprout_args)

    def remove_outliers(self, sigma_away, *args):
        k = 0
        j = 0
        while k < len(self.traj):
            traj = self.traj[k, :]
            cpt = 0
            for ns, sample in enumerate(traj):
                if abs(sample - self.mean_prof[ns]) > sigma_away * self.std_prof[ns]:
                    cpt += 1
                if cpt > 5:
                    self.traj = numpy.delete(self.traj, k, axis=0)
                    k = 0
                    j += 1
                    break
            k += 1
        self.removed = j


class PVP_Reverse(PVP):
    def __init__(self, condition):
        super().__init__(condition)

    def add_2D_traj_raw(self, x, y, t, *args, correct_start="yes"):
        d = [math.sqrt((u - x[0]) ** 2 + (v - y[0]) ** 2) for u, v in zip(x, y)]
        container, TS = interp_filt(
            numpy.array(t),
            numpy.array(d),
            _filter={"filtername": "kaiser", "fc": 8, "rdb": 10, "width": 5},
            deriv=1,
            zero_time=True,
        )
        self.TS = TS
        if correct_start == "yes":
            container, _ = self.find_start(container, "threshold", 5)
        else:
            pass
        self.traj_raw.append(container[1, :].tolist())

        try:
            self.extend(container[1, :], args[0])
        except IndexError:
            self.extend(container[1, :])


class PVP_Project(PVP):
    def __init__(self, condition):
        super().__init__(condition)

    def add_2D_traj_raw_x(self, x, y, t, *args, correct_start="yes"):
        tx, ty = args[1], args[2]
        vec = [tx - x[0], ty - y[0]]
        norm_vector = math.sqrt(vec[0] ** 2 + vec[1] ** 2)
        dir_mov = [vec[0] / norm_vector, vec[1] / norm_vector]
        _proj = [(tx - u) * dir_mov[0] + (ty - v) * dir_mov[1] for u, v in zip(x, y)]
        container, TS = interp_filt(
            numpy.array(t),
            numpy.array(_proj),
            _filter={"filtername": "kaiser", "fc": 8, "rdb": 10, "width": 5},
            deriv=1,
            zero_time=True,
        )
        self.TS = TS
        if correct_start == "yes":
            container, _ = self.find_start(container, "threshold", 3)
        else:
            pass
        self.traj_raw.append(container[1, :].tolist())

        try:
            self.extend(container[1, :], args[0])
        except IndexError:
            self.extend(container[1, :])

    def add_2D_traj_raw_y(self, x, y, t, *args, correct_start="yes"):
        tx, ty = args[1], args[2]
        vec = [-(ty - y[0]), tx - x[0]]
        norm_vector = math.sqrt(vec[0] ** 2 + vec[1] ** 2)
        dir_mov = [vec[0] / norm_vector, vec[1] / norm_vector]
        _proj = [(tx - u) * dir_mov[0] + (ty - v) * dir_mov[1] for u, v in zip(x, y)]
        container, TS = interp_filt(
            numpy.array(t),
            numpy.array(_proj),
            _filter={"filtername": "kaiser", "fc": 8, "rdb": 10, "width": 5},
            deriv=1,
            zero_time=True,
        )
        self.TS = TS
        if correct_start == "yes":
            container, _ = self.find_start(container, "threshold", 3)
        else:
            pass
        self.traj_raw.append(container[1, :].tolist())

        try:
            self.extend(container[1, :], args[0])
        except IndexError:
            self.extend(container[1, :])


class PVP_Centroid(PVP):
    def __init__(self, condition):
        super().__init__(condition)
        self.traj_raw_x = []
        self.traj_raw_y = []
        self.traj_raw = []
        self.traj_x = numpy.array([])
        self.traj_y = numpy.array([])

    def add_2D_traj_raw(self, x, y, t, *args, correct_start="yes"):
        d = [math.sqrt((u - x[0]) ** 2 + (v - y[0]) ** 2) for u, v in zip(x, y)]
        container, TS = interp_filt(
            numpy.array(t),
            numpy.array(d),
            _filter={"filtername": "kaiser", "fc": 8, "rdb": 10, "width": 5},
            deriv=1,
            zero_time=True,
        )
        _projx = self.get_proj_x(x, y, t, *args, correct_start="yes")
        _projy = self.get_proj_y(x, y, t, *args, correct_start="yes")

        containerx, TS = interp_filt(
            numpy.array(t),
            numpy.array(_projx),
            TS,
            _filter={"filtername": "kaiser", "fc": 8, "rdb": 10, "width": 5},
            deriv=1,
            zero_time=True,
        )
        containery, TS = interp_filt(
            numpy.array(t),
            numpy.array(_projy),
            TS,
            _filter={"filtername": "kaiser", "fc": 8, "rdb": 10, "width": 5},
            deriv=1,
            zero_time=True,
        )
        self.TS = TS
        if correct_start == "yes":
            containerx, indx = self.find_start(containerx, "threshold", 5)
            containery, indx = self.find_start(containery, "threshold", 5)
        else:
            indx = 0
        self.traj_raw_x.append(containerx[1, indx:].tolist())
        self.traj_raw_y.append(containery[1, indx:].tolist())
        self.traj_raw.append(containerx[1, indx:].tolist())
        try:
            self.traj_x = self.extend(self.traj_x, containerx[1, :], args[0])
            self.traj_y = self.extend(self.traj_y, containery[1, :], args[0])
        except IndexError:
            self.traj_x = self.extend(self.traj_x, containerx[1, :])
            self.traj_y = self.extend(self.traj_y, containery[1, :])

    def get_proj_x(self, x, y, t, *args, correct_start="yes"):
        tx, ty = args[1], args[2]
        vec = [tx - x[0], ty - y[0]]
        norm_vector = math.sqrt(vec[0] ** 2 + vec[1] ** 2)
        dir_mov = [vec[0] / norm_vector, vec[1] / norm_vector]
        _proj = [(tx - u) * dir_mov[0] + (ty - v) * dir_mov[1] for u, v in zip(x, y)]
        return _proj

    def get_proj_y(self, x, y, t, *args, correct_start="yes"):
        tx, ty = args[1], args[2]
        vec = [-(ty - y[0]), tx - x[0]]
        norm_vector = math.sqrt(vec[0] ** 2 + vec[1] ** 2)
        dir_mov = [vec[0] / norm_vector, vec[1] / norm_vector]
        _proj = [(tx - u) * dir_mov[0] + (ty - v) * dir_mov[1] for u, v in zip(x, y)]
        return _proj

    def extend(self, trajs, _traj, *args):
        _traj = _traj.reshape((1, -1))
        if trajs.shape[0] == 0:
            try:
                _ = args[0]
                while math.ceil(args[0] / self.TS) > _traj.shape[1]:
                    _traj = numpy.append(_traj, _traj[0, -1]).reshape(1, -1)
            except IndexError:
                pass
            return numpy.array(_traj)
        else:
            while trajs.shape[1] < _traj.shape[1]:
                trajs = numpy.concatenate(
                    (trajs, trajs[:, -1].reshape((-1, 1))), axis=1
                )
            while trajs.shape[1] > _traj.shape[1]:
                _traj = numpy.append(_traj, _traj[0, -1]).reshape(1, -1)
        return numpy.concatenate((trajs, _traj), axis=0)

    def compute_profiles(self):
        self.mean_prof_x = numpy.mean(self.traj_x, axis=0)
        self.mean_prof_y = numpy.mean(self.traj_y, axis=0)
        self.mean_prof = self.mean_prof_x + self.mean_prof_y
        self.std_prof_x = numpy.std(self.traj_x, axis=0)
        self.std_prof_y = numpy.std(self.traj_y, axis=0)
        self.std_prof = numpy.sqrt(
            numpy.square(self.std_prof_x) + numpy.square(self.std_prof_y)
        )

    def plot_traj_extend(self, ax1, ax2):
        self.plot_traj_extend_x(ax1)
        self.plot_traj_extend_y(ax2)

    def plot_traj_extend_x(self, ax):
        _abs = [self.TS * i for i in range(self.traj_x.shape[1])]
        for v in range(self.traj_x.shape[0]):
            ax.plot(_abs, self.traj_x[v, :].tolist(), "-", color="#1f77b4")

    def plot_traj_extend_y(self, ax):
        _abs = [self.TS * i for i in range(self.traj_y.shape[1])]
        for v in range(self.traj_y.shape[0]):
            ax.plot(_abs, self.traj_y[v, :].tolist(), "-", color="#1f77b4")

    def compute_timestamps(self):
        self.timestamps = [self.TS * i for i in range(self.traj_x.shape[1])]

    def remove_outliers(self, sigma_away, *args):
        k = 0
        j = 0
        while k < len(self.traj_x):
            traj = self.traj_x[k, :]
            cpt = 0
            for ns, sample in enumerate(traj):
                if (
                    abs(sample - self.mean_prof_x[ns])
                    > sigma_away * self.std_prof_x[ns]
                ):
                    cpt += 1
                if cpt > 5:
                    self.traj_x = numpy.delete(self.traj_x, k, axis=0)
                    self.traj_y = numpy.delete(self.traj_y, k, axis=0)
                    k = 0
                    j += 1
                    break
            k += 1
        self.removed = j
        k = 0
        j = 0
        while k < len(self.traj_y):
            traj = self.traj_y[k, :]
            cpt = 0
            for ns, sample in enumerate(traj):
                if (
                    abs(sample - self.mean_prof_y[ns])
                    > sigma_away * self.std_prof_y[ns]
                ):
                    cpt += 1
                if cpt > 5:
                    self.traj_x = numpy.delete(self.traj_x, k, axis=0)
                    self.traj_y = numpy.delete(self.traj_y, k, axis=0)
                    k = 0
                    j += 1
                    break
            k += 1
        self.removed += j


class PVP_det(PVP_Centroid):
    def __init__(self, condition):
        super().__init__(condition)

    def compute_profiles(self):
        self.mean_prof_x = numpy.mean(self.traj_x, axis=0)
        self.mean_prof_y = numpy.mean(self.traj_y, axis=0)

        self.mean_prof = self.mean_prof_x + self.mean_prof_y

        self.std_prof_x = numpy.std(self.traj_x, axis=0)
        self.std_prof_y = numpy.std(self.traj_y, axis=0)

        self.std_prof = []
        self.cross_cov = []
        self.norm_cross_cov = []
        for i, v in enumerate(self.traj_x[1, :]):
            X = self.traj_x[:, i]
            Y = self.traj_y[:, i]
            cov = numpy.cov(X, Y)
            det = cov[0, 0] * cov[1, 1] - cov[0, 1] ** 2
            self.std_prof.append(math.sqrt(math.sqrt(det)))
            self.cross_cov.append(cov[0, 1])
            self.norm_cross_cov.append(cov[0, 1] ** 2 / cov[0, 0] / cov[1, 1])

    ########### enelever routines dessous

    #
    # def pvp_routine(self, sigma_away, *args,):
    #     self.compute_timestamps()
    #     self.compute_profiles()
    #     if sigma_away:
    #         self.remove_outliers(sigma_away, *args)
    #
    #     self.compute_profiles()
    #
    # def plot_stdprofiles(self, ax):
    #     y = self.std_prof
    #     _abs = self.timestamps[:len(y)]
    #     ax.semilogy(_abs, y, 'k-', lw = 3)
    #     ax.grid(b=True, which='minor', linestyle='--')
    #     ax.set_xlabel("Time (s)")
    #     ax.set_ylabel(r"$\sigma(t) (m)$")
    # ax.set_ylim([0.9,5e2])

    # # self.nmovs = len(self.traj_x[0,:])
    # # self.cross_cov = [1/self.nmovs*numpy.correlate(self.traj_x[i,:], self.traj_y[i,:], 'same') for i,v in enumerate(self.traj_x[:,1])]
    # self.var_prof_x = numpy.var(self.traj_x, axis = 0)
    # self.var_prof_y = numpy.var(self.traj_y, axis = 0)
    # # print(self.var_prof_x.shape, self.var_prof_y.shape, self.cross_cov.shape)
    # # self.std_prof = numpy.sqrt(numpy.multiply(self.var_prof_x, self.var_prof_y)-numpy.square(self.cross_cov))
    # self.std_prof = numpy.sqrt(numpy.multiply(self.var_prof_x, self.var_prof_y))


_normalize = lambda x: numpy.divide(x - numpy.mean(x), numpy.std(x))
norm_max = lambda x: numpy.divide(x, numpy.max(x))


def multitraj_get_movs(position, trim=[0, 0]):
    normpos = _normalize(position)
    indx = numpy.array([i for i in range(0, len(normpos))])

    indx_output = []
    _sign = math.copysign(1, normpos[0])
    for k, v in enumerate(normpos):
        new_sign = math.copysign(1, v)
        if new_sign * _sign == -1:
            indx_output.append(k)
        else:
            pass
        _sign = new_sign

    output = indx[indx_output]

    if trim[0]:
        output = output[trim[0] :]
    if trim[1]:
        output = output[: -trim[1]]
    return output


def multitraj_get_starts(
    timestamps, position, speed, threshold=1e-2, multitraj_type="both"
):
    def get_start(
        mov_indx, timestamps, nposition, nspeed, threshold=1e-2, multitraj_type="both"
    ):
        idx = mov_indx
        speed = norm_max(nspeed)
        while abs(speed[idx]) > threshold:
            idx += -1
        ### verify some conditions
        return idx

    output = []
    _pos = _normalize(position)
    _spd = _normalize(speed)
    _movs = multitraj_get_movs(_pos)
    for mov_indx in _movs:
        if multitraj_type == "ascending" and _spd[mov_indx] > 0:
            output.append(
                get_start(
                    mov_indx,
                    timestamps,
                    position,
                    speed,
                    threshold=1e-2,
                    multitraj_type=multitraj_type,
                )
            )
        elif multitraj_type == "descending" and _spd[mov_indx] < 0:
            output.append(
                get_start(
                    mov_indx,
                    timestamps,
                    position,
                    speed,
                    threshold=1e-2,
                    multitraj_type=multitraj_type,
                )
            )
        elif multitraj_type == "both":
            output.append(
                get_start(
                    mov_indx,
                    timestamps,
                    position,
                    speed,
                    threshold=1e-2,
                    multitraj_type=multitraj_type,
                )
            )
    return output


def get_stop(timestamps, pos, speed, _thresh=1e-2):
    ### Stop points
    # Score is based on the longest dwell period
    #
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # ax.plot(timestamps, pos, '-')

    threshold = lambda signal: [x if abs(x) > _thresh else 0 for x in signal]

    vthresh = threshold(speed)
    indx = 0
    # First zero crossing
    while vthresh[indx] == 0:
        indx += 1
    try:
        while vthresh[indx] != 0:
            indx += 1
    except IndexError:
        return len(pos), len(pos), len(pos), len(pos), len(pos), len(pos), []

    first_zero = indx
    # ax.plot(timestamps[first_zero], pos[first_zero], '*')

    tmp_start = indx
    tmp_stop = len(pos)
    plateau = vthresh[tmp_start:tmp_stop]
    Dwell = False
    plateaux = []
    for nu, u in enumerate(plateau[:-1]):
        if u == 0 and plateau[nu + 1] == 0 and plateau[nu - 1] == 0 and Dwell == False:
            a = nu + tmp_start
            Dwell = True
        elif u != 0 and Dwell == True:
            b = nu + tmp_start
            Dwell = False
            if (timestamps[b] - timestamps[a]) > 30e-3:
                plateaux.append([a, b])
            else:
                pass
        else:
            pass

    try:
        last_dwell_begin = plateaux[-1][0]
        last_dwell_mid = int((plateaux[-1][1] + plateaux[-1][0]) / 2)
        last_dwell_end = plateaux[-1][1]
        first_dwell_mid = int((plateaux[0][1] + plateaux[0][0]) / 2)

        tmp = 0
        for a, b in plateaux:
            _dist = b - a
            if _dist > tmp:
                tmp = _dist
                out = int(a + _dist / 2)
        mid_longest_dwell = out

    except IndexError:
        last_dwell_begin = first_zero
        last_dwell_mid = first_zero
        last_dwell_end = first_zero
        first_dwell_mid = first_zero
        mid_longest_dwell = first_zero
        plateaux = []

    # plt.show()
    # plt.close()
    return (
        first_zero,
        last_dwell_begin,
        last_dwell_mid,
        last_dwell_end,
        first_dwell_mid,
        mid_longest_dwell,
        plateaux,
    )
