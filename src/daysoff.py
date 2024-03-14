import calendar
from dateutil.relativedelta import relativedelta
import datetime
import unittest
import itertools


def daterange(date1, date2):
    """
    date 1 - the date we are stating looking for days off
    date 2 - the date we stop looking for days off
    returns the interval in wich we search for optimal days
    """
    for n in range(int((date2 - date1).days) + 1):
        yield date1 + datetime.timedelta(n)


def find_continuous_sets(_set, min_length=3):
    """
    finding continuous set of days
    allowing long weekends
    """
    # print("_set", _set)
    sets = []

    prev = None
    continuous_set = []
    for x in _set:
        #print("x:", x, "prev: ", prev)
        if prev == None:
            prev = x
            continuous_set.append(x)
            continue

        if x - prev == 1:
            continuous_set.append(x)
            prev = x
        else:
            if len(continuous_set) >= min_length:
                sets.append(continuous_set)
            continuous_set = [x]
            prev = x

    if continuous_set and len(continuous_set) >= min_length:
        sets.append(continuous_set)
    return sets


def test_find_continuous_sets():
    """
    trying to test, do better
    """
    test_cases = [
        ([1, 2, 3, 4, 5, 6, 7, 8, 14, 15], [[1, 2, 3, 4, 5, 6, 7, 8], [14, 15]]),
        (
            [1, 2, 7, 8, 10, 11, 12, 13, 14, 15],
            [[1, 2], [7, 8], [10, 11, 12, 13, 14, 15]],
        ),
        (
            [1, 2, 3, 4, 5, 6, 7, 8, 14, 15, 17, 19],
            [[1, 2, 3, 4, 5, 6, 7, 8], [14, 15]],
        ),
    ]

    for in_, result in test_cases:
        assert find_continuous_sets(in_, 2) == result


def calculate_sets_weight(_sets):
    """
    evelueting wich set is "better" than other 
    returns a number between 0 and 1 --> smaller the number, better the set 
    """

    #print("\n\n_sets:", _sets)
    power = len(_sets)
    #print("power:", power)
    weights = [1 / len(s) * power for s in _sets]
    #print("weights", weights)
    total_weight = sum(weights)
    #print("total_weight", total_weight)
    return total_weight


def test_calculate_sets_weight():
    """
    trying to test, do better
    """
    test_cases = [
        ([[1, 2, 3, 4, 5, 6, 7, 8], [14, 15]], 1.25),
        ([[1, 2], [7, 8], [10, 11, 12, 13, 14, 15]], 3.5),
    ]
    for in_, result in test_cases:
        assert round(calculate_sets_weight(in_), 2) == result


# 1 2 7 8 14 15 -- 6
# 1 2 3 4 5 6 7 8 14 15 -- 10
# |<-----8----->|  + 2          - 8 ** (1 / 2) + 2 ** (1/2) // didn't work out for maximizing
# |<-----8----->|  + 2          - 8 ** (2) + 2 ** 2
# 1 2 7 8 10 11 12 13 14 15 -- 10
# 2    2  |<      6      >|  - 6 * (1/3) + 2 ** (1/3) + 2 ** 1/3 // no-go
# 2    2  |<      6      >|  - 6 ** 3 + 2 ** 3 + 2 ** 3


def get_weekend_days(year):
    """
    figuring out wich days are weekends day
    this need to be written to have the possibility of any other days in a week off (for the whole year)
    """
    weekend_days = set()
    s = datetime.date(year, 1, 1)
    e = datetime.date(year, 1, 31)     # samo en mesec, ni celo leto 
    i = 1

    dates = daterange(s, e)
    for d in dates:
        if d.isoweekday() in {6, 7}:
            weekend_days.add(i)
        i += 1

    return weekend_days


def date_to_day_of_year(d: datetime.date) -> int:
    """
    convert date to number: 
    1st Jan --> 1
    1st Feb --> 32
    """
    return d.timetuple().tm_yday


def get_day_of_year_from_national_holidays(
    list_of_dates: list[datetime.date], move_holidays=True
) -> set:
   
    holidays_as_day_of_year = set()

    for d in list_of_dates:
        if not move_holidays:
            holidays_as_day_of_year.add(date_to_day_of_year(d))
        else:
            holidays_as_day_of_year.add(
                date_to_day_of_year(move_holiday(list_of_dates, d))
            )

    return holidays_as_day_of_year


def move_holiday(national_holidays, d):
    holidays = set(national_holidays)
    # print("holidays", holidays)
    # print(d, d.isoweekday())
    # print(d in holidays)

    if d.isoweekday() == 6:
        while d in holidays:
            d = d - datetime.timedelta(days=1)
    elif d.isoweekday() == 7:
        while d in holidays:
            d = d + datetime.timedelta(days=1)

    return d


def test_move_holiday():
    year = 2023
    national_holidays = [
        datetime.date(year, 1, 1),
        datetime.date(year, 1, 2),
        datetime.date(year, 1, 7),  # fake holiday to test saturday
        datetime.date(year, 2, 8),
        datetime.date(year, 12, 31),
    ]

    assert move_holiday(national_holidays, datetime.date(year, 1, 1)) == datetime.date(
        year, 1, 3
    )
    assert move_holiday(national_holidays, datetime.date(year, 1, 7)) == datetime.date(
        year, 1, 6
    )


