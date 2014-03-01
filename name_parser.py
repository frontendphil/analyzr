import random

if __name__ == "__main__":
    names = []

    with open("dirty_list_of_names", "r") as dirty_list:
        for name in dirty_list:
            if name in names:
                continue

            names.append(name)

        random.shuffle(names)

        with open("list_of_names", "wb") as parsed_list:
            for name in names:
                name = name.replace("\xc2\xa0", "").strip()
                parsed_list.write("%s\n" % name)
