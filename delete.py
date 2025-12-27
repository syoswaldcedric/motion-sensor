person = {
    "name": "John",
    "age": 30,
    "city": "New York",
    "country": "USA",
    "gender": "Male",
    "birthday": "1990-01-01",
}

key, val = zip(*person.items())
print(key)
print(val)

print(list(range(10)))
print(range(10))
