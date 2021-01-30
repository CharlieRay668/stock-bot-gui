import numpy as np
import matplotlib.pyplot as plt
from TDRestAPI import Rest_Account
from price_probability_distobution import get_pdfs_from_deltas
from scipy.optimize import curve_fit, minimize
from scipy import stats
from datetime import datetime, timedelta
import time

acc = Rest_Account("keys.json")

# S0 = 36.0
# T = 1.0
# r = 0.06
# sigma = 0.2

# def mcs_simulation(intervals, paths):
#     M, I = intervals, paths

#     dt = T/M
#     S = np.zeros((M+1, I))
#     S[0] = np.ones(I) * S0
#     rn = np.random.standard_normal(S.shape)
#     for t in range(1, M+1):
#         S[t, :] = S[t-1, :] * np.exp((r - sigma**2/2) * dt + sigma * np.sqrt(dt) * rn[t, :])
#     return S

# S = mcs_simulation(100, 50000)
# print(S[-1].mean())
# plt.hist(S[-1], bins=100)
# plt.show()
# exit()


def mean_line(x, m, b):
    return m * x + b

def std_line(x, m, b, c):
    return m * x**c + b

def get_position_string(ticker, strike, expiration, side):
    """ When a trader makes a trade call this function to get a
    position string. Give this position string to get_score_percent
    when this position is closed.

    Captures the current market projection for the given ticker. The position
    string is used to look back on a trade and determine odds that a trader
    was able to achieve their level of returns or better.

    Args:
        ticker (str): Ticker of the underlying asset
        strike (float): Strike price of the option contract
        expiration (datetime.Datetime): Expiration date of the option contract
        side ("C" or "P"): Call or Put. "C" for Call, "P" for Put

    Returns:
        String: Position string to be given to get_score_percent when the
        position is closed
    """

    from_date = datetime.now()
    to_date = from_date + timedelta(days=80)
    mark = acc.get_quotes([ticker])["mark"].iloc[0]

    options_data = acc.get_options_chain(ticker, from_date, to_date, strike_count=50)
    if options_data is None:
        return

    # last_query_time = time.time()
    print("[%s]" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Calculating PDF for", ticker, flush=True)
    pdfs = get_pdfs_from_deltas(options_data, distribution=stats.norm)
    if len(pdfs.keys()) == 1:
        print(ticker, " doesn't have weekly expirations")
        return
    
    days = []
    means = []
    mean_errs = []
    stds = []
    std_errs = []
    total_err = 0
    for label in pdfs:
        u, s, errs = pdfs[label]
        if np.isnan(u) or np.isnan(s):
            continue
        err = 100 * np.linalg.norm(errs / (u, s))
        total_err += err
        means.append(u)
        mean_errs.append(errs[0])
        stds.append(s)
        std_errs.append(errs[1])

        expiration = datetime.strptime(label, "%Y-%m-%d")
        today = datetime.now()
        today = datetime(today.year, today.month, today.day)
        days.append((expiration - today).days)

    print(total_err)
    if total_err / len(pdfs) > 20:
        print("Too much error in", ticker)
        return


    days = np.array(days)
    means = np.array(means)
    stds = np.array(stds)
    mean_opts, mean_cov = curve_fit(mean_line, days, means, p0=(1, mark), bounds=((-np.inf, 0), (np.inf, np.inf)), sigma=stds)
    mean_m, mean_b = mean_opts

    # if pcov[0][0] == np.nan:
    # import matplotlib.pyplot as plt
    # plt.scatter(days, means)
    # plt.show()
    # mean_line_errs = np.sqrt(np.diag(mean_cov))

    std_opts, std_cov = curve_fit(std_line, days, stds, p0=(1, 0, 0.5), bounds=((-np.inf, -np.inf, 0), (np.inf, np.inf, 1)), sigma=std_errs)
    std_m, std_b, std_c = std_opts

    # std_line_errs = np.sqrt(np.diag(std_cov))

    values = [mean_m, mean_b, std_m, std_b, std_c, datetime.now().strftime("%y-%m-%d %H:%M:%S")]
    return ",".join(map(str, values))

    # u = mean_line(1, mean_m - mean_line_errs[0], mean_b - mean_line_errs[1])
    # s = std_line(1, std_m + std_line_errs[0], std_b + std_line_errs[1], std_c + std_line_errs[2])

    # profile = {}
    # profile["ticker"] = ticker
    # profile["time"] = int(time.time())
    # profile["share_price"] = mark
    # profile["mean"] = u
    # profile["std"] = s
    # profile["err_mean"] = np.sqrt(np.abs(np.sum(np.diag(mean_cov) / mean_opts)))
    # profile["err_std"] = np.sqrt(np.abs(np.sum(np.diag(std_cov) / std_opts)))
    # # s_sign = 1 if u > mark else -1
    # # loss_odds_max = quad(lambda x: stats.norm.pdf(x, u-errs[0], s + errs[1]*s_sign), 0, mark)[0]
    # # profit_odds = 1 - stats.norm.cdf(mark, u, s)
    # profile["sort_key"] = (u / mark) / s


def get_score_percent(position_string, share_price):
    """ Calculates the percent of hypothetical traders that
    would have had the same or higher returns given what the market
    knew when the position was entered

    Args:
        position_string ([type]): [description]
        share_price ([type]): [description]

    Returns:
        [type]: [description]
    """
    strings = position_string.split(",")
    mean_m, mean_b, std_m, std_b, std_c = map(float, strings[:-1])
    date = datetime.strptime(strings[-1], "%y-%m-%d %H:%M:%S")

    days = (datetime.now() - date).total_seconds() / (60*60*24)
    print(days)

    u = mean_line(days, mean_m, mean_b)
    s = std_line(days, std_m, std_b, std_c)

    return 1-stats.norm.cdf(share_price, u, s)


string = get_position_string("TSLA", None, None, None)
print(string)
print(get_score_percent(string, 880))