def test_get_day_of_year_from_national_holidays():
    year = 2023
    national_holidays = [
        datetime.date(year, 1, 1),
        datetime.date(year, 1, 2),
        datetime.date(year, 2, 8),
    ]

    assert get_day_of_year_from_national_holidays(national_holidays, False) == {
        1,
        2,
        39,
    }

    assert get_day_of_year_from_national_holidays(national_holidays, True) == {
        3,
        2,
        39,
    }


def find_optimum(
    year: int,
    total_days_off: int,
    national_holidays: list[datetime.date],
):
    interval_days_off = total_days_off

    month_combs = []

    for i in range(1, 12):
        month_optimum = find_interval_optimum(
            interval_days_off,
            national_holidays,
            datetime.date(year, i, 1),
            datetime.date(year, i, 1)
            + relativedelta(months=2)
            - datetime.timedelta(days=1),
        )
        print("month optimum", month_optimum)
        month_combs.extend(month_optimum[0][0])
    # for comb in month_combs:
    #     #print("\n\n-----\n\n")
    #     for d in comb:
    #         #print(day_of_year_to_date(year, d))


def day_of_year_to_date(year, di: int) -> datetime.date:
    return datetime.date(year, 1, 1) + datetime.timedelta(days=di - 1)


def find_interval_optimum(
    interval_days_off: int,
    national_holidays: list[datetime.date],      # to je list, spremenit ga morem v set
    start_date: datetime.date,
    end_date: datetime.date,
):
    #print(start_date, end_date)
    weekends = get_weekend_days(year)
    national_holidays_int = get_day_of_year_from_national_holidays(
        national_holidays, move_holidays=True     # zakaj je tle move holidays true hard codirano
    )

    #print(national_holidays_int)



    constant_days_off = weekends.union(national_holidays_int)

    #print(weekends) 
    #print(constant_days_off)

    
    start_int = 1          #date_to_day_of_year(start_date)
    end_int = 10                 #date_to_day_of_year(end_date)


    interval_ints = set(range(start_int, end_int))

    #print("interval:", interval_ints)     

    #print("total days off", constant_days_off)     # tle gledamo samo wikende od januarja, cel interval pa je januar+februar ?
    

    all_possible_days_off = set(
        range(min(constant_days_off), max(constant_days_off))
    ).difference(constant_days_off)

    #print("all possible days off", all_possible_days_off)


    all_possible_days_off = set(
        x for x in all_possible_days_off if start_int <= x <= end_int)  

    print("all_possible_days_off - check", len(all_possible_days_off))
    #print("all_possible_days_off", all_possible_days_off, type(all_possible_days_off)) 

    all_possible_days_off = [
        set(c) for c in itertools.combinations(all_possible_days_off, interval_days_off)]   # to naredi kombinacije brez ponavljananja

    print("done getting all combinations", len(all_possible_days_off))
    #print(all_possible_days_off) # 
    all_possible_days_off_with_holidays = [
        sorted(c.union(constant_days_off)) for c in all_possible_days_off
    ]

    print("all_possible_days_off_with_holidays... done")
    print("all_possible_days_off_with_holidays", all_possible_days_off_with_holidays)
    #print("B",len(all_possible_days_off_with_holidays), type(all_possible_days_off_with_holidays))    # all possible days off in all possible days off with holidays vrne isto stevilo kombinaciji, neki ni kul 

    
####################################################AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    days_as_continuous_sets = [
        find_continuous_sets(_set) for _set in all_possible_days_off_with_holidays
    ]
    
    #print("combs_as_nested_sets")
    #print("combs_as_nested_sets", days_as_continuous_sets)    
    
    days_as_continuous_sets_weighted = [
        (comb, calculate_sets_weight(comb)) for comb in days_as_continuous_sets
    ]
    

    print("days_as_continuous_sets_weighted")
    print("days_as_continuous_sets_weighted", days_as_continuous_sets_weighted)    

# hocemo spravit v obliko (kombinacija dni, utez) da lahko klicemo min funkcijo na konstrukt

   # days_as_continuous_sets_weighted = [
    #    (comb, weight)
    #    for comb, weight in days_as_continuous_sets_weighted
    #    if weight > 0.0        # to je vedno res pokonstrukciji
    #]

    


    ordered = sorted(days_as_continuous_sets_weighted, key=lambda x: x[1])
    #for comb, weight in ordered[:3]:
        #print("\n\n-----------------------------\n\n")
        #print(comb)
    #     for date_set in comb:
    #         print("----")
    #         for d in date_set:
    #             print(datetime.date(year, 1, 1) + datetime.timedelta(days=d - 1))
    # print("alshd", ordered[:3])            
    # return ordered[:3]
    #raise Exception("bez")

if __name__ == "__main__":
    year = 2023

    total_days_off = 4  # tle definiramo koliko prostih dni imamo

    national_holidays = [
        datetime.date(year, 1, 1),
        datetime.date(year, 1, 2),
        datetime.date(year, 2, 8),
        datetime.date(year, 4, 10),
        datetime.date(year, 4, 27),
        datetime.date(year, 5, 1),
        datetime.date(year, 5, 2),
        datetime.date(year, 8, 15),
        datetime.date(year, 10, 31),
        datetime.date(year, 11, 1),
        datetime.date(year, 12, 25),
        datetime.date(year, 12, 26),
        datetime.date(year, 12, 31),
    ]

          
    fu = find_optimum(
        year,
        total_days_off,
        national_holidays,
    )
    print("find optimum", fu)