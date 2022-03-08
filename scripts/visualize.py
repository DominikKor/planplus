from main import get_full_schedule

data = get_full_schedule()

print(data)
for ik, iv in data.items():
    print(f"Klasse {ik}:\n")
    for j in iv:
        print(j)
    print("\n--------------------------------------\n")

"""
{
    "9B": ["1. Ma", "2. De"],
    "8B": ["1. Sp", "2. Sp"],
}
"""
