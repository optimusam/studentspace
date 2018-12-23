from models import *
from app import app
import json

def insertCollege():
    # db.drop_all(Review)
    db.create_all()
    # college = College(name="SRM Institute of Science and Technology", description="SRM Institute of Science and Technology, or Sri Ramaswamy Memorial Institute of Science and Technology, formerly known as SRM University, is a deemed university located in Kattankulathur, Tamil Nadu, India. It was founded in 1985 as SRM Engineering College in Kattankulathur, under University of Madras.", location="Kattankulathur, Tamil Nadu")
    # db.session.add(college)
    # db.session.commit()

def fillData():
    fileName = ["profIT.json", "profCSE.json"]
    for file in fileName:
        file = open(f"import/{file}", "r")
        teachers_json = json.loads(file.read())["teachers"]

        for teacher in teachers_json:
            teacher = Teacher(name=teacher["name"], department=teacher["department"], designation=teacher["designation"], college_id=1)
            db.session.add(teacher)
            db.session.commit()

def main():
    insertCollege()
    # fillData()
    print("DONE!")

if __name__ == "__main__":
    with app.app_context():
        main()
