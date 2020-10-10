
class Address:
    def __init__(self, name, address1, address2, city, state, postal, country, phone):
        self.name = name
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.postal = postal
        self.country = country
        self.phone = phone

    def __str__(self):
        return "To:" + self.name