"""01: fetch live/public data (Stooq daily + Frankfurter spot check)."""
from src.data_loader import save_all
if __name__ == "__main__":
    man = save_all()
    print(f"wrote {man}")
    print(open(man).read())
