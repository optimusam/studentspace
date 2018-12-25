from models import *
from app import app
import json
import os
import csv


def insertCollege():
    db.drop_all()
    db.create_all()
    college = College(name="SRM Institute of Science and Technology", description="SRM Institute of Science and Technology, or Sri Ramaswamy Memorial Institute of Science and Technology, formerly known as SRM University, is a deemed university located in Kattankulathur, Tamil Nadu, India. It was founded in 1985 as SRM Engineering College in Kattankulathur, under University of Madras.", location="Kattankulathur, Tamil Nadu")
    db.session.add(college)
    db.session.commit()

def fillData():
    filenames = os.listdir('./import')
    for filename in filenames:
        with open(f"./import/{filename}") as csvFile:
            reader = csv.reader(csvFile, delimiter=',')
            for row in reader:
                try:
                    t= Teacher(name=row[0], designation=row[1],department=row[2], college_id=1)
                    db.session.add(t)
                except Exception as e:
                    print("Error-->",e, t.name, t.designation, t.department)
            db.session.commit()
            print("Done {filename}")
def main():
    insertCollege()
    fillData()
    print("DONE!")

if __name__ == "__main__":
    with app.app_context():
        main()
