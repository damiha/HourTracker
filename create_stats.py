import matplotlib.pyplot as plt
import numpy as np
import os
import time

plt.rcParams["figure.figsize"] = (8,6)

save_destination = "static/stats_images"

def save_empty_image_at(filename, title):
    plt.clf()
    plt.title(title)
    plt.text(0.25, 0.5, "No stats available", fontsize=25)
    plt.savefig(f"{save_destination}/{filename}")

def create_hours_today(categories, title):

    # can't create stats when no categories were added that day
    # old stats images have to be deleted since they are out of date
    if len(categories) == 0:
        save_empty_image_at("hours_worked_today.png", title)
        return
    
    category_names = list(map(lambda c: c["name"], categories))
    hours_list = list(map(lambda c: c["hours"], categories))

    hours_per_category = list(map(lambda h: np.sum(np.array(h)), hours_list))

    x_pos = np.arange(len(category_names))

    hours_cumulated = np.array(hours_per_category)

    # yscale should always be from [0, 10] hours (except when needed more)
    ymax = max(10, np.max(hours_cumulated))

    # delete old version of file
    #os.remove(f"{save_destination}/hours_worked_today.png")
    plt.clf()
    plt.title(title)
    plt.bar(x_pos, hours_cumulated, align="center", color="steelblue")
    plt.xticks(x_pos, category_names)
    plt.yticks(np.linspace(0, ymax, ymax + 1))
    plt.savefig(f"{save_destination}/hours_worked_today.png")