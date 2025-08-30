from app.config import config


class CashbackCalculator:
    def __init__(self):
        self.rates = config.get("rates", {"first": 0.05, "second": 0.07, "third": 0.10})
        self.cap = config.get("caps", {}).get("invoice_max", 1.50)

    def calculate(self, purchase_num: int, amount: float) -> float:
        capped_amount = min(amount, self.cap)
        if purchase_num == 1:
            rate = self.rates.get("first", 0.05)
        elif purchase_num == 2:
            rate = self.rates.get("second", 0.07)
        elif purchase_num == 3:
            rate = self.rates.get("third", 0.10)
        else:
            rate = 0.0
        return round(capped_amount * rate, 3)
