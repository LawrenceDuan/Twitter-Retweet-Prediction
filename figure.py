from matplotlib import pyplot as plt
from time import gmtime, strftime

def draw_figure(improvements, a, b, c):
    plt.title("Retweet Prediction Performance")
    plt.xlabel("Improvement over baseline in percentage (%)")
    plt.ylabel("Number of users")
    plt.hist(improvements)
    plt.figtext(0.64, 0.85, 'No. of users: ', fontsize=8)
    plt.figtext(0.76, 0.85, a, fontsize=8)
    plt.figtext(0.64, 0.83, 'No. of folds: ', fontsize=8)
    plt.figtext(0.76, 0.83, b, fontsize=8)
    plt.figtext(0.64, 0.81, 'Average improvements: ', fontsize=8)
    plt.figtext(0.70, 0.79, c, fontsize=8)

    # plt.show()

    current_time = strftime("%Y%m%d %H%M%S", gmtime())


    plt.savefig("performance " + current_time + ".png")