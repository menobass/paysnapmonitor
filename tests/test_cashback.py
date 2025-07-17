from app.cashback import CashbackCalculator

def test_cashback_rates():
    calc = CashbackCalculator()
    assert calc.calculate(1, 1.00) == round(1.00 * 0.05, 3)
    assert calc.calculate(2, 1.00) == round(1.00 * 0.07, 3)
    assert calc.calculate(3, 1.00) == round(1.00 * 0.10, 3)
    assert calc.calculate(1, 2.00) == round(1.50 * 0.05, 3)
