from matplotlib import pyplot as plt

def draw_figure(improvements):
    plt.title("Retweet Prediction Performance")
    plt.xlabel("Improvement over baseline in percentage (%)")
    plt.ylabel("Number of users")
    plt.hist(improvements)
    plt.figtext(0.64, 0.85, 'No. of users: 1', fontsize=8)
    plt.figtext(0.64, 0.83, 'No. of folds: 10', fontsize=8)
    plt.figtext(0.64, 0.81, 'Average improvements: 59%', fontsize=8)

    plt.show()

    # plt.savefig("performance.png")