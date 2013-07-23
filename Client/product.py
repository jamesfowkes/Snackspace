class Product:

    def __init__(self, barcode, description, priceinpence):
        self.valid = False
        self.description = ''
        self.price_in_pence = 0
        self.count = 0

        self.barcode = barcode
        self.description = description
        self.price_in_pence = int(priceinpence)
        self.count = 1
        self.valid = True

    def increment(self):
        if (self.valid):
            self.count += 1

    def decrement(self):
        if (self.valid):
            if self.count > 0:
                self.count -= 1

        return self.count

    @property
    def total_price(self):
        return self.count * self.price_in_pence

