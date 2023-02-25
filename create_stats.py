import matplotlib.pyplot as plt
import numpy as np
import os
import time
from datetime import date, timedelta

plt.rcParams["figure.figsize"] = (8,6)

save_destination = "static/stats_images"

def save_empty_image_at(filename, title):
    plt.clf()
    plt.title(title)
    plt.text(0.25, 0.5, "No stats available", fontsize=25)
    plt.savefig(f"{save_destination}/{filename}")

# categories = a dict that represents a days work
def get_total_hours(categories):
    total_hours = 0
    for category in categories:
        total_hours += sum(category["hours"])
    return total_hours

def get_past_records(records, number_of_days):

    categories_past = []
    days = []

    for i in range(number_of_days):
        day = date.today() - timedelta(days=i)
        
        # only append short string for visualization
        days.insert(0, day.strftime("%d/%m"))
        day = day.strftime("%d/%m/%Y")

        if records.count_documents({"date": day}) == 1:
            category_that_day = records.find({"date" : day})[0]["categories"]
            categories_past.insert(0, category_that_day)
        else:
            categories_past.insert(0, [])

    return days, categories_past

def create_hours_last_week(records, title):

    # query the database for the last days (max 7 days) including today
    days, categories_past_week = get_past_records(records, number_of_days=7)

    hours_past_week = list(map(lambda c: get_total_hours(c), categories_past_week))

    xpos = np.arange(len(hours_past_week))
    ymax = max(np.max(np.array(hours_past_week)), 10)

    plt.clf()
    plt.title(title)
    plt.bar(xpos, hours_past_week, color="steelblue", align="center")
    plt.xticks(xpos, days)
    plt.yticks(np.linspace(0, ymax, ymax + 1))
    plt.savefig(f"{save_destination}/hours_last_week.png")


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

def get_hours_per_category(categories_past):

    hours_per_category = dict()

    for categories in categories_past:
        for category in categories:
            added_hours = sum(category["hours"])
            cat_name = category["name"]
            hours_per_category[cat_name] = hours_per_category.get(cat_name, 0) + added_hours

    return hours_per_category

def create_work_distribution_last_week(records, title):
    
    days, categories_past_week = get_past_records(records, number_of_days=7)

    hours_per_category = get_hours_per_category(categories_past_week)
    
    labels = hours_per_category.keys()
    hours_per_category = hours_per_category.values()
    hours_in_total = sum(hours_per_category)

    if hours_in_total == 0:
        save_empty_image_at("work_distribution_last_week.png", title)
        return

    plt.clf()
    plt.title(title)
    plt.pie(hours_per_category, labels=labels, autopct = lambda pct: f"{round(pct * hours_in_total / 100)}")
    plt.savefig(f"{save_destination}/work_distribution_last_week.png")

