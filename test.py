import json
from pprint import pprint

class Obj:
        def __init__(self, first_name, last_name, middle_name):
            self.first_name = first_name
            self.last_name = last_name
            self.middle_name = middle_name

        def main(self):
            print(f"BEFORE: {self.last_name}, {self.first_name} {self.middle_name}")
            self.callback(
                new_first_name = "Mark Anthony",
                new_last_name  = "Vale"
                # new_middle_name key => not using here
            )

        def callback(self, **kwargs):
            self.first_name         = kwargs.get('new_first_name')
            self.last_name          = kwargs.get('new_last_name')

            # Set a default value if new_middle_name key is missing in parameters when self.callback is being call
            self.middle_name        = kwargs.get('new_middle_name', "Not Foo")

            print(f"AFTER: {self.last_name}, {self.first_name} {self.middle_name}")
    



if __name__ == "__main__":
    obj = Obj(first_name="John", last_name="Doe", middle_name="Foo")
    print(obj.main())

    with open('test-data/mmi-data.json') as f:
        mmi_data = json.loads(f.read())
    pprint(mmi_data[0]['_id'])
