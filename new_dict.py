from work_with_db import db


class TwoWayDict(dict):
    def key_by_value(self, value):
        for key, val in self.items():
            if val == value:
                return key
        raise Exception

    def get_values(self, values: list) -> list:
        return [key for key, val in self.items() if val in values]

    def flip(self):
        return TwoWayDict({self[key]: key for key in self})


def _decode() -> dict[str, TwoWayDict]:
    """
    Создание словаря {"название_таблицы": {поле name: id, ...}}
    из 4-х таблиц
    """
    result = {}
    table_names = [
        "Decode_Department",
        "Decode_Program_Source",
        "Decode_Subject",
        "Decode_Training_Format",
        "Decode_Access_Level"
    ]
    for table in table_names:
        records = db.select(f'select * from "{table}" order by id')
        result[table[7:]] = TwoWayDict({elem[1]: elem[0] for elem in records})
        
    return result


decodes = _decode()

if __name__ == "__main__":
    print(decodes)
    # print(decodes["Subject"].key_by_value(15))
    # print(decodes['Department'].flip())

    print(decodes["Department"].key_by_value(1))
