import datetime


def folder_structure_from_date(date):
    date = None
    if date is None:
        date = datetime.datetime.utcnow()
    try:
        date_folder = date.strftime("d=%Y-%m-%d/h=%H")
        return date_folder
    except Exception as error:
        raise error


def main():
    stime = datetime.datetime.utcnow()
    print(folder_structure_from_date(stime))
    pass


main()
